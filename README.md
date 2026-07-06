<img width="1034" height="836" alt="Screenshot from 2026-05-28 17-17-05" src="https://github.com/user-attachments/assets/648564df-3d0a-4d95-833d-c3adaf57b899" />
# PS5 UART Dijagnostika v2.0
**Servis Port Sabac** — Alat za citanje i brisanje gresaka sa PS5 konzole putem UART/RS232 interfejsa.

---

## Sadrzaj paketa

| Fajl | Opis |
|------|------|
| `ps5_uart_reader.py` | Linux verzija (GTK3) |
| `ps5_uart_windows.py` | Windows verzija (tkinter) |
| `install_linux.sh` | Linux automatska instalacija |
| `install_windows.bat` | Windows automatska instalacija |
| `requirements.txt` | Python zavisnosti |
| `SERVISPORT_RP2040_BRIDGE.uf2` | RP2040 Zero Firmware, zahteva MicroPython |

---

## Brza instalacija

### Linux
```bash
chmod +x install_linux.sh
./install_linux.sh
```

### Windows
Desni klik na `install_windows.bat` → **Pokreni kao administrator**

---

## Sistemski zahtevi

### Linux
- Python 3.8+
- GTK3 (`python3-gi`, `gir1.2-gtk-3.0`)
- `pyserial`, `requests`

### Windows
- Python 3.11+ (instalira se automatski ako nije prisutan)
- `pyserial` (instalira se automatski)
- CH340 / CP210x / FT232 drajver (dugme Instaliraj u aplikaciji)

---

## Pokretanje bez instalacije

**Linux:**
```bash
pip install pyserial requests --break-system-packages
sudo usermod -aG dialout $USER
# Odjaviti se i ponovo prijaviti
python3 ps5_uart_reader.py
```

**Windows:**
```bat
pip install pyserial
python ps5_uart_windows.py
```

---

## Spajanje PS5 na adapter

| PS5 pad | Adapter |
|---------|---------|
| TX | → RX adaptera |
| RX | ← TX adaptera |
| GND | — GND |

- Logika: **3.3V TTL** (ne 5V!)
- Baud rate: **115200 / 8N1**
- PS5 prikljuciti samo na struju — ne pritiskati power dugme

---

## Baza kodova
Automatski se preuzima pri svakom pokretanju sa:
`https://servisport.rs/servisni/download/ps5.xml`

Lokalna kopija: `~/.ps5uart/codes.json`
Ako nema interneta — koristi se poslednja sacuvana verzija.
Rucno osvezavanje: dugme **Azuriraj bazu** u aplikaciji.

---

## Lokacije fajlova

| Fajl | Lokacija |
|------|----------|
| Baza kodova | `~/.ps5uart/codes.json` |
| Log istorija | `~/.ps5uart/history.log` |
| Windows instalacija | `%LOCALAPPDATA%\PS5UART\` |

---

*Servis Port Sabac · servisport.rs*
