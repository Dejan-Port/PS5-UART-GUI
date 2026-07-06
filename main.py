"""
PS5 UART Bridge — RP2040 Zero
Servis Port Sabac

Povezivanje:
  GPIO0 (TX) → PS5 RX pad
  GPIO1 (RX) ← PS5 TX pad
  GND        → PS5 GND
  USB        → PC (pojavljuje se kao COM port)

RGB LED (GPIO16 WS2812):
  Crvena  = ceka PS5 / EMC nije aktivan
  Zelena  = EMC aktivan, spreman za komande
  Plava   = prima/salje podatke
  Zuta    = greska checksuma
"""

import machine
import sys
import time
import neopixel
import select

# ── Konfiguracija ─────────────────────────────────────────────────────────────
PS5_TX_PIN  = 8        # GPIO8 → PS5 RX
PS5_RX_PIN  = 9        # GPIO9 ← PS5 TX
PS5_BAUD    = 115200
LED_PIN     = 16       # WS2812 na RP2040 Zero
LED_BRIGHT  = 0.08     # 0.0–1.0

# ── RGB LED ───────────────────────────────────────────────────────────────────
_led = neopixel.NeoPixel(machine.Pin(LED_PIN), 1)
# Odmah crvena — pre bilo kakvog init-a
_led[0] = (int(255 * LED_BRIGHT), 0, 0)
_led.write()

def _b(r, g, b):
    return (int(r * LED_BRIGHT), int(g * LED_BRIGHT), int(b * LED_BRIGHT))

def led_red():    _led[0] = _b(0, 255, 0);   _led.write()
def led_green():  _led[0] = _b(255, 0, 0);   _led.write()
def led_blue():   _led[0] = _b(0, 0, 255);   _led.write()
def led_yellow(): _led[0] = _b(255, 200, 0); _led.write()
def led_off():    _led[0] = (0, 0, 0);        _led.write()

# ── PS5 UART ──────────────────────────────────────────────────────────────────
_rx_pin = machine.Pin(PS5_RX_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
ps5 = machine.UART(
    1,
    baudrate=PS5_BAUD,
    tx=machine.Pin(PS5_TX_PIN),
    rx=_rx_pin,
    timeout=50,
    rxbuf=512
)

# ── Checksum ──────────────────────────────────────────────────────────────────
def csum(s):
    return sum(ord(c) for c in s) % 256

def validate_strip(line):
    """
    Skida :XX checksum sa kraja linije i validira.
    Vraca (content, valid) — content bez checksuma.
    Ako nema checksuma, vraca (line, True).
    """
    if not line:
        return line, False
    idx = line.rfind(':')
    if idx < 0 or idx + 3 != len(line):
        return line, True   # nema checksuma — proslediti kao sto je
    try:
        cs_recv = int(line[idx+1:], 16)
        content = line[:idx]
        return content, cs_recv == csum(content)
    except Exception:
        return line[:idx] if idx > 0 else line, False

def add_csum(cmd):
    """Dodaje :XX checksum na komandu."""
    cmd = cmd.strip()
    return "{:s}:{:02X}".format(cmd, csum(cmd))

# ── Stanje ────────────────────────────────────────────────────────────────────
emc_ready      = False
pc_ready       = False
ps5_rx_buf     = b""
pc_rx_buf      = b""
probe_sent     = False   # ignorisi RX dok ne posaljemo bar jedan probe
emc_confirm    = 0       # koliko uzastopnih validnih OK linija — treba 2

def set_emc(ready):
    global emc_ready
    emc_ready = ready
    if ready:
        led_green()
    else:
        led_red()

# ── Slanje ka PS5 ─────────────────────────────────────────────────────────────
def send_ps5(cmd):
    """Dodaje checksum i salje komandu PS5."""
    wire = add_csum(cmd) + "\n"
    ps5.write(wire.encode("ascii"))

# ── Slanje ka PC ──────────────────────────────────────────────────────────────
def send_pc(line):
    """Salje liniju PC-u preko USB CDC."""
    sys.stdout.write(line + "\r\n")

# ── Procesiranje linije od PS5 ────────────────────────────────────────────────
def process_ps5_line(raw):
    global emc_ready, probe_sent, emc_confirm
    raw = raw.strip("\r\n ")
    if not raw:
        return
    if not pc_ready:
        return
    if not probe_sent:
        send_pc(raw)
        return

    content, valid = validate_strip(raw)

    if not valid:
        emc_confirm = 0
        led_yellow()
        time.sleep_ms(100)
        if emc_ready:
            led_green()
        else:
            led_red()
        send_pc(content)
        return

    led_blue()

    # Detektuj CMD READY — PS5 je bootovala u EMC mod
    cu = content.upper()
    if "UART CMD READY" in cu or "CMD READY" in cu or "[MANU]" in cu:
        if not emc_ready:
            time.sleep_ms(50)
            send_ps5("\x05")   # Ctrl+E
            set_emc(True)

    # OK odgovor — potrebna 2 validna OK (iz bilo kojih proba) da bi se proglasio EMC
    if not emc_ready and content.startswith("OK ") and len(content) >= 19:
        parts = content.split()
        if len(parts) >= 3:
            try:
                int(parts[1], 16)
                int(parts[2].split(':')[0], 16)
                emc_confirm += 1
                if emc_confirm >= 2:
                    set_emc(True)
            except ValueError:
                emc_confirm = 0

    send_pc(content)

    time.sleep_ms(10)
    if emc_ready:
        led_green()
    else:
        led_red()

# ── Procesiranje linije od PC-a ───────────────────────────────────────────────
def process_pc_line(line):
    global pc_ready, probe_sent, emc_ready, emc_confirm
    line = line.strip()
    if not line:
        return
    if line == "BRIDGE:PING":
        pc_ready = True
        probe_sent = True
        send_pc("BRIDGE:READY")
        if emc_ready:
            send_pc("BRIDGE:EMC=1")
        return
    if line == "BRIDGE:DISCONNECT":
        pc_ready = False
        emc_ready = False
        emc_confirm = 0
        probe_sent = False
        led_red()
        return
    if line == "BRIDGE:STATUS":
        send_pc("BRIDGE:EMC={}".format("1" if emc_ready else "0"))
        return
    # PC salje komandu PS5 — od sad slusamo odgovore za EMC detekciju
    probe_sent = True
    send_ps5(line)

# ── Wake-up proba ─────────────────────────────────────────────────────────────
_last_probe = 0
_probe_interval = 2000   # ms
_last_announce = 0
_announce_interval = 5000  # ms — ponavlja BRIDGE:READY dok PC ne potvrdi

def maybe_probe(now):
    global _last_probe, probe_sent
    if emc_ready or not pc_ready:
        return
    if now - _last_probe >= _probe_interval:
        _last_probe = now
        ps5.write(b"\x05")
        send_ps5("errlog 0")
        probe_sent = True

# ── Glavni loop ───────────────────────────────────────────────────────────────
led_red()
time.sleep_ms(300)
ps5.read()   # flush svog suma koji je uleteo pre pull-up-a
send_pc("BRIDGE:READY")

while True:
    now = time.ticks_ms()

    # -- Cita sa PS5 UART --
    if ps5.any():
        chunk = ps5.read(256)
        if chunk:
            try:
                ps5_rx_buf += chunk
            except Exception:
                ps5_rx_buf = chunk
        while b"\n" in ps5_rx_buf:
            idx = ps5_rx_buf.index(b"\n")
            raw = ps5_rx_buf[:idx].decode("utf-8")
            ps5_rx_buf = ps5_rx_buf[idx+1:]
            process_ps5_line(raw)

    # -- Cita sa PC (USB CDC) — non-blocking --
    r, _, _ = select.select([sys.stdin], [], [], 0)
    if r:
        try:
            c = sys.stdin.read(1)
            if c == '\x03':
                raise KeyboardInterrupt
            if c:
                pc_rx_buf += c.encode("utf-8")
        except KeyboardInterrupt:
            raise
        except Exception:
            pass
    while b"\n" in pc_rx_buf:
        idx = pc_rx_buf.index(b"\n")
        line = pc_rx_buf[:idx].decode("utf-8").strip("\r")
        pc_rx_buf = pc_rx_buf[idx+1:]
        process_pc_line(line)

    # -- Wake-up probe --
    maybe_probe(now)

    # -- Periodican BRIDGE:READY dok PC ne potvrdi --
    if not pc_ready and time.ticks_diff(now, _last_announce) >= _announce_interval:
        _last_announce = now
        send_pc("BRIDGE:READY")

    time.sleep_ms(1)
