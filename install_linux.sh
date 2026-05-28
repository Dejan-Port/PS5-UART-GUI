#!/bin/bash
# ============================================================
#  PS5 UART Dijagnostika – Linux installer
#  Servis Port Sabac
# ============================================================

set -e

APP_NAME="PS5 UART Dijagnostika"
APP_DIR="$HOME/.local/share/ps5uart"
DESKTOP_DIR="$HOME/.local/share/applications"
BIN_DIR="$HOME/.local/bin"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "============================================"
echo "  $APP_NAME – Instalacija"
echo "  Servis Port Sabac"
echo "============================================"
echo ""

# ── Provera Python verzije ───────────────────────────────────
echo -e "${YELLOW}[1/5] Provera Python verzije...${NC}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}GRESKA: Python3 nije instaliran.${NC}"
    echo "Pokrenite: sudo apt install python3 python3-pip"
    exit 1
fi
PY_VER=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$PY_VER" -lt 8 ]; then
    echo -e "${RED}GRESKA: Potreban Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}OK – Python $(python3 --version)${NC}"

# ── Instalacija GTK3 binding-a ───────────────────────────────
echo -e "${YELLOW}[2/5] Provjera GTK3 zavisnosti...${NC}"
if ! python3 -c "import gi; gi.require_version('Gtk','3.0'); from gi.repository import Gtk" &>/dev/null; then
    echo "Instaliram GTK3 Python binding..."
    sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
        gir1.2-pango-1.0 gir1.2-gdkpixbuf-2.0 2>/dev/null || \
    sudo dnf install -y python3-gobject gtk3 2>/dev/null || \
    sudo pacman -S --noconfirm python-gobject gtk3 2>/dev/null || \
    { echo -e "${RED}GRESKA: Nije moguce automatski instalirati GTK3.${NC}"; exit 1; }
fi
echo -e "${GREEN}OK – GTK3${NC}"

# ── Instalacija Python paketa ────────────────────────────────
echo -e "${YELLOW}[3/5] Instalacija Python paketa...${NC}"
pip3 install pyserial requests --break-system-packages --quiet 2>/dev/null || \
pip3 install pyserial requests --quiet 2>/dev/null || \
pip3 install --user pyserial requests --quiet
echo -e "${GREEN}OK – pyserial, requests${NC}"

# ── Kopiranje aplikacije ─────────────────────────────────────
echo -e "${YELLOW}[4/5] Kopiranje aplikacije u $APP_DIR ...${NC}"
mkdir -p "$APP_DIR"
cp "$(dirname "$0")/ps5_uart_reader.py" "$APP_DIR/"

# Wrapper skripta
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/ps5uart" << 'WRAPPER'
#!/bin/bash
exec python3 "$HOME/.local/share/ps5uart/ps5_uart_reader.py" "$@"
WRAPPER
chmod +x "$BIN_DIR/ps5uart"
echo -e "${GREEN}OK${NC}"

# ── Desktop prečica ──────────────────────────────────────────
echo -e "${YELLOW}[5/5] Pravljenje desktop precice...${NC}"
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_DIR/ps5uart.desktop" << DESKTOP
[Desktop Entry]
Version=2.0
Type=Application
Name=PS5 UART Dijagnostika
Comment=PS5 greske citac – Servis Port Sabac
Exec=python3 $APP_DIR/ps5_uart_reader.py
Icon=utilities-terminal
Terminal=false
Categories=Utility;Electronics;
Keywords=PS5;UART;dijagnostika;servis;
DESKTOP
chmod +x "$DESKTOP_DIR/ps5uart.desktop"
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
echo -e "${GREEN}OK${NC}"

# ── Serijski port dozvola ────────────────────────────────────
echo ""
if ! groups | grep -q dialout; then
    echo -e "${YELLOW}VAZNO: Dodajem korisnika u 'dialout' grupu za pristup serijskom portu...${NC}"
    sudo usermod -aG dialout "$USER"
    echo -e "${GREEN}OK – Odjavite se i ponovo prijavite da bi izmena stupila na snagu!${NC}"
else
    echo -e "${GREEN}Korisnik vec ima pristup serijskom portu.${NC}"
fi

echo ""
echo "============================================"
echo -e "${GREEN}  Instalacija zavrsena!${NC}"
echo "============================================"
echo ""
echo "Pokretanje:"
echo "  ps5uart          (iz terminala, ako je ~/.local/bin u PATH)"
echo "  ili trazite 'PS5 UART' u meniju aplikacija"
echo ""
