#!/usr/bin/env python3
"""
PS5 UART Dijagnostika v2.0
Servis Port Sabac
GTK3 Linux Desktop Aplikacija

Protokol:
  - Baud: 115200, 8N1
  - PS5 salje "OK 00000000:3A $$ [MANU] UART CMD READY:36" pri ukljucivanju
  - Ctrl+E (\x05) ulazi u EMC CMD mode
  - errlog N     cita N-ti zapis (FFFFFFFF = kraj)
  - errlog clear brise sve zapise sa konzole
  - Format: OK 00000000 <ERROR_CODE> <TIMESTAMP> <FLAGS> ... :checksum
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk, Pango, GdkPixbuf
import base64
import tempfile
import webbrowser

LOGO_32_B64 = "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"
LOGO_48_B64 = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAANjUlEQVR4nM2ae5BU1Z3HP+ece/s53fNgBhRwHARB42uCgiYlDw3iSpCNMWiptVkfWasWk2Wza5WmfFfWdTVqki0f0VVqrdRuZCXxDYJVq65SKoKCohIBEQRhYN79mL597zm//aNnGgZNdnrY1O636lT1dJ977+/7e5/fHSUiwgghItSwfVTQWte0X9VC4P8jvJFsEhGUUnR1drJ163acCOIcTgCxiBVEHBhNzPMRcRjj4Xk+xmiM54FSIBa0Qik1qGmFE4ezDmsd8ZjPtGnTMMb87xKokIC1b7xBqRhiUZTLJawVTDqBOIMvChdZpFQAF0Kk8DwPpRRoQ9k6lF8gnk5ikknQhshCLggwDjwxFAfKFAoDzJhxOs65EbnTiAgopQijiFxvnnFjx5IPStRlUgxEQvH9TRR37EB7kJo8lYap03BBAW0BZXDWoZQiphWJdJKtfXvZunMLOMOJrZNobW6jVI6IOYfRJbq7+kaq05ETAEDAhSVCG6K0oqu7h70P/4rNH25ij69wKqKlWGbmvPlMveb72FxA5MqIcigMKvJ58NVV/Oc7bxHr6UGcJojDhd+az/fPuZQgDAmDAeJ+Y00ERh7yIijP4cRS8n3yT/+WDze/w66zT2ej7yOntBMtnMdrL6ykc/2b6PoYZRVgY0IslWDl9nWsemMN5+omxnRZzmicyCXHTed3Ty9n7ebXac5kAUHr2nLKiAkIoIzGeFAul2HbNnKT2mgd10zf/i7ee3MDJ01qpbO5gd5PdkAygVN6cFk2fLGViTpD27Hj+OxAJ2s3bWba8W1MSDbz/mcfobXCOYfS6k9DQAFagRVLLO5jTphC4pNtlCzMmTuLOfNmsWNPB6qzl8bTT6VcjhAPAsqESpjafBS7S13YUsS3zpzBN089iY4DB9jT18nJbSdTthEowYvFaiIw8hgA8BRWefhBSOqixbR37Oe9Z1+ksXUioXPs+/wLvn3lFaRPayff248VhaAZsBHzT/omn+z/nGXr13FCqhGjFP/yX6u58M8Wce5Jc8gV8ijPEYv/CQmI0oinsaWAZCLOxKVLadn6e/Zu+RiVTDD+5JPxW4+htyuHh2AVOCtEYYDneSyZdxUfT93Olq2/J6YV3/vaqZx63Mn0D+TQWDR+TTWgNgIKRIFzDqcgCiOUDcl8fTpNZ34DpTQSBURBiN+UBO1AVVKwQqEcWBfn3PpjWHDKOXi+oljI0d3bRSzm4fkaFWqE2mKgJgtopZEIsJCMJ7ESY/O779Kxbx9hENHT20VkLZEVyuUSURhijCEKLTaypOuy+Mon5hm0hnNmzWZK23H05vsRpUALStXWC9VEwGgfazXaj9GTy3PXHbfR19PFxInHgIK6dJqWlha0c8T9OCaRQilFMpnEOSEolygUChzozWGtcNudt3PbDTcyedoJ5II8oqXSctSAkdNVgI4RhZZMXT2PPPAox09uZdXq1YyfMIF0ug4/liBfLNLXn6dQLFEsBZRDS38uT3GgRCyWxFpFT3cvF393ETPPOouXX15DfV0GcWDFVCxRA2qqxJ6OoVWcKLRMPWEab7zyIr9d8RSpdJooqqTXRCKBUgYlFW0W8nmCckB/Ls+2rVvJF/Kk0ynuvOsefKP5h1tvoa+QR+vB+HI1yV+bCykqQVnM9bH44u9Ql07w5PIVaKXwfY9yuYzve8TiscGzg2NgoAQojPZoamxkwtHjaWio49hjWpkz52wmtrbSm8uhfYPRttI11krAuUrDpf6I+ZwIURgSTySQSFEeKLDw2ws577wF9HZ3oZUhX8gTBAHaOkQZEDAokqk0Ou6R9TTJuCae8TC+R99AQFexgB/z8YwHyhHZ/5nAUHtfJTDUtlpr0Vp/JRGjNVoLxXyOKHIIlv78fpQYlNJooC7VQCZuSRhFdz5PIZdDKYWUA4znURzooRRAUIhQno/245i4ojwQENMJBgYsce8PO4WI4JwbViuUiMjWbdsY09REU1PTHyWSy/XT1dWNOBAEEYXnmcFcD9Y6wrBMNpPh7p/9jF/88n6UUvzouuu4/vobKORzeL5XOcQ4h1Ia6yzOWYIgIpFIMPX4yXieP9z6ziEiVcEHBgaIx+MVxZdKJZl77nxpO7ZNHn74Ienp7pYhWGtltLjl1luFSg8od/7jT0d9nyg6KENHR4fcfvsdMn36GbJly8finBOeWvE7SSXrRPm+ANJ23GS56+5/knw+/6UbOOeGLWutRFE0bJVKJYmiSG666SYxxogxRu64/bZhvx26rLWHLPeVwu/cuUuWLl0q48YdVVXKfffdKyIizJ57jgCSGdsi8WRG8JICyOkzZ8iOHdtFZHSWuOnmm6sPu+Xmm2u+fuiZ//6b/5AxYw4K3pRtFK2MTJx4rHR07BPvp3fcwb33Znn++WcBTTLbhE8jG9ZtZOHCi3nmmaeYMmUKYRhWz7gymAU+37WbjevXk85kKAcBIg4rlY7ShZY5s+cAlcBbtfIlSmGJRCKO53lo3yNTl+GM9unDzr7OOaIoIhaL8dBDv+KH1y3FmBjjxhxNKcjR3d+D53nMnTsbrfTBscqTy5fzkxtv4bPPdgAavDhEwsRjxvLh5g1ksw3VAAcwxrDj0528/NwzNGbqUTFFORAwYD0h7qVIJBMorcgXS5SDMs6AVYIon958P+Maslx+0cUYz6vOnIYC9b77f8n1f/9jGtMtlKISzpYJohLnzD2Xu++5ixkzZlaykLWVxKu1pqenl2XLnmD1mpfp7umls6OLYpBnyuRJXHrJ97j66qvIZDIARFGE53n09vWxYd2bdHbuJR5LEVqHNQZnQ8qBqzSAikqe1x6hCFG5zImTJzG9vb3a/w8JvnPXLh577HEeefRxDnQcoClbj/I1J06bwpVXX8WVf3klxjMHM+WQBay1w/KriLB37xdobdi0aTP33n8/e3bv4qKLvsN1S/6a8eMnVPcppfjggw/Y8PbrJJtayJcDfA2R1SARHgZPGXryJRqzKRYtuIC6QUUM4b2NG3nwgQdZ+9abnHXmmfzVNdeQyxdoa2ulLl3HhAkThrnZkNtVq4YxploolNZopapCHnXUUZx//jzefnsd//zAA8w773zmzJ7FkiVLOOWUUwDo7j6AScYQDXWZOpQLceKhRPCVxqCIp+soFoskU8mqMCtXrWLZssf4bMdO5s8/n9UrV9La2spXYUjrh8bMHxwtHvr10OehC7dv/5RHHnmU1WvWcNqpp7F48cV05veRrsvy/if72PTBRyTrkyjnV4LeWbTStPjQ3n46R49rpnP/XpYtWwYIl11+GVdcfgXpdLoq6KHJ4tBnH46aZqOHV8Te3l5+/osH+GjLe1y25Af07+vgntd2s29PJ0o7XDHEIlgcyViMnh2f8vO/u5Kgu5Pnn13OT268gQsWLPiShv9YT3Y4ajuRDWpBRIiiiIaGBn5wzV/w6juT6O0poRXUa8eu3v0k02mcK+MJKOuwWpON+2gbMLmtlR/+6MdcsGDBoNtatDY1n4dhlNPpIdPm+vtZ/uwKdDZDUFIoFVHqL9CxuxMSHtoKxqvEgXWOjFFMmdRG5Cz79vfQ3v415sw+e8Rz0K9CbWOVwwjs2PkpkVIkTBJtS5RFSMTrmTqlBfHBc6C0QYlC4TAKikEepYSW5gY+2bKNb5w1g1gsPirhR01gCNaGaONDaIgRJ1WXRgJFVAwIyhGiDELlrKENJDxIJZNorRHlyOf7B6vu/xGBeCJFVAiIyQADuQK7Pt6JWMe4MS00NTdXq2tQDvA9Q18hIN/fhdaadF2KWMzDP6x1rhk1d1mHwDknfX19UiwU5KWX1hzsFO+9R4rFgvT09EhfX690dh6Qnp5u+c2Ty6t7Hn/8MSkUCkfUsouIHJEFlFJks9nBvzRKaxRQ39BAMpkikUgOS4nJZLqa3xsaGkmlUtgoglEGMByhC8HB5i4IBhDnECAMQ6IoQkTwPK9amIqFgeqZPQzLlWtrHKMcjtFTPwTGmEMsAfXZ+sHWe6goKYwxxONJKh4EmbrMqPL+4TgiApU5jmPt2rU899xzg2NBxeo1a3jhhecJwwBrLSKO119/g1deebnqUm+99TabNm2qVvdR44giaBALL1wkgHjGE115xSItzc3D9syaNUcAMYfs+Xp7e/V359zhtx0RjqiQffHFXtavf4f9+zvQWuOkok2tNcponn766er5IZ/PVfL/4B6lFH39faxevZrp06fTMph2a+mDRm2BKIpEROTXv/63aloczVJKCSBPPPGvIiIShmHNsowuBuSgJQB8/8vF6HBNfuWwbDCIVY3vBIbLMgoMjVQOHOiURYv+vOrbSmlRSosxngBy6SWXyIoVK2TGjJmDe4yAqu5RSsu1114re3bvEWvtqOJg1FlIKUU8kSSf7yaTTdDUlKKhMUvTmHrGjq0nmTIkk4oLLliI8ctkszHqGxM0NKbJZBPUZWOIOMY01TF+wvjR+T+jbKeH2t93393ImjVrWLz4u4RhiNYVlxAcWhteenEVx0+dRk9fN2edOZNSKaheH0YRYTngtVdf42+W/i2xGt9ODmFUWWhIUxMmjKevv5cnn1w+7LSmVSUjaaVoa2tl3VPrKOSLeL4HCIrKP3uEYUQsHsdoPWoL/DeqmPBVkFXrvgAAAABJRU5ErkJggg=="

def _logo_pixbuf(b64_str, size):
    """Kreira GdkPixbuf iz base64 PNG stringa."""
    try:
        data = base64.b64decode(b64_str)
        tmp = tempfile.mktemp(suffix=".png")
        with open(tmp, "wb") as f:
            f.write(data)
        pb = GdkPixbuf.Pixbuf.new_from_file_at_size(tmp, size, size)
        return pb
    except Exception:
        return None

import threading
import serial
import serial.tools.list_ports
import json
import os
import sys
import re
import time
import requests
from datetime import datetime

# ─── Prevodi ─────────────────────────────────────────────────────────────────
TRANSLATIONS = {'sr': {'app_title': 'PS5 UART Dijagnostika  v2.0', 'app_subtitle': 'Servis Port Sabac  •  RS232/USB  –  citanje i brisanje gresaka', 'btn_help': '? Uputstvo', 'lang_toggle': 'EN', 'panel_port': 'SERIJSKI PORT', 'baud_label': 'Baud:', 'btn_connect': 'Povezi', 'btn_disconnect': 'Prekini vezu', 'btn_refresh': 'Osvezi', 'btn_pinout': 'Pinout', 'conn_off': 'Nije povezano', 'emc_wait': 'EMC: ceka PS5...', 'emc_ready': 'EMC: spreman za komande', 'panel_commands': 'PS5 KOMANDE', 'btn_read': 'Citaj sve greske sa PS5', 'btn_clear_ps5': 'Obrisi greske sa PS5', 'custom_cmd_label': 'Prilagodjena komanda:', 'btn_send': 'Posalji', 'panel_search': 'RUCNA PRETRAGA', 'btn_search': 'Pretrazi bazu', 'search_hint': 'npr. 80C00140', 'panel_db': 'BAZA KODOVA', 'btn_update_db': 'Azuriraj bazu', 'db_loading': 'Ucitavanje...', 'db_online': 'Online ({n} kodova)', 'db_offline': 'Offline ({n} kodova)', 'db_local': 'Lokalna baza ({n} kodova)', 'db_downloading': 'Preuzimam bazu...', 'panel_drivers': 'USB/RS232 DRAJVERI', 'btn_install': 'Instaliraj', 'panel_found': 'PRONADJENE GRESKE', 'found_count': '{n} kodova', 'col_code': 'Kod', 'col_desc': 'Opis greske', 'col_time': 'Vreme', 'btn_export': 'Sacuvaj izvestaj', 'btn_clear_list': 'Obrisi listu', 'panel_details': 'DETALJI / RUCNA PRETRAGA', 'details_hint': 'Klikni na gresku ili unesi kod rucno.', 'panel_log': 'UART LOG', 'btn_clear_log': 'Obrisi log', 'status_ready': 'Spreman.', 'status_connected': 'Povezano: {port} @ {baud}', 'status_disconnected': 'Veza prekinuta.', 'status_reading': 'Citam greske sa PS5...', 'status_cleared': 'Greske uspesno obrisane sa PS5.', 'status_saved': 'Sacuvano: {path}', 'status_no_codes': 'Nema kodova za cuvanje.', 'status_found': 'Pronadjen: {code} – {desc}', 'log_connected': '[VEZA] Spojen na {port} @ {baud}\n', 'log_disconnected': '[VEZA] Veza prekinuta.\n', 'log_emc_ready': '[EMC] CMD READY detektovan – Ctrl+E poslan\n', 'log_emc_active': '[EMC] OK odgovor – EMC aktivan\n', 'log_reading': '[CITANJE] Pokrenuto...\n', 'log_read_done': '[CITANJE] {msg}\n', 'log_read_end': '[CITANJE] Kraj errlog-a.\n', 'log_clearing': "[BRISANJE] Saljem 'errlog clear'...\n", 'log_cleared_ok': '[BRISANJE] Uspesno obrisano.\n', 'log_db_updated': '[DB] Azurirana: {n} kodova\n', 'log_db_offline': '[DB] Nema interneta – koristi se lokalna baza.\n', 'dlg_clear_title': 'Obrisi greske sa PS5?', 'dlg_clear_body': "Salje se 'errlog clear' komanda PS5 konzoli.\nSvi zapisi na konzoli bice trajno obrisani.\n\nPreporucuje se da prvo sacuvas kodove.", 'dlg_yes': 'Da, obrisi', 'dlg_no': 'Otkazi', 'err_no_port': 'Izaberite serijski port.', 'err_serial': 'Greska serijskog porta', 'err_save': 'Greska pri cuvanju', 'no_devices': '(nema povezanih USB uredjaja)', 'pinout_title': 'PS5 UART Pinout', 'pinout_pages': ['EDM-010 / EDM-020', 'EDM-030 / EDM-03x', 'EDM-040 / EDM-041 (Slim)', 'Spajanje adaptera'], 'wiring_ps5': 'PS5 konzola', 'wiring_adapter': 'USB/RS232 adapter', 'wiring_note1': 'TX i RX su uvek ukrsteni!', 'wiring_note2': 'Baud: 115200  |  8N1  |  3.3V TTL  (ne 5V!)', 'pad_gnd': 'GND', 'pad_tx': 'TX  →  RX adaptera', 'pad_tx_slim': 'TX  →  RX adaptera (levi)', 'pad_rx': 'RX  ←  TX adaptera', 'pad_gnd_left': 'GND  (levi pad, red 1)', 'pad_gnd_below': 'GND  (ispod, sredina)', 'pinout_note_010': 'Padovi pored WiFi modula, desna kolona  |  3.3V logika!', 'pinout_note_030': 'Padovi ispod fan konektora, u dva reda  |  3.3V logika!', 'pinout_note_040': 'Fan adapter mora biti pricvrscen vijkom  |  3.3V logika!', 'wifi_label': 'WiFi modul', 'fan_label': 'Fan konektor', 'screw_label': 'vijak (montaza)', 'help_title': 'Uputstvo za koriscenje', 'btn_close': 'Zatvori', 'severity_critical': 'KRITICNA GRESKA', 'severity_warning': 'UPOZORENJE', 'severity_info': 'INFO', 'severity_unknown': 'NEPOZNATO', 'export_header': 'PS5 UART Dijagnoza\nServis Port Sabac\n', 'export_date': 'Datum: {date}\n', 'export_code': 'KOD:   {code}\n', 'export_desc': 'OPIS:  {desc}\n', 'export_time': 'VREME: {time}\n', 'log_wake': '[WAKE] Ctrl+E poslan (pokusaj {n})\n', 'log_wake_enter': '[WAKE] Enter poslan...\n', 'log_timeout': '[TIMEOUT] Nema odgovora na errlog {n}\n', 'read_done_msg': 'Citanje zavrseno – {n} zapisa.', 'read_no_errors': ' Nema gresaka.', 'log_port_found': '[PORT] Pronadjeno {n} USB port(ova).\n', 'sev_critical': 'KRITICNA GRESKA', 'sev_warning': 'UPOZORENJE', 'sev_info': 'INFO', 'sev_unknown': 'NEPOZNATO', 'code_not_found': 'Kod nije pronadjen u bazi'}, 'en': {'app_title': 'PS5 UART Diagnostics  v2.0', 'app_subtitle': 'Servis Port Sabac  •  RS232/USB  –  read and clear errors', 'btn_help': '? Help', 'lang_toggle': 'SR', 'panel_port': 'SERIAL PORT', 'baud_label': 'Baud:', 'btn_connect': 'Connect', 'btn_disconnect': 'Disconnect', 'btn_refresh': 'Refresh', 'btn_pinout': 'Pinout', 'conn_off': 'Not connected', 'emc_wait': 'EMC: waiting for PS5...', 'emc_ready': 'EMC: ready for commands', 'panel_commands': 'PS5 COMMANDS', 'btn_read': 'Read all errors from PS5', 'btn_clear_ps5': 'Clear errors from PS5', 'custom_cmd_label': 'Custom command:', 'btn_send': 'Send', 'panel_search': 'MANUAL LOOKUP', 'btn_search': 'Search database', 'search_hint': 'e.g. 80C00140', 'panel_db': 'ERROR DATABASE', 'btn_update_db': 'Update database', 'db_loading': 'Loading...', 'db_online': 'Online ({n} codes)', 'db_offline': 'Offline ({n} codes)', 'db_local': 'Local database ({n} codes)', 'db_downloading': 'Downloading database...', 'panel_drivers': 'USB/RS232 DRIVERS', 'btn_install': 'Install', 'panel_found': 'FOUND ERRORS', 'found_count': '{n} codes', 'col_code': 'Code', 'col_desc': 'Error description', 'col_time': 'Time', 'btn_export': 'Save report', 'btn_clear_list': 'Clear list', 'panel_details': 'DETAILS / MANUAL LOOKUP', 'details_hint': 'Click an error or enter a code manually.', 'panel_log': 'UART LOG', 'btn_clear_log': 'Clear log', 'status_ready': 'Ready.', 'status_connected': 'Connected: {port} @ {baud}', 'status_disconnected': 'Connection closed.', 'status_reading': 'Reading errors from PS5...', 'status_cleared': 'Errors successfully cleared from PS5.', 'status_saved': 'Saved: {path}', 'status_no_codes': 'No codes to save.', 'status_found': 'Found: {code} – {desc}', 'log_connected': '[CONN] Connected to {port} @ {baud}\n', 'log_disconnected': '[CONN] Connection closed.\n', 'log_emc_ready': '[EMC] CMD READY detected – Ctrl+E sent\n', 'log_emc_active': '[EMC] OK response – EMC active\n', 'log_reading': '[READ] Started reading errlog...\n', 'log_read_done': '[READ] {msg}\n', 'log_read_end': '[READ] End of errlog (FFFFFFFF).\n', 'log_clearing': "[CLEAR] Sending 'errlog clear'...\n", 'log_cleared_ok': '[CLEAR] Successfully cleared.\n', 'log_db_updated': '[DB] Updated: {n} codes\n', 'log_db_offline': '[DB] No internet – using local database.\n', 'dlg_clear_title': 'Clear errors from PS5?', 'dlg_clear_body': "This sends 'errlog clear' to the PS5 console.\nAll error records will be permanently deleted.\n\nIt is recommended to save the codes first.", 'dlg_yes': 'Yes, clear', 'dlg_no': 'Cancel', 'err_no_port': 'Please select a serial port.', 'err_serial': 'Serial port error', 'err_save': 'Save error', 'no_devices': '(no USB devices connected)', 'pinout_title': 'PS5 UART Pinout', 'pinout_pages': ['EDM-010 / EDM-020', 'EDM-030 / EDM-03x', 'EDM-040 / EDM-041 (Slim)', 'Adapter wiring'], 'wiring_ps5': 'PS5 console', 'wiring_adapter': 'USB/RS232 adapter', 'wiring_note1': 'TX and RX are always crossed!', 'wiring_note2': 'Baud: 115200  |  8N1  |  3.3V TTL  (not 5V!)', 'pad_gnd': 'GND', 'pad_tx': 'TX  →  Adapter RX', 'pad_tx_slim': 'TX  →  Adapter RX (left)', 'pad_rx': 'RX  ←  Adapter TX', 'pad_gnd_left': 'GND  (left pad, row 1)', 'pad_gnd_below': 'GND  (below, center)', 'pinout_note_010': 'Pads next to WiFi module, right column  |  3.3V logic!', 'pinout_note_030': 'Pads below fan connector, two rows  |  3.3V logic!', 'pinout_note_040': 'Fan adapter must be secured with screw  |  3.3V logic!', 'wifi_label': 'WiFi module', 'fan_label': 'Fan connector', 'screw_label': 'screw (mount)', 'help_title': 'Help / Instructions', 'btn_close': 'Close', 'severity_critical': 'CRITICAL ERROR', 'severity_warning': 'WARNING', 'severity_info': 'INFO', 'severity_unknown': 'UNKNOWN', 'export_header': 'PS5 UART Diagnostic Report\nServis Port Sabac\n', 'export_date': 'Date: {date}\n', 'export_code': 'CODE:  {code}\n', 'export_desc': 'DESC:  {desc}\n', 'export_time': 'TIME:  {time}\n', 'log_wake': '[WAKE] Ctrl+E sent (attempt {n})\n', 'log_wake_enter': '[WAKE] Enter sent...\n', 'log_timeout': '[TIMEOUT] No response to errlog {n}\n', 'read_done_msg': 'Read complete – {n} records.', 'read_no_errors': ' No errors found.', 'log_port_found': '[PORT] Found {n} USB port(s).\n', 'sev_critical': 'CRITICAL ERROR', 'sev_warning': 'WARNING', 'sev_info': 'INFO', 'sev_unknown': 'UNKNOWN', 'code_not_found': 'Code not found in database'}}

HELP_TEXTS = {'sr': 'PS5 UART Dijagnostika v2.0  –  Servis Port Sabac\n\nSPAJANJE PS5 NA ADAPTER\n━━━━━━━━━━━━━━━━━━━━━━\nPS5 TX  →  Adapter RX\nPS5 RX  ←  Adapter TX\nPS5 GND —  Adapter GND\n\nLogika: 3.3V TTL (ne 5V!)\nBaud rate: 115200 / 8N1\n\nKORACI ZA CITANJE GRESAKA\n━━━━━━━━━━━━━━━━━━━━━━━━\n1. Pokrenuti aplikaciju\n2. Kliknuti Osvezi za listu portova\n3. Izabrati port (/dev/ttyUSB0 ili COM3)\n4. Kliknuti Povezi\n5. Prikljuciti PS5 SAMO na struju\n   (ne pritiskati power dugme)\n6. Sacekati 10-20 sec — EMC postane zelen\n7. Kliknuti Citaj sve greske sa PS5\n8. Kliknuti na gresku za detaljan opis\n9. Po potrebi: Sacuvaj izvestaj\n10. Opciono: Obrisi greske sa PS5\n\nUART KOMANDE\n━━━━━━━━━━━\nerrlog 0..31  — cita N-ti zapis\nerrlog clear  — brise sve zapise\nerrlog count  — broj zapisa\nerrver        — verzija firmware-a\n\nPINOUT PO REVIZIJI PLOCE\n━━━━━━━━━━━━━━━━━━━━━━━\nEDM-010/020: padovi pored WiFi modula,\n             desna kolona (GND, TX, RX)\nEDM-030/03x: padovi ispod fan konektora,\n             GND levo, TX i RX desno\nEDM-040/041: padovi na ivici ploce,\n             TX levo, RX pored, GND ispod\n\nRESAVANJE PROBLEMA\n━━━━━━━━━━━━━━━━━\nEMC ostaje narandzast → zameni TX/RX zice\nLampice ne treperu    → proveri drajver adaptera\nPort nije vidljiv     → pritisni Osvezi\nTimeout               → iskljuci/ukljuci PS5 struju', 'en': 'PS5 UART Diagnostics v2.0  –  Servis Port Sabac\n\nCONNECTING PS5 TO ADAPTER\n━━━━━━━━━━━━━━━━━━━━━━━━\nPS5 TX  →  Adapter RX\nPS5 RX  ←  Adapter TX\nPS5 GND —  Adapter GND\n\nLogic: 3.3V TTL (not 5V!)\nBaud rate: 115200 / 8N1\n\nSTEPS TO READ ERRORS\n━━━━━━━━━━━━━━━━━━━\n1. Launch the application\n2. Click Refresh to list serial ports\n3. Select port (/dev/ttyUSB0 or COM3)\n4. Click Connect\n5. Connect PS5 to power ONLY\n   (do NOT press the power button)\n6. Wait 10-20 sec — EMC turns green\n7. Click Read all errors from PS5\n8. Click an error for detailed description\n9. If needed: Save report\n10. Optional: Clear errors from PS5\n\nUART COMMANDS\n━━━━━━━━━━━━\nerrlog 0..31  — reads N-th record\nerrlog clear  — clears all records\nerrlog count  — number of records\nerrver        — EMC firmware version\n\nPINOUT BY BOARD REVISION\n━━━━━━━━━━━━━━━━━━━━━━━\nEDM-010/020: pads next to WiFi module,\n             right column (GND, TX, RX)\nEDM-030/03x: pads below fan connector,\n             GND left, TX and RX right\nEDM-040/041: pads at board edge,\n             TX left, RX next, GND below\n\nTROUBLESHOOTING\n━━━━━━━━━━━━━━\nEMC stays orange  → swap TX/RX wires\nAdapter LEDs off  → check adapter driver\nPort not visible  → press Refresh\nTimeout           → unplug/replug PS5 power'}

def tr(key, lang="sr", **kw):
    t = TRANSLATIONS.get(lang, TRANSLATIONS["sr"]).get(key, key)
    if kw:
        try: t = t.format(**kw)
        except: pass
    return t

# ─── Konstante ────────────────────────────────────────────────────────────────
APP_TITLE   = "PS5 UART Dijagnostika v2.0 – Servis Port"
BAUD_RATE   = 115200
DB_URL = "https://servisport.rs/servisni/download/ps5.xml"
DB_PATH     = os.path.expanduser("~/.ps5uart/codes.json")
LOG_PATH    = os.path.expanduser("~/.ps5uart/history.log")

# Lokalni ps5.xml — pored exe-a ili skripte
def _local_xml_path():
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "ps5.xml")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ps5.xml")

BUILTIN_CODES = {
    "00100E3C": "Observed error code 00100E3C. Cause not yet determined.",
    "0015442C": "Observed error code 0015442C. Cause not yet determined.",
    "015E4E8B": "Observed error code 015E4E8B. Cause not yet determined.",
    "80000001": "APU Overheat or Initialization Error",
    "80000008": "Observed error code 80000008. Cause not yet determined.",
    "80000009": "Unexpected Power Loss or Shutdown Failure",
    "8000000C": "Observed error code 8000000C. Cause not yet determined.",
    "80050000": "APU VRM (2 Phases) Power Fail, Check Infineon XDPE14286A 16 Phase PWM Controller, Check mosfets APU side for short (Caps Usually Short) - Single Beep, 1 Second Blue Light, 8.6mA draw power on.",
    "80050020": "Observed error code 80050020. Cause not yet determined.",
    "80050040": "Observed error code 80050040. Cause not yet determined.",
    "80060000": "APU VRM (6 Phases) Power Fail, Check Infineon XDPE14286A 16 Phase PWM Controller",
    "80060020": "Observed error code 80060020. Cause not yet determined.",
    "80060040": "Observed error code 80060040. Cause not yet determined.",
    "80068000": "Observed error code 80068000. Cause not yet determined.",
    "80097CE4": "Observed error code 80097CE4. Cause not yet determined.",
    "80800000": "Kernel Panic Shutdown",
    "80800014": "TPM 2.0 chip or Power Failure",
    "8080001A": "Non-Native TPM 2.0 Chip (After APU Init)",
    "8080001F": "Observed error code 8080001F. Cause not yet determined.",
    "80800022": "No/Bad Communication Between APU -> RAM - APU Initilized - Replace All/Some RAM (Check APU for Die Cracks)",
    "80800023": "Observed error code 80800023. Cause not yet determined.",
    "80800024": "Observed error code 80800024. Cause not yet determined.",
    "80801028": "Observed error code 80801028. Cause not yet determined.",
    "80802001": "SSD controller (coprocessor) <-> APU data",
    "80802081": "SSD Controller (Co-Processor) <-> APU Data Line Error",
    "80802220": "Observed error code 80802220. Cause not yet determined.",
    "80802442": "Observed error code 80802442. Cause not yet determined.",
    "80802471": "Observed error code 80802471. Cause not yet determined.",
    "80802660": "Observed error code 80802660. Cause not yet determined.",
    "80802669": "Observed error code 80802669. Cause not yet determined.",
    "80810001": "General Power Failure (Peripheral, GDDR6, APU, Data Line Short)",
    "8081001A": "Observed error code 8081001A. Cause not yet determined.",
    "80830000": "Shutdown or Freeze After SAM_IPL Loaded - GDDR6 Data Line Issue (Replace)",
    "80830018": "Observed error code 80830018. Cause not yet determined.",
    "80830019": "Observed error code 80830019. Cause not yet determined.",
    "808300F0": "Secure Loader Error",
    "808300F1": "Observed error code 808300F1. Cause not yet determined.",
    "80870003": "Post Secure Loader Error - Check fuse F7001 - (No beep, no light)",
    "80870004": "Observed error code 80870004. Cause not yet determined.",
    "80871001": "DDR4 Error (Power Failure or Short Circuit)",
    "80871054": "SSD Banks IO Error Between SSD Controller",
    "80871055": "SSD Banks IO Error Between SSD Controller",
    "80871062": "SSD Controller <-> Syscon (Bridge) Data Line Error",
    "808710FF": "Observed error code 808710FF. Cause not yet determined.",
    "80891001": "SSD Controller or DDR4 Error (Power Failure or Short Circuit)",
    "80892003": "SSD Controller or DDR4 Error (Power Failure or Short Circuit)",
    "80894003": "SSD Controller or DDR4 Error (Power Failure or Short Circuit) - Missing 2.5v on DA9081",
    "8089400F": "SSD Controller or DDR4 Error (Power Failure or Short Circuit)",
    "808940AE": "NOR Modification Error.",
    "808B0000": "Observed error code 808B0000. Cause not yet determined.",
    "808B0027": "Power Short 5V Line (F7002) - Single Beep, No LED.",
    "808B0098": "DDR4 Error (Communication Issue)",
    "808B00FF": "Observed error code 808B00FF. Cause not yet determined.",
    "808C2092": "Possibly APU I2C lines damaged or disconnected. Check APU for die cracks.",
    "808C3090": "Power Failure - PWM or Unspecific",
    "808C3790": "Power Failure - PWM or Unspecific",
    "808C3F90": "Power Failure - PWM or Unspecific",
    "808C4E90": "Observed error code 808C4E90. Cause not yet determined.",
    "808C4F90": "Power Failure - PWM or Unspecific",
    "808D0000": "Observed error code 808D0000. Cause not yet determined.",
    "808D0002": "Issue with daughter board (LED Board) Check Flex and Daughter Board Repair or Replace - Three Beeps, White Light, Immediate Shutdown.",
    "808E0005": "Observed error code 808E0005. Cause not yet determined.",
    "808E0006": "Observed error code 808E0006. Cause not yet determined.",
    "808E0109": "Observed error code 808E0109. Cause not yet determined.",
    "808E829A": "Observed error code 808E829A. Cause not yet determined.",
    "808F0002": "TPM 2.0 chip or Power Failure",
    "808F0003": "TPM 2.0 chip or Power Failure",
    "80900100": "Observed error code 80900100. Cause not yet determined.",
    "80910002": "Observed error code 80910002. Cause not yet determined.",
    "80910200": "SSD Controller or DDR4 Error (Power Failure or Short Circuit) - Possible DA9081 1.2v Side: APU",
    "80910800": "SSD Controller or DDR4 Error (Power Failure or Short Circuit) - Possible DA9081 1.2v Side: Fan",
    "80910A00": "Observed error code 80910A00. Cause not yet determined.",
    "80912000": "Observed error code 80912000. Cause not yet determined.",
    "80918000": "Observed error code 80918000. Cause not yet determined.",
    "80C00114": "Observed error code 80C00114. Cause not yet determined.",
    "80C0012D": "Observed error code 80C0012D. Cause not yet determined.",
    "80C00134": "SSD Banks Error",
    "80C00136": "WI-FI or BT Problem or Power Failure - (Check WI-FI/Bluethtooh Module code thrown when module removed) - Powers off after 2 seconds",
    "80C00140": "APU Halt (No Response) - Forced Power Off Via Power Button",
    "80D002F5": "Observed error code 80D002F5. Cause not yet determined.",
    "80D004F5": "Observed error code 80D004F5. Cause not yet determined.",
    "80D00402": "SSD Banks Error",
    "86000005": "NOR Corrupt - Regenerate with tool and try again!",
    "86000006": "NOR Corrupt - Regenerate with tool and try again!",
    "B0012404": "HDMI Port - (User Submitted: Check HDMI Port, Port was damaged)",
    "B0082108": "Observed error code B0082108. Cause not yet determined.",
    "B0085108": "Observed error code B0085108. Cause not yet determined.",
    "B0088108": "Observed error code B0088108. Cause not yet determined.",
    "B0FFFFFF": "Observed error code B0FFFFFF. Cause not yet determined.",
    "C0010303": "Observed error code C0010303. Cause not yet determined.",
    "C0020103": "APU Not Responding - Trying Init or Reboot - 1",
    "C0020203": "APU Not Responding - Trying Init or Reboot - 2",
    "C0020303": "APU Not Responding - Trying Init or Reboot - 3 - (User Submitted: System wont start Blue Light Flashes)",
    "C00C0002": "VRM Controller Failure, Check Mosfet (6414A) Located Side-A, Below Sony Interactive Entertainment Inc. Check Infineon XDPE14286A 16 Phase PWM Controller - Located Side-A, Right of fuse 7001 - Single Beep, 1 second blue light, off.",
    "C00C0303": "Observed error code C00C0303. Cause not yet determined.",
    "C00C8000": "Observed error code C00C8000. Cause not yet determined.",
    "C0160203": "Observed error code C0160203. Cause not yet determined.",
    "C0160303": "Observed error code C0160303. Cause not yet determined.",
    "C0810002": "HDMI IC Problem or Power Failure",
    "C0810303": "HDMI IC Problem or Data Line Short or Power Failure",
    "C0900002": "HDMI fault - Possible short on or around MN864739",
    "C0900303": "Observed error code C0900303. Cause not yet determined.",
    "C0920002": "Observed error code C0920002. Cause not yet determined.",
    "E0000001": "Southbridge Issue - Cannot Read Errors - Wait & Retry",
    "E0000002": "Southbridge Issue - Cannot Read Errors - Wait & Retry",
    "E0000003": "Southbridge Issue - Cannot Read Errors - Wait & Retry",
    "E0000004": "Southbridge Issue - Cannot Read Errors - Wait & Retry",
    "E0000005": "Southbridge Issue - Cannot Read Errors - Wait & Retry",
    "E0000006": "Southbridge Issue - Cannot Read Errors - Wait & Retry",
    "E1200000": "Observed error code E1200000. Cause not yet determined.",
    "E1201A50": "Observed error code E1201A50. Cause not yet determined.",
    "E1E00619": "Observed error code E1E00619. Cause not yet determined.",
    "E1E0061D": "Observed error code E1E0061D. Cause not yet determined.",
    "E1E0191D": "Observed error code E1E0191D. Cause not yet determined.",
    "E1E01C05": "Observed error code E1E01C05. Cause not yet determined.",
    "E1E01D06": "Observed error code E1E01D06. Cause not yet determined.",
    "E2200000": "Observed error code E2200000. Cause not yet determined.",
    "E2E0061D": "Observed error code E2E0061D. Cause not yet determined.",
    "E2200116": "Observed error code E2200116. Cause not yet determined.",
    "E2E0191D": "Observed error code E2E0191D. Cause not yet determined.",
    "E2E01C06": "Observed error code E2E01C06. Cause not yet determined.",
    "E2E01D06": "Observed error code E2E01D06. Cause not yet determined.",
    "E31218E9": "Observed error code E31218E9. Cause not yet determined.",
    "E3121F70": "Observed error code E3121F70. Cause not yet determined.",
    "E3122155": "Observed error code E3122155. Cause not yet determined.",
    "E312210A": "Observed error code E312210A. Cause not yet determined.",
    "E3122219": "Observed error code E3122219. Cause not yet determined.",
    "FFFFFFFF": "No Errors",
    "80801101": "RAM dataline fault on Chip 1. Reball or replace RAM.",
    "80801102": "RAM dataline fault on Chip 2. Reball or replace RAM.",
    "80801103": "RAM dataline fault on Chip 1,2. Reball or replace RAM.",
    "80801104": "RAM dataline fault on Chip 3. Reball or replace RAM.",
    "80801105": "RAM dataline fault on Chip 1,3. Reball or replace RAM.",
    "80801106": "RAM dataline fault on Chip 2,3. Reball or replace RAM.",
    "80801107": "RAM dataline fault on Chip 1,2,3. Reball or replace RAM.",
    "80801108": "RAM dataline fault on Chip 4. Reball or replace RAM.",
    "80801109": "RAM dataline fault on Chip 1,4. Reball or replace RAM.",
    "8080110A": "RAM dataline fault on Chip 2,4. Reball or replace RAM.",
    "8080110B": "RAM dataline fault on Chip 1,2,4. Reball or replace RAM.",
    "8080110C": "RAM dataline fault on Chip 3,4. Reball or replace RAM.",
    "8080110D": "RAM dataline fault on Chip 1,3,4. Reball or replace RAM.",
    "8080110E": "RAM dataline fault on Chip 2,3,4. Reball or replace RAM.",
    "8080110F": "RAM dataline fault on Chip 1,2,3,4. Reball or replace RAM.",
    "80801110": "RAM dataline fault on Chip 5. Reball or replace RAM.",
    "80801111": "RAM dataline fault on Chip 1,5. Reball or replace RAM.",
    "80801112": "RAM dataline fault on Chip 2,5. Reball or replace RAM.",
    "80801113": "RAM dataline fault on Chip 1,2,5. Reball or replace RAM.",
    "80801114": "RAM dataline fault on Chip 3,5. Reball or replace RAM.",
    "80801115": "RAM dataline fault on Chip 1,3,5. Reball or replace RAM.",
    "80801116": "RAM dataline fault on Chip 2,3,5. Reball or replace RAM.",
    "80801117": "RAM dataline fault on Chip 1,2,3,5. Reball or replace RAM.",
    "80801118": "RAM dataline fault on Chip 4,5. Reball or replace RAM.",
    "80801119": "RAM dataline fault on Chip 1,4,5. Reball or replace RAM.",
    "8080111A": "RAM dataline fault on Chip 2,4,5. Reball or replace RAM.",
    "8080111B": "RAM dataline fault on Chip 1,2,4,5. Reball or replace RAM.",
    "8080111C": "RAM dataline fault on Chip 3,4,5. Reball or replace RAM.",
    "8080111D": "RAM dataline fault on Chip 1,3,4,5. Reball or replace RAM.",
    "8080111E": "RAM dataline fault on Chip 2,3,4,5. Reball or replace RAM.",
    "8080111F": "RAM dataline fault on Chip 1,2,3,4,5. Reball or replace RAM.",
    "80801120": "RAM dataline fault on Chip 6. Reball or replace RAM.",
    "80801121": "RAM dataline fault on Chip 1,6. Reball or replace RAM.",
    "80801122": "RAM dataline fault on Chip 2,6. Reball or replace RAM.",
    "80801123": "RAM dataline fault on Chip 1,2,6. Reball or replace RAM.",
    "80801124": "RAM dataline fault on Chip 3,6. Reball or replace RAM.",
    "80801125": "RAM dataline fault on Chip 1,3,6. Reball or replace RAM.",
    "80801126": "RAM dataline fault on Chip 2,3,6. Reball or replace RAM.",
    "80801127": "RAM dataline fault on Chip 1,2,3,6. Reball or replace RAM.",
    "80801128": "RAM dataline fault on Chip 4,6. Reball or replace RAM.",
    "80801129": "RAM dataline fault on Chip 1,4,6. Reball or replace RAM.",
    "8080112A": "RAM dataline fault on Chip 2,4,6. Reball or replace RAM.",
    "8080112B": "RAM dataline fault on Chip 1,2,4,6. Reball or replace RAM.",
    "8080112C": "RAM dataline fault on Chip 3,4,6. Reball or replace RAM.",
    "8080112D": "RAM dataline fault on Chip 1,3,4,6. Reball or replace RAM.",
    "8080112E": "RAM dataline fault on Chip 2,3,4,6. Reball or replace RAM.",
    "8080112F": "RAM dataline fault on Chip 1,2,3,4,6. Reball or replace RAM.",
    "80801130": "RAM dataline fault on Chip 5,6. Reball or replace RAM.",
    "80801131": "RAM dataline fault on Chip 1,5,6. Reball or replace RAM.",
    "80801132": "RAM dataline fault on Chip 2,5,6. Reball or replace RAM.",
    "80801133": "RAM dataline fault on Chip 1,2,5,6. Reball or replace RAM.",
    "80801134": "RAM dataline fault on Chip 3,5,6. Reball or replace RAM.",
    "80801135": "RAM dataline fault on Chip 1,3,5,6. Reball or replace RAM.",
    "80801136": "RAM dataline fault on Chip 2,3,5,6. Reball or replace RAM.",
    "80801137": "RAM dataline fault on Chip 1,2,3,5,6. Reball or replace RAM.",
    "80801138": "RAM dataline fault on Chip 4,5,6. Reball or replace RAM.",
    "80801139": "RAM dataline fault on Chip 1,4,5,6. Reball or replace RAM.",
    "8080113A": "RAM dataline fault on Chip 2,4,5,6. Reball or replace RAM.",
    "8080113B": "RAM dataline fault on Chip 1,2,4,5,6. Reball or replace RAM.",
    "8080113C": "RAM dataline fault on Chip 3,4,5,6. Reball or replace RAM.",
    "8080113D": "RAM dataline fault on Chip 1,3,4,5,6. Reball or replace RAM.",
    "8080113E": "RAM dataline fault on Chip 2,3,4,5,6. Reball or replace RAM.",
    "8080113F": "RAM dataline fault on Chip 1,2,3,4,5,6. Reball or replace RAM.",
    "80801140": "RAM dataline fault on Chip 7. Reball or replace RAM.",
    "80801141": "RAM dataline fault on Chip 1,7. Reball or replace RAM.",
    "80801142": "RAM dataline fault on Chip 2,7. Reball or replace RAM.",
    "80801143": "RAM dataline fault on Chip 1,2,7. Reball or replace RAM.",
    "80801144": "RAM dataline fault on Chip 3,7. Reball or replace RAM.",
    "80801145": "RAM dataline fault on Chip 1,3,7. Reball or replace RAM.",
    "80801146": "RAM dataline fault on Chip 2,3,7. Reball or replace RAM.",
    "80801147": "RAM dataline fault on Chip 1,2,3,7. Reball or replace RAM.",
    "80801148": "RAM dataline fault on Chip 4,7. Reball or replace RAM.",
    "80801149": "RAM dataline fault on Chip 1,4,7. Reball or replace RAM.",
    "8080114A": "RAM dataline fault on Chip 2,4,7. Reball or replace RAM.",
    "8080114B": "RAM dataline fault on Chip 1,2,4,7. Reball or replace RAM.",
    "8080114C": "RAM dataline fault on Chip 3,4,7. Reball or replace RAM.",
    "8080114D": "RAM dataline fault on Chip 1,3,4,7. Reball or replace RAM.",
    "8080114E": "RAM dataline fault on Chip 2,3,4,7. Reball or replace RAM.",
    "8080114F": "RAM dataline fault on Chip 1,2,3,4,7. Reball or replace RAM.",
    "80801150": "RAM dataline fault on Chip 5,7. Reball or replace RAM.",
    "80801151": "RAM dataline fault on Chip 1,5,7. Reball or replace RAM.",
    "80801152": "RAM dataline fault on Chip 2,5,7. Reball or replace RAM.",
    "80801153": "RAM dataline fault on Chip 1,2,5,7. Reball or replace RAM.",
    "80801154": "RAM dataline fault on Chip 3,5,7. Reball or replace RAM.",
    "80801155": "RAM dataline fault on Chip 1,3,5,7. Reball or replace RAM.",
    "80801156": "RAM dataline fault on Chip 2,3,5,7. Reball or replace RAM.",
    "80801157": "RAM dataline fault on Chip 1,2,3,5,7. Reball or replace RAM.",
    "80801158": "RAM dataline fault on Chip 4,5,7. Reball or replace RAM.",
    "80801159": "RAM dataline fault on Chip 1,4,5,7. Reball or replace RAM.",
    "8080115A": "RAM dataline fault on Chip 2,4,5,7. Reball or replace RAM.",
    "8080115B": "RAM dataline fault on Chip 1,2,4,5,7. Reball or replace RAM.",
    "8080115C": "RAM dataline fault on Chip 3,4,5,7. Reball or replace RAM.",
    "8080115D": "RAM dataline fault on Chip 1,3,4,5,7. Reball or replace RAM.",
    "8080115E": "RAM dataline fault on Chip 2,3,4,5,7. Reball or replace RAM.",
    "8080115F": "RAM dataline fault on Chip 1,2,3,4,5,7. Reball or replace RAM.",
    "80801160": "RAM dataline fault on Chip 6,7. Reball or replace RAM.",
    "80801161": "RAM dataline fault on Chip 1,6,7. Reball or replace RAM.",
    "80801162": "RAM dataline fault on Chip 2,6,7. Reball or replace RAM.",
    "80801163": "RAM dataline fault on Chip 1,2,6,7. Reball or replace RAM.",
    "80801164": "RAM dataline fault on Chip 3,6,7. Reball or replace RAM.",
    "80801165": "RAM dataline fault on Chip 1,3,6,7. Reball or replace RAM.",
    "80801166": "RAM dataline fault on Chip 2,3,6,7. Reball or replace RAM.",
    "80801167": "RAM dataline fault on Chip 1,2,3,6,7. Reball or replace RAM.",
    "80801168": "RAM dataline fault on Chip 4,6,7. Reball or replace RAM.",
    "80801169": "RAM dataline fault on Chip 1,4,6,7. Reball or replace RAM.",
    "8080116A": "RAM dataline fault on Chip 2,4,6,7. Reball or replace RAM.",
    "8080116B": "RAM dataline fault on Chip 1,2,4,6,7. Reball or replace RAM.",
    "8080116C": "RAM dataline fault on Chip 3,4,6,7. Reball or replace RAM.",
    "8080116D": "RAM dataline fault on Chip 1,3,4,6,7. Reball or replace RAM.",
    "8080116E": "RAM dataline fault on Chip 2,3,4,6,7. Reball or replace RAM.",
    "8080116F": "RAM dataline fault on Chip 1,2,3,4,6,7. Reball or replace RAM.",
    "80801170": "RAM dataline fault on Chip 5,6,7. Reball or replace RAM.",
    "80801171": "RAM dataline fault on Chip 1,5,6,7. Reball or replace RAM.",
    "80801172": "RAM dataline fault on Chip 2,5,6,7. Reball or replace RAM.",
    "80801173": "RAM dataline fault on Chip 1,2,5,6,7. Reball or replace RAM.",
    "80801174": "RAM dataline fault on Chip 3,5,6,7. Reball or replace RAM.",
    "80801175": "RAM dataline fault on Chip 1,3,5,6,7. Reball or replace RAM.",
    "80801176": "RAM dataline fault on Chip 2,3,5,6,7. Reball or replace RAM.",
    "80801177": "RAM dataline fault on Chip 1,2,3,5,6,7. Reball or replace RAM.",
    "80801178": "RAM dataline fault on Chip 4,5,6,7. Reball or replace RAM.",
    "80801179": "RAM dataline fault on Chip 1,4,5,6,7. Reball or replace RAM.",
    "8080117A": "RAM dataline fault on Chip 2,4,5,6,7. Reball or replace RAM.",
    "8080117B": "RAM dataline fault on Chip 1,2,4,5,6,7. Reball or replace RAM.",
    "8080117C": "RAM dataline fault on Chip 3,4,5,6,7. Reball or replace RAM.",
    "8080117D": "RAM dataline fault on Chip 1,3,4,5,6,7. Reball or replace RAM.",
    "8080117E": "RAM dataline fault on Chip 2,3,4,5,6,7. Reball or replace RAM.",
    "8080117F": "RAM dataline fault on Chip 1,2,3,4,5,6,7. Reball or replace RAM.",
    "80801180": "RAM dataline fault on Chip 8. Reball or replace RAM.",
    "80801181": "RAM dataline fault on Chip 1,8. Reball or replace RAM.",
    "80801182": "RAM dataline fault on Chip 2,8. Reball or replace RAM.",
    "80801183": "RAM dataline fault on Chip 1,2,8. Reball or replace RAM.",
    "80801184": "RAM dataline fault on Chip 3,8. Reball or replace RAM.",
    "80801185": "RAM dataline fault on Chip 1,3,8. Reball or replace RAM.",
    "80801186": "RAM dataline fault on Chip 2,3,8. Reball or replace RAM.",
    "80801187": "RAM dataline fault on Chip 1,2,3,8. Reball or replace RAM.",
    "80801188": "RAM dataline fault on Chip 4,8. Reball or replace RAM.",
    "80801189": "RAM dataline fault on Chip 1,4,8. Reball or replace RAM.",
    "8080118A": "RAM dataline fault on Chip 2,4,8. Reball or replace RAM.",
    "8080118B": "RAM dataline fault on Chip 1,2,4,8. Reball or replace RAM.",
    "8080118C": "RAM dataline fault on Chip 3,4,8. Reball or replace RAM.",
    "8080118D": "RAM dataline fault on Chip 1,3,4,8. Reball or replace RAM.",
    "8080118E": "RAM dataline fault on Chip 2,3,4,8. Reball or replace RAM.",
    "8080118F": "RAM dataline fault on Chip 1,2,3,4,8. Reball or replace RAM.",
    "80801190": "RAM dataline fault on Chip 5,8. Reball or replace RAM.",
    "80801191": "RAM dataline fault on Chip 1,5,8. Reball or replace RAM.",
    "80801192": "RAM dataline fault on Chip 2,5,8. Reball or replace RAM.",
    "80801193": "RAM dataline fault on Chip 1,2,5,8. Reball or replace RAM.",
    "80801194": "RAM dataline fault on Chip 3,5,8. Reball or replace RAM.",
    "80801195": "RAM dataline fault on Chip 1,3,5,8. Reball or replace RAM.",
    "80801196": "RAM dataline fault on Chip 2,3,5,8. Reball or replace RAM.",
    "80801197": "RAM dataline fault on Chip 1,2,3,5,8. Reball or replace RAM.",
    "80801198": "RAM dataline fault on Chip 4,5,8. Reball or replace RAM.",
    "80801199": "RAM dataline fault on Chip 1,4,5,8. Reball or replace RAM.",
    "8080119A": "RAM dataline fault on Chip 2,4,5,8. Reball or replace RAM.",
    "8080119B": "RAM dataline fault on Chip 1,2,4,5,8. Reball or replace RAM.",
    "8080119C": "RAM dataline fault on Chip 3,4,5,8. Reball or replace RAM.",
    "8080119D": "RAM dataline fault on Chip 1,3,4,5,8. Reball or replace RAM.",
    "8080119E": "RAM dataline fault on Chip 2,3,4,5,8. Reball or replace RAM.",
    "8080119F": "RAM dataline fault on Chip 1,2,3,4,5,8. Reball or replace RAM.",
    "808011A0": "RAM dataline fault on Chip 6,8. Reball or replace RAM.",
    "808011A1": "RAM dataline fault on Chip 1,6,8. Reball or replace RAM.",
    "808011A2": "RAM dataline fault on Chip 2,6,8. Reball or replace RAM.",
    "808011A3": "RAM dataline fault on Chip 1,2,6,8. Reball or replace RAM.",
    "808011A4": "RAM dataline fault on Chip 3,6,8. Reball or replace RAM.",
    "808011A5": "RAM dataline fault on Chip 1,3,6,8. Reball or replace RAM.",
    "808011A6": "RAM dataline fault on Chip 2,3,6,8. Reball or replace RAM.",
    "808011A7": "RAM dataline fault on Chip 1,2,3,6,8. Reball or replace RAM.",
    "808011A8": "RAM dataline fault on Chip 4,6,8. Reball or replace RAM.",
    "808011A9": "RAM dataline fault on Chip 1,4,6,8. Reball or replace RAM.",
    "808011AA": "RAM dataline fault on Chip 2,4,6,8. Reball or replace RAM.",
    "808011AB": "RAM dataline fault on Chip 1,2,4,6,8. Reball or replace RAM.",
    "808011AC": "RAM dataline fault on Chip 3,4,6,8. Reball or replace RAM.",
    "808011AD": "RAM dataline fault on Chip 1,3,4,6,8. Reball or replace RAM.",
    "808011AE": "RAM dataline fault on Chip 2,3,4,6,8. Reball or replace RAM.",
    "808011AF": "RAM dataline fault on Chip 1,2,3,4,6,8. Reball or replace RAM.",
    "808011B0": "RAM dataline fault on Chip 5,6,8. Reball or replace RAM.",
    "808011B1": "RAM dataline fault on Chip 1,5,6,8. Reball or replace RAM.",
    "808011B2": "RAM dataline fault on Chip 2,5,6,8. Reball or replace RAM.",
    "808011B3": "RAM dataline fault on Chip 1,2,5,6,8. Reball or replace RAM.",
    "808011B4": "RAM dataline fault on Chip 3,5,6,8. Reball or replace RAM.",
    "808011B5": "RAM dataline fault on Chip 1,3,5,6,8. Reball or replace RAM.",
    "808011B6": "RAM dataline fault on Chip 2,3,5,6,8. Reball or replace RAM.",
    "808011B7": "RAM dataline fault on Chip 1,2,3,5,6,8. Reball or replace RAM.",
    "808011B8": "RAM dataline fault on Chip 4,5,6,8. Reball or replace RAM.",
    "808011B9": "RAM dataline fault on Chip 1,4,5,6,8. Reball or replace RAM.",
    "808011BA": "RAM dataline fault on Chip 2,4,5,6,8. Reball or replace RAM.",
    "808011BB": "RAM dataline fault on Chip 1,2,4,5,6,8. Reball or replace RAM.",
    "808011BC": "RAM dataline fault on Chip 3,4,5,6,8. Reball or replace RAM.",
    "808011BD": "RAM dataline fault on Chip 1,3,4,5,6,8. Reball or replace RAM.",
    "808011BE": "RAM dataline fault on Chip 2,3,4,5,6,8. Reball or replace RAM.",
    "808011BF": "RAM dataline fault on Chip 1,2,3,4,5,6,8. Reball or replace RAM.",
    "808011C0": "RAM dataline fault on Chip 7,8. Reball or replace RAM.",
    "808011C1": "RAM dataline fault on Chip 1,7,8. Reball or replace RAM.",
    "808011C2": "RAM dataline fault on Chip 2,7,8. Reball or replace RAM.",
    "808011C3": "RAM dataline fault on Chip 1,2,7,8. Reball or replace RAM.",
    "808011C4": "RAM dataline fault on Chip 3,7,8. Reball or replace RAM.",
    "808011C5": "RAM dataline fault on Chip 1,3,7,8. Reball or replace RAM.",
    "808011C6": "RAM dataline fault on Chip 2,3,7,8. Reball or replace RAM.",
    "808011C7": "RAM dataline fault on Chip 1,2,3,7,8. Reball or replace RAM.",
    "808011C8": "RAM dataline fault on Chip 4,7,8. Reball or replace RAM.",
    "808011C9": "RAM dataline fault on Chip 1,4,7,8. Reball or replace RAM.",
    "808011CA": "RAM dataline fault on Chip 2,4,7,8. Reball or replace RAM.",
    "808011CB": "RAM dataline fault on Chip 1,2,4,7,8. Reball or replace RAM.",
    "808011CC": "RAM dataline fault on Chip 3,4,7,8. Reball or replace RAM.",
    "808011CD": "RAM dataline fault on Chip 1,3,4,7,8. Reball or replace RAM.",
    "808011CE": "RAM dataline fault on Chip 2,3,4,7,8. Reball or replace RAM.",
    "808011CF": "RAM dataline fault on Chip 1,2,3,4,7,8. Reball or replace RAM.",
    "808011D0": "RAM dataline fault on Chip 5,7,8. Reball or replace RAM.",
    "808011D1": "RAM dataline fault on Chip 1,5,7,8. Reball or replace RAM.",
    "808011D2": "RAM dataline fault on Chip 2,5,7,8. Reball or replace RAM.",
    "808011D3": "RAM dataline fault on Chip 1,2,5,7,8. Reball or replace RAM.",
    "808011D4": "RAM dataline fault on Chip 3,5,7,8. Reball or replace RAM.",
    "808011D5": "RAM dataline fault on Chip 1,3,5,7,8. Reball or replace RAM.",
    "808011D6": "RAM dataline fault on Chip 2,3,5,7,8. Reball or replace RAM.",
    "808011D7": "RAM dataline fault on Chip 1,2,3,5,7,8. Reball or replace RAM.",
    "808011D8": "RAM dataline fault on Chip 4,5,7,8. Reball or replace RAM.",
    "808011D9": "RAM dataline fault on Chip 1,4,5,7,8. Reball or replace RAM.",
    "808011DA": "RAM dataline fault on Chip 2,4,5,7,8. Reball or replace RAM.",
    "808011DB": "RAM dataline fault on Chip 1,2,4,5,7,8. Reball or replace RAM.",
    "808011DC": "RAM dataline fault on Chip 3,4,5,7,8. Reball or replace RAM.",
    "808011DD": "RAM dataline fault on Chip 1,3,4,5,7,8. Reball or replace RAM.",
    "808011DE": "RAM dataline fault on Chip 2,3,4,5,7,8. Reball or replace RAM.",
    "808011DF": "RAM dataline fault on Chip 1,2,3,4,5,7,8. Reball or replace RAM.",
    "808011E0": "RAM dataline fault on Chip 6,7,8. Reball or replace RAM.",
    "808011E1": "RAM dataline fault on Chip 1,6,7,8. Reball or replace RAM.",
    "808011E2": "RAM dataline fault on Chip 2,6,7,8. Reball or replace RAM.",
    "808011E3": "RAM dataline fault on Chip 1,2,6,7,8. Reball or replace RAM.",
    "808011E4": "RAM dataline fault on Chip 3,6,7,8. Reball or replace RAM.",
    "808011E5": "RAM dataline fault on Chip 1,3,6,7,8. Reball or replace RAM.",
    "808011E6": "RAM dataline fault on Chip 2,3,6,7,8. Reball or replace RAM.",
    "808011E7": "RAM dataline fault on Chip 1,2,3,6,7,8. Reball or replace RAM.",
    "808011E8": "RAM dataline fault on Chip 4,6,7,8. Reball or replace RAM.",
    "808011E9": "RAM dataline fault on Chip 1,4,6,7,8. Reball or replace RAM.",
    "808011EA": "RAM dataline fault on Chip 2,4,6,7,8. Reball or replace RAM.",
    "808011EB": "RAM dataline fault on Chip 1,2,4,6,7,8. Reball or replace RAM.",
    "808011EC": "RAM dataline fault on Chip 3,4,6,7,8. Reball or replace RAM.",
    "808011ED": "RAM dataline fault on Chip 1,3,4,6,7,8. Reball or replace RAM.",
    "808011EE": "RAM dataline fault on Chip 2,3,4,6,7,8. Reball or replace RAM.",
    "808011EF": "RAM dataline fault on Chip 1,2,3,4,6,7,8. Reball or replace RAM.",
    "808011F0": "RAM dataline fault on Chip 5,6,7,8. Reball or replace RAM.",
    "808011F1": "RAM dataline fault on Chip 1,5,6,7,8. Reball or replace RAM.",
    "808011F2": "RAM dataline fault on Chip 2,5,6,7,8. Reball or replace RAM.",
    "808011F3": "RAM dataline fault on Chip 1,2,5,6,7,8. Reball or replace RAM.",
    "808011F4": "RAM dataline fault on Chip 3,5,6,7,8. Reball or replace RAM.",
    "808011F5": "RAM dataline fault on Chip 1,3,5,6,7,8. Reball or replace RAM.",
    "808011F6": "RAM dataline fault on Chip 2,3,5,6,7,8. Reball or replace RAM.",
    "808011F7": "RAM dataline fault on Chip 1,2,3,5,6,7,8. Reball or replace RAM.",
    "808011F8": "RAM dataline fault on Chip 4,5,6,7,8. Reball or replace RAM.",
    "808011F9": "RAM dataline fault on Chip 1,4,5,6,7,8. Reball or replace RAM.",
    "808011FA": "RAM dataline fault on Chip 2,4,5,6,7,8. Reball or replace RAM.",
    "808011FB": "RAM dataline fault on Chip 1,2,4,5,6,7,8. Reball or replace RAM.",
    "808011FC": "RAM dataline fault on Chip 3,4,5,6,7,8. Reball or replace RAM.",
    "808011FD": "RAM dataline fault on Chip 1,3,4,5,6,7,8. Reball or replace RAM.",
    "808011FE": "RAM dataline fault on Chip 2,3,4,5,6,7,8. Reball or replace RAM.",
    "808011FF": "RAM dataline fault on Chip 1,2,3,4,5,6,7,8. Reball or replace RAM.",
    "80801501": "RAM calibration/impedance fault on Chip 1. Replace RAM or reball.",
    "80801502": "RAM calibration/impedance fault on Chip 2. Replace RAM or reball.",
    "80801503": "RAM calibration/impedance fault on Chip 1,2. Replace RAM or reball.",
    "80801504": "RAM calibration/impedance fault on Chip 3. Replace RAM or reball.",
    "80801505": "RAM calibration/impedance fault on Chip 1,3. Replace RAM or reball.",
    "80801506": "RAM calibration/impedance fault on Chip 2,3. Replace RAM or reball.",
    "80801507": "RAM calibration/impedance fault on Chip 1,2,3. Replace RAM or reball.",
    "80801508": "RAM calibration/impedance fault on Chip 4. Replace RAM or reball.",
    "80801509": "RAM calibration/impedance fault on Chip 1,4. Replace RAM or reball.",
    "8080150A": "RAM calibration/impedance fault on Chip 2,4. Replace RAM or reball.",
    "8080150B": "RAM calibration/impedance fault on Chip 1,2,4. Replace RAM or reball.",
    "8080150C": "RAM calibration/impedance fault on Chip 3,4. Replace RAM or reball.",
    "8080150D": "RAM calibration/impedance fault on Chip 1,3,4. Replace RAM or reball.",
    "8080150E": "RAM calibration/impedance fault on Chip 2,3,4. Replace RAM or reball.",
    "8080150F": "RAM calibration/impedance fault on Chip 1,2,3,4. Replace RAM or reball.",
    "80801510": "RAM calibration/impedance fault on Chip 5. Replace RAM or reball.",
    "80801511": "RAM calibration/impedance fault on Chip 1,5. Replace RAM or reball.",
    "80801512": "RAM calibration/impedance fault on Chip 2,5. Replace RAM or reball.",
    "80801513": "RAM calibration/impedance fault on Chip 1,2,5. Replace RAM or reball.",
    "80801514": "RAM calibration/impedance fault on Chip 3,5. Replace RAM or reball.",
    "80801515": "RAM calibration/impedance fault on Chip 1,3,5. Replace RAM or reball.",
    "80801516": "RAM calibration/impedance fault on Chip 2,3,5. Replace RAM or reball.",
    "80801517": "RAM calibration/impedance fault on Chip 1,2,3,5. Replace RAM or reball.",
    "80801518": "RAM calibration/impedance fault on Chip 4,5. Replace RAM or reball.",
    "80801519": "RAM calibration/impedance fault on Chip 1,4,5. Replace RAM or reball.",
    "8080151A": "RAM calibration/impedance fault on Chip 2,4,5. Replace RAM or reball.",
    "8080151B": "RAM calibration/impedance fault on Chip 1,2,4,5. Replace RAM or reball.",
    "8080151C": "RAM calibration/impedance fault on Chip 3,4,5. Replace RAM or reball.",
    "8080151D": "RAM calibration/impedance fault on Chip 1,3,4,5. Replace RAM or reball.",
    "8080151E": "RAM calibration/impedance fault on Chip 2,3,4,5. Replace RAM or reball.",
    "8080151F": "RAM calibration/impedance fault on Chip 1,2,3,4,5. Replace RAM or reball.",
    "80801520": "RAM calibration/impedance fault on Chip 6. Replace RAM or reball.",
    "80801521": "RAM calibration/impedance fault on Chip 1,6. Replace RAM or reball.",
    "80801522": "RAM calibration/impedance fault on Chip 2,6. Replace RAM or reball.",
    "80801523": "RAM calibration/impedance fault on Chip 1,2,6. Replace RAM or reball.",
    "80801524": "RAM calibration/impedance fault on Chip 3,6. Replace RAM or reball.",
    "80801525": "RAM calibration/impedance fault on Chip 1,3,6. Replace RAM or reball.",
    "80801526": "RAM calibration/impedance fault on Chip 2,3,6. Replace RAM or reball.",
    "80801527": "RAM calibration/impedance fault on Chip 1,2,3,6. Replace RAM or reball.",
    "80801528": "RAM calibration/impedance fault on Chip 4,6. Replace RAM or reball.",
    "80801529": "RAM calibration/impedance fault on Chip 1,4,6. Replace RAM or reball.",
    "8080152A": "RAM calibration/impedance fault on Chip 2,4,6. Replace RAM or reball.",
    "8080152B": "RAM calibration/impedance fault on Chip 1,2,4,6. Replace RAM or reball.",
    "8080152C": "RAM calibration/impedance fault on Chip 3,4,6. Replace RAM or reball.",
    "8080152D": "RAM calibration/impedance fault on Chip 1,3,4,6. Replace RAM or reball.",
    "8080152E": "RAM calibration/impedance fault on Chip 2,3,4,6. Replace RAM or reball.",
    "8080152F": "RAM calibration/impedance fault on Chip 1,2,3,4,6. Replace RAM or reball.",
    "80801530": "RAM calibration/impedance fault on Chip 5,6. Replace RAM or reball.",
    "80801531": "RAM calibration/impedance fault on Chip 1,5,6. Replace RAM or reball.",
    "80801532": "RAM calibration/impedance fault on Chip 2,5,6. Replace RAM or reball.",
    "80801533": "RAM calibration/impedance fault on Chip 1,2,5,6. Replace RAM or reball.",
    "80801534": "RAM calibration/impedance fault on Chip 3,5,6. Replace RAM or reball.",
    "80801535": "RAM calibration/impedance fault on Chip 1,3,5,6. Replace RAM or reball.",
    "80801536": "RAM calibration/impedance fault on Chip 2,3,5,6. Replace RAM or reball.",
    "80801537": "RAM calibration/impedance fault on Chip 1,2,3,5,6. Replace RAM or reball.",
    "80801538": "RAM calibration/impedance fault on Chip 4,5,6. Replace RAM or reball.",
    "80801539": "RAM calibration/impedance fault on Chip 1,4,5,6. Replace RAM or reball.",
    "8080153A": "RAM calibration/impedance fault on Chip 2,4,5,6. Replace RAM or reball.",
    "8080153B": "RAM calibration/impedance fault on Chip 1,2,4,5,6. Replace RAM or reball.",
    "8080153C": "RAM calibration/impedance fault on Chip 3,4,5,6. Replace RAM or reball.",
    "8080153D": "RAM calibration/impedance fault on Chip 1,3,4,5,6. Replace RAM or reball.",
    "8080153E": "RAM calibration/impedance fault on Chip 2,3,4,5,6. Replace RAM or reball.",
    "8080153F": "RAM calibration/impedance fault on Chip 1,2,3,4,5,6. Replace RAM or reball.",
    "80801540": "RAM calibration/impedance fault on Chip 7. Replace RAM or reball.",
    "80801541": "RAM calibration/impedance fault on Chip 1,7. Replace RAM or reball.",
    "80801542": "RAM calibration/impedance fault on Chip 2,7. Replace RAM or reball.",
    "80801543": "RAM calibration/impedance fault on Chip 1,2,7. Replace RAM or reball.",
    "80801544": "RAM calibration/impedance fault on Chip 3,7. Replace RAM or reball.",
    "80801545": "RAM calibration/impedance fault on Chip 1,3,7. Replace RAM or reball.",
    "80801546": "RAM calibration/impedance fault on Chip 2,3,7. Replace RAM or reball.",
    "80801547": "RAM calibration/impedance fault on Chip 1,2,3,7. Replace RAM or reball.",
    "80801548": "RAM calibration/impedance fault on Chip 4,7. Replace RAM or reball.",
    "80801549": "RAM calibration/impedance fault on Chip 1,4,7. Replace RAM or reball.",
    "8080154A": "RAM calibration/impedance fault on Chip 2,4,7. Replace RAM or reball.",
    "8080154B": "RAM calibration/impedance fault on Chip 1,2,4,7. Replace RAM or reball.",
    "8080154C": "RAM calibration/impedance fault on Chip 3,4,7. Replace RAM or reball.",
    "8080154D": "RAM calibration/impedance fault on Chip 1,3,4,7. Replace RAM or reball.",
    "8080154E": "RAM calibration/impedance fault on Chip 2,3,4,7. Replace RAM or reball.",
    "8080154F": "RAM calibration/impedance fault on Chip 1,2,3,4,7. Replace RAM or reball.",
    "80801550": "RAM calibration/impedance fault on Chip 5,7. Replace RAM or reball.",
    "80801551": "RAM calibration/impedance fault on Chip 1,5,7. Replace RAM or reball.",
    "80801552": "RAM calibration/impedance fault on Chip 2,5,7. Replace RAM or reball.",
    "80801553": "RAM calibration/impedance fault on Chip 1,2,5,7. Replace RAM or reball.",
    "80801554": "RAM calibration/impedance fault on Chip 3,5,7. Replace RAM or reball.",
    "80801555": "RAM calibration/impedance fault on Chip 1,3,5,7. Replace RAM or reball.",
    "80801556": "RAM calibration/impedance fault on Chip 2,3,5,7. Replace RAM or reball.",
    "80801557": "RAM calibration/impedance fault on Chip 1,2,3,5,7. Replace RAM or reball.",
    "80801558": "RAM calibration/impedance fault on Chip 4,5,7. Replace RAM or reball.",
    "80801559": "RAM calibration/impedance fault on Chip 1,4,5,7. Replace RAM or reball.",
    "8080155A": "RAM calibration/impedance fault on Chip 2,4,5,7. Replace RAM or reball.",
    "8080155B": "RAM calibration/impedance fault on Chip 1,2,4,5,7. Replace RAM or reball.",
    "8080155C": "RAM calibration/impedance fault on Chip 3,4,5,7. Replace RAM or reball.",
    "8080155D": "RAM calibration/impedance fault on Chip 1,3,4,5,7. Replace RAM or reball.",
    "8080155E": "RAM calibration/impedance fault on Chip 2,3,4,5,7. Replace RAM or reball.",
    "8080155F": "RAM calibration/impedance fault on Chip 1,2,3,4,5,7. Replace RAM or reball.",
    "80801560": "RAM calibration/impedance fault on Chip 6,7. Replace RAM or reball.",
    "80801561": "RAM calibration/impedance fault on Chip 1,6,7. Replace RAM or reball.",
    "80801562": "RAM calibration/impedance fault on Chip 2,6,7. Replace RAM or reball.",
    "80801563": "RAM calibration/impedance fault on Chip 1,2,6,7. Replace RAM or reball.",
    "80801564": "RAM calibration/impedance fault on Chip 3,6,7. Replace RAM or reball.",
    "80801565": "RAM calibration/impedance fault on Chip 1,3,6,7. Replace RAM or reball.",
    "80801566": "RAM calibration/impedance fault on Chip 2,3,6,7. Replace RAM or reball.",
    "80801567": "RAM calibration/impedance fault on Chip 1,2,3,6,7. Replace RAM or reball.",
    "80801568": "RAM calibration/impedance fault on Chip 4,6,7. Replace RAM or reball.",
    "80801569": "RAM calibration/impedance fault on Chip 1,4,6,7. Replace RAM or reball.",
    "8080156A": "RAM calibration/impedance fault on Chip 2,4,6,7. Replace RAM or reball.",
    "8080156B": "RAM calibration/impedance fault on Chip 1,2,4,6,7. Replace RAM or reball.",
    "8080156C": "RAM calibration/impedance fault on Chip 3,4,6,7. Replace RAM or reball.",
    "8080156D": "RAM calibration/impedance fault on Chip 1,3,4,6,7. Replace RAM or reball.",
    "8080156E": "RAM calibration/impedance fault on Chip 2,3,4,6,7. Replace RAM or reball.",
    "8080156F": "RAM calibration/impedance fault on Chip 1,2,3,4,6,7. Replace RAM or reball.",
    "80801570": "RAM calibration/impedance fault on Chip 5,6,7. Replace RAM or reball.",
    "80801571": "RAM calibration/impedance fault on Chip 1,5,6,7. Replace RAM or reball.",
    "80801572": "RAM calibration/impedance fault on Chip 2,5,6,7. Replace RAM or reball.",
    "80801573": "RAM calibration/impedance fault on Chip 1,2,5,6,7. Replace RAM or reball.",
    "80801574": "RAM calibration/impedance fault on Chip 3,5,6,7. Replace RAM or reball.",
    "80801575": "RAM calibration/impedance fault on Chip 1,3,5,6,7. Replace RAM or reball.",
    "80801576": "RAM calibration/impedance fault on Chip 2,3,5,6,7. Replace RAM or reball.",
    "80801577": "RAM calibration/impedance fault on Chip 1,2,3,5,6,7. Replace RAM or reball.",
    "80801578": "RAM calibration/impedance fault on Chip 4,5,6,7. Replace RAM or reball.",
    "80801579": "RAM calibration/impedance fault on Chip 1,4,5,6,7. Replace RAM or reball.",
    "8080157A": "RAM calibration/impedance fault on Chip 2,4,5,6,7. Replace RAM or reball.",
    "8080157B": "RAM calibration/impedance fault on Chip 1,2,4,5,6,7. Replace RAM or reball.",
    "8080157C": "RAM calibration/impedance fault on Chip 3,4,5,6,7. Replace RAM or reball.",
    "8080157D": "RAM calibration/impedance fault on Chip 1,3,4,5,6,7. Replace RAM or reball.",
    "8080157E": "RAM calibration/impedance fault on Chip 2,3,4,5,6,7. Replace RAM or reball.",
    "8080157F": "RAM calibration/impedance fault on Chip 1,2,3,4,5,6,7. Replace RAM or reball.",
    "80801580": "RAM calibration/impedance fault on Chip 8. Replace RAM or reball.",
    "80801581": "RAM calibration/impedance fault on Chip 1,8. Replace RAM or reball.",
    "80801582": "RAM calibration/impedance fault on Chip 2,8. Replace RAM or reball.",
    "80801583": "RAM calibration/impedance fault on Chip 1,2,8. Replace RAM or reball.",
    "80801584": "RAM calibration/impedance fault on Chip 3,8. Replace RAM or reball.",
    "80801585": "RAM calibration/impedance fault on Chip 1,3,8. Replace RAM or reball.",
    "80801586": "RAM calibration/impedance fault on Chip 2,3,8. Replace RAM or reball.",
    "80801587": "RAM calibration/impedance fault on Chip 1,2,3,8. Replace RAM or reball.",
    "80801588": "RAM calibration/impedance fault on Chip 4,8. Replace RAM or reball.",
    "80801589": "RAM calibration/impedance fault on Chip 1,4,8. Replace RAM or reball.",
    "8080158A": "RAM calibration/impedance fault on Chip 2,4,8. Replace RAM or reball.",
    "8080158B": "RAM calibration/impedance fault on Chip 1,2,4,8. Replace RAM or reball.",
    "8080158C": "RAM calibration/impedance fault on Chip 3,4,8. Replace RAM or reball.",
    "8080158D": "RAM calibration/impedance fault on Chip 1,3,4,8. Replace RAM or reball.",
    "8080158E": "RAM calibration/impedance fault on Chip 2,3,4,8. Replace RAM or reball.",
    "8080158F": "RAM calibration/impedance fault on Chip 1,2,3,4,8. Replace RAM or reball.",
    "80801590": "RAM calibration/impedance fault on Chip 5,8. Replace RAM or reball.",
    "80801591": "RAM calibration/impedance fault on Chip 1,5,8. Replace RAM or reball.",
    "80801592": "RAM calibration/impedance fault on Chip 2,5,8. Replace RAM or reball.",
    "80801593": "RAM calibration/impedance fault on Chip 1,2,5,8. Replace RAM or reball.",
    "80801594": "RAM calibration/impedance fault on Chip 3,5,8. Replace RAM or reball.",
    "80801595": "RAM calibration/impedance fault on Chip 1,3,5,8. Replace RAM or reball.",
    "80801596": "RAM calibration/impedance fault on Chip 2,3,5,8. Replace RAM or reball.",
    "80801597": "RAM calibration/impedance fault on Chip 1,2,3,5,8. Replace RAM or reball.",
    "80801598": "RAM calibration/impedance fault on Chip 4,5,8. Replace RAM or reball.",
    "80801599": "RAM calibration/impedance fault on Chip 1,4,5,8. Replace RAM or reball.",
    "8080159A": "RAM calibration/impedance fault on Chip 2,4,5,8. Replace RAM or reball.",
    "8080159B": "RAM calibration/impedance fault on Chip 1,2,4,5,8. Replace RAM or reball.",
    "8080159C": "RAM calibration/impedance fault on Chip 3,4,5,8. Replace RAM or reball.",
    "8080159D": "RAM calibration/impedance fault on Chip 1,3,4,5,8. Replace RAM or reball.",
    "8080159E": "RAM calibration/impedance fault on Chip 2,3,4,5,8. Replace RAM or reball.",
    "8080159F": "RAM calibration/impedance fault on Chip 1,2,3,4,5,8. Replace RAM or reball.",
    "808015A0": "RAM calibration/impedance fault on Chip 6,8. Replace RAM or reball.",
    "808015A1": "RAM calibration/impedance fault on Chip 1,6,8. Replace RAM or reball.",
    "808015A2": "RAM calibration/impedance fault on Chip 2,6,8. Replace RAM or reball.",
    "808015A3": "RAM calibration/impedance fault on Chip 1,2,6,8. Replace RAM or reball.",
    "808015A4": "RAM calibration/impedance fault on Chip 3,6,8. Replace RAM or reball.",
    "808015A5": "RAM calibration/impedance fault on Chip 1,3,6,8. Replace RAM or reball.",
    "808015A6": "RAM calibration/impedance fault on Chip 2,3,6,8. Replace RAM or reball.",
    "808015A7": "RAM calibration/impedance fault on Chip 1,2,3,6,8. Replace RAM or reball.",
    "808015A8": "RAM calibration/impedance fault on Chip 4,6,8. Replace RAM or reball.",
    "808015A9": "RAM calibration/impedance fault on Chip 1,4,6,8. Replace RAM or reball.",
    "808015AA": "RAM calibration/impedance fault on Chip 2,4,6,8. Replace RAM or reball.",
    "808015AB": "RAM calibration/impedance fault on Chip 1,2,4,6,8. Replace RAM or reball.",
    "808015AC": "RAM calibration/impedance fault on Chip 3,4,6,8. Replace RAM or reball.",
    "808015AD": "RAM calibration/impedance fault on Chip 1,3,4,6,8. Replace RAM or reball.",
    "808015AE": "RAM calibration/impedance fault on Chip 2,3,4,6,8. Replace RAM or reball.",
    "808015AF": "RAM calibration/impedance fault on Chip 1,2,3,4,6,8. Replace RAM or reball.",
    "808015B0": "RAM calibration/impedance fault on Chip 5,6,8. Replace RAM or reball.",
    "808015B1": "RAM calibration/impedance fault on Chip 1,5,6,8. Replace RAM or reball.",
    "808015B2": "RAM calibration/impedance fault on Chip 2,5,6,8. Replace RAM or reball.",
    "808015B3": "RAM calibration/impedance fault on Chip 1,2,5,6,8. Replace RAM or reball.",
    "808015B4": "RAM calibration/impedance fault on Chip 3,5,6,8. Replace RAM or reball.",
    "808015B5": "RAM calibration/impedance fault on Chip 1,3,5,6,8. Replace RAM or reball.",
    "808015B6": "RAM calibration/impedance fault on Chip 2,3,5,6,8. Replace RAM or reball.",
    "808015B7": "RAM calibration/impedance fault on Chip 1,2,3,5,6,8. Replace RAM or reball.",
    "808015B8": "RAM calibration/impedance fault on Chip 4,5,6,8. Replace RAM or reball.",
    "808015B9": "RAM calibration/impedance fault on Chip 1,4,5,6,8. Replace RAM or reball.",
    "808015BA": "RAM calibration/impedance fault on Chip 2,4,5,6,8. Replace RAM or reball.",
    "808015BB": "RAM calibration/impedance fault on Chip 1,2,4,5,6,8. Replace RAM or reball.",
    "808015BC": "RAM calibration/impedance fault on Chip 3,4,5,6,8. Replace RAM or reball.",
    "808015BD": "RAM calibration/impedance fault on Chip 1,3,4,5,6,8. Replace RAM or reball.",
    "808015BE": "RAM calibration/impedance fault on Chip 2,3,4,5,6,8. Replace RAM or reball.",
    "808015BF": "RAM calibration/impedance fault on Chip 1,2,3,4,5,6,8. Replace RAM or reball.",
    "808015C0": "RAM calibration/impedance fault on Chip 7,8. Replace RAM or reball.",
    "808015C1": "RAM calibration/impedance fault on Chip 1,7,8. Replace RAM or reball.",
    "808015C2": "RAM calibration/impedance fault on Chip 2,7,8. Replace RAM or reball.",
    "808015C3": "RAM calibration/impedance fault on Chip 1,2,7,8. Replace RAM or reball.",
    "808015C4": "RAM calibration/impedance fault on Chip 3,7,8. Replace RAM or reball.",
    "808015C5": "RAM calibration/impedance fault on Chip 1,3,7,8. Replace RAM or reball.",
    "808015C6": "RAM calibration/impedance fault on Chip 2,3,7,8. Replace RAM or reball.",
    "808015C7": "RAM calibration/impedance fault on Chip 1,2,3,7,8. Replace RAM or reball.",
    "808015C8": "RAM calibration/impedance fault on Chip 4,7,8. Replace RAM or reball.",
    "808015C9": "RAM calibration/impedance fault on Chip 1,4,7,8. Replace RAM or reball.",
    "808015CA": "RAM calibration/impedance fault on Chip 2,4,7,8. Replace RAM or reball.",
    "808015CB": "RAM calibration/impedance fault on Chip 1,2,4,7,8. Replace RAM or reball.",
    "808015CC": "RAM calibration/impedance fault on Chip 3,4,7,8. Replace RAM or reball.",
    "808015CD": "RAM calibration/impedance fault on Chip 1,3,4,7,8. Replace RAM or reball.",
    "808015CE": "RAM calibration/impedance fault on Chip 2,3,4,7,8. Replace RAM or reball.",
    "808015CF": "RAM calibration/impedance fault on Chip 1,2,3,4,7,8. Replace RAM or reball.",
    "808015D0": "RAM calibration/impedance fault on Chip 5,7,8. Replace RAM or reball.",
    "808015D1": "RAM calibration/impedance fault on Chip 1,5,7,8. Replace RAM or reball.",
    "808015D2": "RAM calibration/impedance fault on Chip 2,5,7,8. Replace RAM or reball.",
    "808015D3": "RAM calibration/impedance fault on Chip 1,2,5,7,8. Replace RAM or reball.",
    "808015D4": "RAM calibration/impedance fault on Chip 3,5,7,8. Replace RAM or reball.",
    "808015D5": "RAM calibration/impedance fault on Chip 1,3,5,7,8. Replace RAM or reball.",
    "808015D6": "RAM calibration/impedance fault on Chip 2,3,5,7,8. Replace RAM or reball.",
    "808015D7": "RAM calibration/impedance fault on Chip 1,2,3,5,7,8. Replace RAM or reball.",
    "808015D8": "RAM calibration/impedance fault on Chip 4,5,7,8. Replace RAM or reball.",
    "808015D9": "RAM calibration/impedance fault on Chip 1,4,5,7,8. Replace RAM or reball.",
    "808015DA": "RAM calibration/impedance fault on Chip 2,4,5,7,8. Replace RAM or reball.",
    "808015DB": "RAM calibration/impedance fault on Chip 1,2,4,5,7,8. Replace RAM or reball.",
    "808015DC": "RAM calibration/impedance fault on Chip 3,4,5,7,8. Replace RAM or reball.",
    "808015DD": "RAM calibration/impedance fault on Chip 1,3,4,5,7,8. Replace RAM or reball.",
    "808015DE": "RAM calibration/impedance fault on Chip 2,3,4,5,7,8. Replace RAM or reball.",
    "808015DF": "RAM calibration/impedance fault on Chip 1,2,3,4,5,7,8. Replace RAM or reball.",
    "808015E0": "RAM calibration/impedance fault on Chip 6,7,8. Replace RAM or reball.",
    "808015E1": "RAM calibration/impedance fault on Chip 1,6,7,8. Replace RAM or reball.",
    "808015E2": "RAM calibration/impedance fault on Chip 2,6,7,8. Replace RAM or reball.",
    "808015E3": "RAM calibration/impedance fault on Chip 1,2,6,7,8. Replace RAM or reball.",
    "808015E4": "RAM calibration/impedance fault on Chip 3,6,7,8. Replace RAM or reball.",
    "808015E5": "RAM calibration/impedance fault on Chip 1,3,6,7,8. Replace RAM or reball.",
    "808015E6": "RAM calibration/impedance fault on Chip 2,3,6,7,8. Replace RAM or reball.",
    "808015E7": "RAM calibration/impedance fault on Chip 1,2,3,6,7,8. Replace RAM or reball.",
    "808015E8": "RAM calibration/impedance fault on Chip 4,6,7,8. Replace RAM or reball.",
    "808015E9": "RAM calibration/impedance fault on Chip 1,4,6,7,8. Replace RAM or reball.",
    "808015EA": "RAM calibration/impedance fault on Chip 2,4,6,7,8. Replace RAM or reball.",
    "808015EB": "RAM calibration/impedance fault on Chip 1,2,4,6,7,8. Replace RAM or reball.",
    "808015EC": "RAM calibration/impedance fault on Chip 3,4,6,7,8. Replace RAM or reball.",
    "808015ED": "RAM calibration/impedance fault on Chip 1,3,4,6,7,8. Replace RAM or reball.",
    "808015EE": "RAM calibration/impedance fault on Chip 2,3,4,6,7,8. Replace RAM or reball.",
    "808015EF": "RAM calibration/impedance fault on Chip 1,2,3,4,6,7,8. Replace RAM or reball.",
    "808015F0": "RAM calibration/impedance fault on Chip 5,6,7,8. Replace RAM or reball.",
    "808015F1": "RAM calibration/impedance fault on Chip 1,5,6,7,8. Replace RAM or reball.",
    "808015F2": "RAM calibration/impedance fault on Chip 2,5,6,7,8. Replace RAM or reball.",
    "808015F3": "RAM calibration/impedance fault on Chip 1,2,5,6,7,8. Replace RAM or reball.",
    "808015F4": "RAM calibration/impedance fault on Chip 3,5,6,7,8. Replace RAM or reball.",
    "808015F5": "RAM calibration/impedance fault on Chip 1,3,5,6,7,8. Replace RAM or reball.",
    "808015F6": "RAM calibration/impedance fault on Chip 2,3,5,6,7,8. Replace RAM or reball.",
    "808015F7": "RAM calibration/impedance fault on Chip 1,2,3,5,6,7,8. Replace RAM or reball.",
    "808015F8": "RAM calibration/impedance fault on Chip 4,5,6,7,8. Replace RAM or reball.",
    "808015F9": "RAM calibration/impedance fault on Chip 1,4,5,6,7,8. Replace RAM or reball.",
    "808015FA": "RAM calibration/impedance fault on Chip 2,4,5,6,7,8. Replace RAM or reball.",
    "808015FB": "RAM calibration/impedance fault on Chip 1,2,4,5,6,7,8. Replace RAM or reball.",
    "808015FC": "RAM calibration/impedance fault on Chip 3,4,5,6,7,8. Replace RAM or reball.",
    "808015FD": "RAM calibration/impedance fault on Chip 1,3,4,5,6,7,8. Replace RAM or reball.",
    "808015FE": "RAM calibration/impedance fault on Chip 2,3,4,5,6,7,8. Replace RAM or reball.",
    "808015FF": "RAM calibration/impedance fault on Chip 1,2,3,4,5,6,7,8. Replace RAM or reball.",
    "80801601": "RAM hardware fault on Chip 1. Diagnose and repair.",
    "80801602": "RAM hardware fault on Chip 2. Diagnose and repair.",
    "80801603": "RAM hardware fault on Chip 1,2. Diagnose and repair.",
    "80801604": "RAM hardware fault on Chip 3. Diagnose and repair.",
    "80801605": "RAM hardware fault on Chip 1,3. Diagnose and repair.",
    "80801606": "RAM hardware fault on Chip 2,3. Diagnose and repair.",
    "80801607": "RAM hardware fault on Chip 1,2,3. Diagnose and repair.",
    "80801608": "RAM hardware fault on Chip 4. Diagnose and repair.",
    "80801609": "RAM hardware fault on Chip 1,4. Diagnose and repair.",
    "8080160A": "RAM hardware fault on Chip 2,4. Diagnose and repair.",
    "8080160B": "RAM hardware fault on Chip 1,2,4. Diagnose and repair.",
    "8080160C": "RAM hardware fault on Chip 3,4. Diagnose and repair.",
    "8080160D": "RAM hardware fault on Chip 1,3,4. Diagnose and repair.",
    "8080160E": "RAM hardware fault on Chip 2,3,4. Diagnose and repair.",
    "8080160F": "RAM hardware fault on Chip 1,2,3,4. Diagnose and repair.",
    "80801610": "RAM hardware fault on Chip 5. Diagnose and repair.",
    "80801611": "RAM hardware fault on Chip 1,5. Diagnose and repair.",
    "80801612": "RAM hardware fault on Chip 2,5. Diagnose and repair.",
    "80801613": "RAM hardware fault on Chip 1,2,5. Diagnose and repair.",
    "80801614": "RAM hardware fault on Chip 3,5. Diagnose and repair.",
    "80801615": "RAM hardware fault on Chip 1,3,5. Diagnose and repair.",
    "80801616": "RAM hardware fault on Chip 2,3,5. Diagnose and repair.",
    "80801617": "RAM hardware fault on Chip 1,2,3,5. Diagnose and repair.",
    "80801618": "RAM hardware fault on Chip 4,5. Diagnose and repair.",
    "80801619": "RAM hardware fault on Chip 1,4,5. Diagnose and repair.",
    "8080161A": "RAM hardware fault on Chip 2,4,5. Diagnose and repair.",
    "8080161B": "RAM hardware fault on Chip 1,2,4,5. Diagnose and repair.",
    "8080161C": "RAM hardware fault on Chip 3,4,5. Diagnose and repair.",
    "8080161D": "RAM hardware fault on Chip 1,3,4,5. Diagnose and repair.",
    "8080161E": "RAM hardware fault on Chip 2,3,4,5. Diagnose and repair.",
    "8080161F": "RAM hardware fault on Chip 1,2,3,4,5. Diagnose and repair.",
    "80801620": "RAM hardware fault on Chip 6. Diagnose and repair.",
    "80801621": "RAM hardware fault on Chip 1,6. Diagnose and repair.",
    "80801622": "RAM hardware fault on Chip 2,6. Diagnose and repair.",
    "80801623": "RAM hardware fault on Chip 1,2,6. Diagnose and repair.",
    "80801624": "RAM hardware fault on Chip 3,6. Diagnose and repair.",
    "80801625": "RAM hardware fault on Chip 1,3,6. Diagnose and repair.",
    "80801626": "RAM hardware fault on Chip 2,3,6. Diagnose and repair.",
    "80801627": "RAM hardware fault on Chip 1,2,3,6. Diagnose and repair.",
    "80801628": "RAM hardware fault on Chip 4,6. Diagnose and repair.",
    "80801629": "RAM hardware fault on Chip 1,4,6. Diagnose and repair.",
    "8080162A": "RAM hardware fault on Chip 2,4,6. Diagnose and repair.",
    "8080162B": "RAM hardware fault on Chip 1,2,4,6. Diagnose and repair.",
    "8080162C": "RAM hardware fault on Chip 3,4,6. Diagnose and repair.",
    "8080162D": "RAM hardware fault on Chip 1,3,4,6. Diagnose and repair.",
    "8080162E": "RAM hardware fault on Chip 2,3,4,6. Diagnose and repair.",
    "8080162F": "RAM hardware fault on Chip 1,2,3,4,6. Diagnose and repair.",
    "80801630": "RAM hardware fault on Chip 5,6. Diagnose and repair.",
    "80801631": "RAM hardware fault on Chip 1,5,6. Diagnose and repair.",
    "80801632": "RAM hardware fault on Chip 2,5,6. Diagnose and repair.",
    "80801633": "RAM hardware fault on Chip 1,2,5,6. Diagnose and repair.",
    "80801634": "RAM hardware fault on Chip 3,5,6. Diagnose and repair.",
    "80801635": "RAM hardware fault on Chip 1,3,5,6. Diagnose and repair.",
    "80801636": "RAM hardware fault on Chip 2,3,5,6. Diagnose and repair.",
    "80801637": "RAM hardware fault on Chip 1,2,3,5,6. Diagnose and repair.",
    "80801638": "RAM hardware fault on Chip 4,5,6. Diagnose and repair.",
    "80801639": "RAM hardware fault on Chip 1,4,5,6. Diagnose and repair.",
    "8080163A": "RAM hardware fault on Chip 2,4,5,6. Diagnose and repair.",
    "8080163B": "RAM hardware fault on Chip 1,2,4,5,6. Diagnose and repair.",
    "8080163C": "RAM hardware fault on Chip 3,4,5,6. Diagnose and repair.",
    "8080163D": "RAM hardware fault on Chip 1,3,4,5,6. Diagnose and repair.",
    "8080163E": "RAM hardware fault on Chip 2,3,4,5,6. Diagnose and repair.",
    "8080163F": "RAM hardware fault on Chip 1,2,3,4,5,6. Diagnose and repair.",
    "80801640": "RAM hardware fault on Chip 7. Diagnose and repair.",
    "80801641": "RAM hardware fault on Chip 1,7. Diagnose and repair.",
    "80801642": "RAM hardware fault on Chip 2,7. Diagnose and repair.",
    "80801643": "RAM hardware fault on Chip 1,2,7. Diagnose and repair.",
    "80801644": "RAM hardware fault on Chip 3,7. Diagnose and repair.",
    "80801645": "RAM hardware fault on Chip 1,3,7. Diagnose and repair.",
    "80801646": "RAM hardware fault on Chip 2,3,7. Diagnose and repair.",
    "80801647": "RAM hardware fault on Chip 1,2,3,7. Diagnose and repair.",
    "80801648": "RAM hardware fault on Chip 4,7. Diagnose and repair.",
    "80801649": "RAM hardware fault on Chip 1,4,7. Diagnose and repair.",
    "8080164A": "RAM hardware fault on Chip 2,4,7. Diagnose and repair.",
    "8080164B": "RAM hardware fault on Chip 1,2,4,7. Diagnose and repair.",
    "8080164C": "RAM hardware fault on Chip 3,4,7. Diagnose and repair.",
    "8080164D": "RAM hardware fault on Chip 1,3,4,7. Diagnose and repair.",
    "8080164E": "RAM hardware fault on Chip 2,3,4,7. Diagnose and repair.",
    "8080164F": "RAM hardware fault on Chip 1,2,3,4,7. Diagnose and repair.",
    "80801650": "RAM hardware fault on Chip 5,7. Diagnose and repair.",
    "80801651": "RAM hardware fault on Chip 1,5,7. Diagnose and repair.",
    "80801652": "RAM hardware fault on Chip 2,5,7. Diagnose and repair.",
    "80801653": "RAM hardware fault on Chip 1,2,5,7. Diagnose and repair.",
    "80801654": "RAM hardware fault on Chip 3,5,7. Diagnose and repair.",
    "80801655": "RAM hardware fault on Chip 1,3,5,7. Diagnose and repair.",
    "80801656": "RAM hardware fault on Chip 2,3,5,7. Diagnose and repair.",
    "80801657": "RAM hardware fault on Chip 1,2,3,5,7. Diagnose and repair.",
    "80801658": "RAM hardware fault on Chip 4,5,7. Diagnose and repair.",
    "80801659": "RAM hardware fault on Chip 1,4,5,7. Diagnose and repair.",
    "8080165A": "RAM hardware fault on Chip 2,4,5,7. Diagnose and repair.",
    "8080165B": "RAM hardware fault on Chip 1,2,4,5,7. Diagnose and repair.",
    "8080165C": "RAM hardware fault on Chip 3,4,5,7. Diagnose and repair.",
    "8080165D": "RAM hardware fault on Chip 1,3,4,5,7. Diagnose and repair.",
    "8080165E": "RAM hardware fault on Chip 2,3,4,5,7. Diagnose and repair.",
    "8080165F": "RAM hardware fault on Chip 1,2,3,4,5,7. Diagnose and repair.",
    "80801660": "RAM hardware fault on Chip 6,7. Diagnose and repair.",
    "80801661": "RAM hardware fault on Chip 1,6,7. Diagnose and repair.",
    "80801662": "RAM hardware fault on Chip 2,6,7. Diagnose and repair.",
    "80801663": "RAM hardware fault on Chip 1,2,6,7. Diagnose and repair.",
    "80801664": "RAM hardware fault on Chip 3,6,7. Diagnose and repair.",
    "80801665": "RAM hardware fault on Chip 1,3,6,7. Diagnose and repair.",
    "80801666": "RAM hardware fault on Chip 2,3,6,7. Diagnose and repair.",
    "80801667": "RAM hardware fault on Chip 1,2,3,6,7. Diagnose and repair.",
    "80801668": "RAM hardware fault on Chip 4,6,7. Diagnose and repair.",
    "80801669": "RAM hardware fault on Chip 1,4,6,7. Diagnose and repair.",
    "8080166A": "RAM hardware fault on Chip 2,4,6,7. Diagnose and repair.",
    "8080166B": "RAM hardware fault on Chip 1,2,4,6,7. Diagnose and repair.",
    "8080166C": "RAM hardware fault on Chip 3,4,6,7. Diagnose and repair.",
    "8080166D": "RAM hardware fault on Chip 1,3,4,6,7. Diagnose and repair.",
    "8080166E": "RAM hardware fault on Chip 2,3,4,6,7. Diagnose and repair.",
    "8080166F": "RAM hardware fault on Chip 1,2,3,4,6,7. Diagnose and repair.",
    "80801670": "RAM hardware fault on Chip 5,6,7. Diagnose and repair.",
    "80801671": "RAM hardware fault on Chip 1,5,6,7. Diagnose and repair.",
    "80801672": "RAM hardware fault on Chip 2,5,6,7. Diagnose and repair.",
    "80801673": "RAM hardware fault on Chip 1,2,5,6,7. Diagnose and repair.",
    "80801674": "RAM hardware fault on Chip 3,5,6,7. Diagnose and repair.",
    "80801675": "RAM hardware fault on Chip 1,3,5,6,7. Diagnose and repair.",
    "80801676": "RAM hardware fault on Chip 2,3,5,6,7. Diagnose and repair.",
    "80801677": "RAM hardware fault on Chip 1,2,3,5,6,7. Diagnose and repair.",
    "80801678": "RAM hardware fault on Chip 4,5,6,7. Diagnose and repair.",
    "80801679": "RAM hardware fault on Chip 1,4,5,6,7. Diagnose and repair.",
    "8080167A": "RAM hardware fault on Chip 2,4,5,6,7. Diagnose and repair.",
    "8080167B": "RAM hardware fault on Chip 1,2,4,5,6,7. Diagnose and repair.",
    "8080167C": "RAM hardware fault on Chip 3,4,5,6,7. Diagnose and repair.",
    "8080167D": "RAM hardware fault on Chip 1,3,4,5,6,7. Diagnose and repair.",
    "8080167E": "RAM hardware fault on Chip 2,3,4,5,6,7. Diagnose and repair.",
    "8080167F": "RAM hardware fault on Chip 1,2,3,4,5,6,7. Diagnose and repair.",
    "80801680": "RAM hardware fault on Chip 8. Diagnose and repair.",
    "80801681": "RAM hardware fault on Chip 1,8. Diagnose and repair.",
    "80801682": "RAM hardware fault on Chip 2,8. Diagnose and repair.",
    "80801683": "RAM hardware fault on Chip 1,2,8. Diagnose and repair.",
    "80801684": "RAM hardware fault on Chip 3,8. Diagnose and repair.",
    "80801685": "RAM hardware fault on Chip 1,3,8. Diagnose and repair.",
    "80801686": "RAM hardware fault on Chip 2,3,8. Diagnose and repair.",
    "80801687": "RAM hardware fault on Chip 1,2,3,8. Diagnose and repair.",
    "80801688": "RAM hardware fault on Chip 4,8. Diagnose and repair.",
    "80801689": "RAM hardware fault on Chip 1,4,8. Diagnose and repair.",
    "8080168A": "RAM hardware fault on Chip 2,4,8. Diagnose and repair.",
    "8080168B": "RAM hardware fault on Chip 1,2,4,8. Diagnose and repair.",
    "8080168C": "RAM hardware fault on Chip 3,4,8. Diagnose and repair.",
    "8080168D": "RAM hardware fault on Chip 1,3,4,8. Diagnose and repair.",
    "8080168E": "RAM hardware fault on Chip 2,3,4,8. Diagnose and repair.",
    "8080168F": "RAM hardware fault on Chip 1,2,3,4,8. Diagnose and repair.",
    "80801690": "RAM hardware fault on Chip 5,8. Diagnose and repair.",
    "80801691": "RAM hardware fault on Chip 1,5,8. Diagnose and repair.",
    "80801692": "RAM hardware fault on Chip 2,5,8. Diagnose and repair.",
    "80801693": "RAM hardware fault on Chip 1,2,5,8. Diagnose and repair.",
    "80801694": "RAM hardware fault on Chip 3,5,8. Diagnose and repair.",
    "80801695": "RAM hardware fault on Chip 1,3,5,8. Diagnose and repair.",
    "80801696": "RAM hardware fault on Chip 2,3,5,8. Diagnose and repair.",
    "80801697": "RAM hardware fault on Chip 1,2,3,5,8. Diagnose and repair.",
    "80801698": "RAM hardware fault on Chip 4,5,8. Diagnose and repair.",
    "80801699": "RAM hardware fault on Chip 1,4,5,8. Diagnose and repair.",
    "8080169A": "RAM hardware fault on Chip 2,4,5,8. Diagnose and repair.",
    "8080169B": "RAM hardware fault on Chip 1,2,4,5,8. Diagnose and repair.",
    "8080169C": "RAM hardware fault on Chip 3,4,5,8. Diagnose and repair.",
    "8080169D": "RAM hardware fault on Chip 1,3,4,5,8. Diagnose and repair.",
    "8080169E": "RAM hardware fault on Chip 2,3,4,5,8. Diagnose and repair.",
    "8080169F": "RAM hardware fault on Chip 1,2,3,4,5,8. Diagnose and repair.",
    "808016A0": "RAM hardware fault on Chip 6,8. Diagnose and repair.",
    "808016A1": "RAM hardware fault on Chip 1,6,8. Diagnose and repair.",
    "808016A2": "RAM hardware fault on Chip 2,6,8. Diagnose and repair.",
    "808016A3": "RAM hardware fault on Chip 1,2,6,8. Diagnose and repair.",
    "808016A4": "RAM hardware fault on Chip 3,6,8. Diagnose and repair.",
    "808016A5": "RAM hardware fault on Chip 1,3,6,8. Diagnose and repair.",
    "808016A6": "RAM hardware fault on Chip 2,3,6,8. Diagnose and repair.",
    "808016A7": "RAM hardware fault on Chip 1,2,3,6,8. Diagnose and repair.",
    "808016A8": "RAM hardware fault on Chip 4,6,8. Diagnose and repair.",
    "808016A9": "RAM hardware fault on Chip 1,4,6,8. Diagnose and repair.",
    "808016AA": "RAM hardware fault on Chip 2,4,6,8. Diagnose and repair.",
    "808016AB": "RAM hardware fault on Chip 1,2,4,6,8. Diagnose and repair.",
    "808016AC": "RAM hardware fault on Chip 3,4,6,8. Diagnose and repair.",
    "808016AD": "RAM hardware fault on Chip 1,3,4,6,8. Diagnose and repair.",
    "808016AE": "RAM hardware fault on Chip 2,3,4,6,8. Diagnose and repair.",
    "808016AF": "RAM hardware fault on Chip 1,2,3,4,6,8. Diagnose and repair.",
    "808016B0": "RAM hardware fault on Chip 5,6,8. Diagnose and repair.",
    "808016B1": "RAM hardware fault on Chip 1,5,6,8. Diagnose and repair.",
    "808016B2": "RAM hardware fault on Chip 2,5,6,8. Diagnose and repair.",
    "808016B3": "RAM hardware fault on Chip 1,2,5,6,8. Diagnose and repair.",
    "808016B4": "RAM hardware fault on Chip 3,5,6,8. Diagnose and repair.",
    "808016B5": "RAM hardware fault on Chip 1,3,5,6,8. Diagnose and repair.",
    "808016B6": "RAM hardware fault on Chip 2,3,5,6,8. Diagnose and repair.",
    "808016B7": "RAM hardware fault on Chip 1,2,3,5,6,8. Diagnose and repair.",
    "808016B8": "RAM hardware fault on Chip 4,5,6,8. Diagnose and repair.",
    "808016B9": "RAM hardware fault on Chip 1,4,5,6,8. Diagnose and repair.",
    "808016BA": "RAM hardware fault on Chip 2,4,5,6,8. Diagnose and repair.",
    "808016BB": "RAM hardware fault on Chip 1,2,4,5,6,8. Diagnose and repair.",
    "808016BC": "RAM hardware fault on Chip 3,4,5,6,8. Diagnose and repair.",
    "808016BD": "RAM hardware fault on Chip 1,3,4,5,6,8. Diagnose and repair.",
    "808016BE": "RAM hardware fault on Chip 2,3,4,5,6,8. Diagnose and repair.",
    "808016BF": "RAM hardware fault on Chip 1,2,3,4,5,6,8. Diagnose and repair.",
    "808016C0": "RAM hardware fault on Chip 7,8. Diagnose and repair.",
    "808016C1": "RAM hardware fault on Chip 1,7,8. Diagnose and repair.",
    "808016C2": "RAM hardware fault on Chip 2,7,8. Diagnose and repair.",
    "808016C3": "RAM hardware fault on Chip 1,2,7,8. Diagnose and repair.",
    "808016C4": "RAM hardware fault on Chip 3,7,8. Diagnose and repair.",
    "808016C5": "RAM hardware fault on Chip 1,3,7,8. Diagnose and repair.",
    "808016C6": "RAM hardware fault on Chip 2,3,7,8. Diagnose and repair.",
    "808016C7": "RAM hardware fault on Chip 1,2,3,7,8. Diagnose and repair.",
    "808016C8": "RAM hardware fault on Chip 4,7,8. Diagnose and repair.",
    "808016C9": "RAM hardware fault on Chip 1,4,7,8. Diagnose and repair.",
    "808016CA": "RAM hardware fault on Chip 2,4,7,8. Diagnose and repair.",
    "808016CB": "RAM hardware fault on Chip 1,2,4,7,8. Diagnose and repair.",
    "808016CC": "RAM hardware fault on Chip 3,4,7,8. Diagnose and repair.",
    "808016CD": "RAM hardware fault on Chip 1,3,4,7,8. Diagnose and repair.",
    "808016CE": "RAM hardware fault on Chip 2,3,4,7,8. Diagnose and repair.",
    "808016CF": "RAM hardware fault on Chip 1,2,3,4,7,8. Diagnose and repair.",
    "808016D0": "RAM hardware fault on Chip 5,7,8. Diagnose and repair.",
    "808016D1": "RAM hardware fault on Chip 1,5,7,8. Diagnose and repair.",
    "808016D2": "RAM hardware fault on Chip 2,5,7,8. Diagnose and repair.",
    "808016D3": "RAM hardware fault on Chip 1,2,5,7,8. Diagnose and repair.",
    "808016D4": "RAM hardware fault on Chip 3,5,7,8. Diagnose and repair.",
    "808016D5": "RAM hardware fault on Chip 1,3,5,7,8. Diagnose and repair.",
    "808016D6": "RAM hardware fault on Chip 2,3,5,7,8. Diagnose and repair.",
    "808016D7": "RAM hardware fault on Chip 1,2,3,5,7,8. Diagnose and repair.",
    "808016D8": "RAM hardware fault on Chip 4,5,7,8. Diagnose and repair.",
    "808016D9": "RAM hardware fault on Chip 1,4,5,7,8. Diagnose and repair.",
    "808016DA": "RAM hardware fault on Chip 2,4,5,7,8. Diagnose and repair.",
    "808016DB": "RAM hardware fault on Chip 1,2,4,5,7,8. Diagnose and repair.",
    "808016DC": "RAM hardware fault on Chip 3,4,5,7,8. Diagnose and repair.",
    "808016DD": "RAM hardware fault on Chip 1,3,4,5,7,8. Diagnose and repair.",
    "808016DE": "RAM hardware fault on Chip 2,3,4,5,7,8. Diagnose and repair.",
    "808016DF": "RAM hardware fault on Chip 1,2,3,4,5,7,8. Diagnose and repair.",
    "808016E0": "RAM hardware fault on Chip 6,7,8. Diagnose and repair.",
    "808016E1": "RAM hardware fault on Chip 1,6,7,8. Diagnose and repair.",
    "808016E2": "RAM hardware fault on Chip 2,6,7,8. Diagnose and repair.",
    "808016E3": "RAM hardware fault on Chip 1,2,6,7,8. Diagnose and repair.",
    "808016E4": "RAM hardware fault on Chip 3,6,7,8. Diagnose and repair.",
    "808016E5": "RAM hardware fault on Chip 1,3,6,7,8. Diagnose and repair.",
    "808016E6": "RAM hardware fault on Chip 2,3,6,7,8. Diagnose and repair.",
    "808016E7": "RAM hardware fault on Chip 1,2,3,6,7,8. Diagnose and repair.",
    "808016E8": "RAM hardware fault on Chip 4,6,7,8. Diagnose and repair.",
    "808016E9": "RAM hardware fault on Chip 1,4,6,7,8. Diagnose and repair.",
    "808016EA": "RAM hardware fault on Chip 2,4,6,7,8. Diagnose and repair.",
    "808016EB": "RAM hardware fault on Chip 1,2,4,6,7,8. Diagnose and repair.",
    "808016EC": "RAM hardware fault on Chip 3,4,6,7,8. Diagnose and repair.",
    "808016ED": "RAM hardware fault on Chip 1,3,4,6,7,8. Diagnose and repair.",
    "808016EE": "RAM hardware fault on Chip 2,3,4,6,7,8. Diagnose and repair.",
    "808016EF": "RAM hardware fault on Chip 1,2,3,4,6,7,8. Diagnose and repair.",
    "808016F0": "RAM hardware fault on Chip 5,6,7,8. Diagnose and repair.",
    "808016F1": "RAM hardware fault on Chip 1,5,6,7,8. Diagnose and repair.",
    "808016F2": "RAM hardware fault on Chip 2,5,6,7,8. Diagnose and repair.",
    "808016F3": "RAM hardware fault on Chip 1,2,5,6,7,8. Diagnose and repair.",
    "808016F4": "RAM hardware fault on Chip 3,5,6,7,8. Diagnose and repair.",
    "808016F5": "RAM hardware fault on Chip 1,3,5,6,7,8. Diagnose and repair.",
    "808016F6": "RAM hardware fault on Chip 2,3,5,6,7,8. Diagnose and repair.",
    "808016F7": "RAM hardware fault on Chip 1,2,3,5,6,7,8. Diagnose and repair.",
    "808016F8": "RAM hardware fault on Chip 4,5,6,7,8. Diagnose and repair.",
    "808016F9": "RAM hardware fault on Chip 1,4,5,6,7,8. Diagnose and repair.",
    "808016FA": "RAM hardware fault on Chip 2,4,5,6,7,8. Diagnose and repair.",
    "808016FB": "RAM hardware fault on Chip 1,2,4,5,6,7,8. Diagnose and repair.",
    "808016FC": "RAM hardware fault on Chip 3,4,5,6,7,8. Diagnose and repair.",
    "808016FD": "RAM hardware fault on Chip 1,3,4,5,6,7,8. Diagnose and repair.",
    "808016FE": "RAM hardware fault on Chip 2,3,4,5,6,7,8. Diagnose and repair.",
    "808016FF": "RAM hardware fault on Chip 1,2,3,4,5,6,7,8. Diagnose and repair.",
    "80801F12": "RAM hardware fault on Chip. Diagnose and repair.",
}
SEVERITY_COLORS = {
    "critical": "#e74c3c",
    "warning":  "#f39c12",
    "info":     "#3498db",
    "unknown":  "#95a5a6",
}


LANG_FILE = os.path.expanduser("~/.ps5uart/lang.txt")

def load_lang():
    try:
        with open(LANG_FILE) as f:
            l = f.read().strip()
            return l if l in ("sr", "en") else "sr"
    except Exception:
        return "sr"

def save_lang(lang):
    try:
        ensure_dirs()
        with open(LANG_FILE, "w") as f:
            f.write(lang)
    except Exception:
        pass
def ensure_dirs():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def code_severity(code):
    c = code.strip().upper().lstrip("0")
    if not c:
        return "unknown"
    first = c[0]
    if first in ("8", "B"):
        return "warning"
    if first in ("C", "F"):
        return "critical"
    return "unknown"

def _parse_xml_to_dict(path):
    """Parsira ps5.xml i vraca dict {KOD: opis}."""
    import xml.etree.ElementTree as ET
    db = {}
    try:
        tree = ET.parse(path)
        for item in tree.getroot().findall("errorCode"):
            code = (item.findtext("ErrorCode") or "").strip().upper()
            desc = (item.findtext("Description") or "").strip()
            if code and desc:
                db[code] = desc
    except Exception:
        pass
    return db

def load_local_db():
    db = dict(BUILTIN_CODES)
    # Uvek ucitaj lokalni ps5.xml kao bazu (ako postoji)
    xml_path = _local_xml_path()
    if os.path.exists(xml_path):
        xml_db = _parse_xml_to_dict(xml_path)
        if xml_db:
            db.update(xml_db)
    # JSON kes (preuzet online) ima prednost nad XML-om
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH) as f:
                cached = json.load(f)
            if cached:
                db.update(cached)
        except Exception:
            pass
    return db

def save_local_db(data):
    ensure_dirs()
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

def fetch_online_db():
    """Preuzima ps5.xml sa servisport.rs i vraca (dict, success)."""
    try:
        import xml.etree.ElementTree as ET
        r = requests.get(DB_URL, timeout=10)
        if r.status_code == 200:
            root = ET.fromstring(r.text)
            db = {}
            for item in root.findall("errorCode"):
                code = (item.findtext("ErrorCode") or "").strip().upper()
                desc = (item.findtext("Description") or "").strip()
                if code and desc:
                    db[code] = desc
            if db:
                save_local_db(db)
                return db, True
    except Exception:
        pass
    return None, False

def lookup_code(raw_code, db):
    """Vraca (normalized_code, description, severity)"""
    variants = []
    c = raw_code.strip().upper()
    variants.append(c.lstrip("0X"))
    variants.append(c)
    try:
        n = int(c.lstrip("0X") or "0", 16)
        variants.append("{:08X}".format(n))
        variants.append("{:X}".format(n))
    except ValueError:
        pass
    for v in variants:
        if v in db:
            return v, db[v], code_severity(v)
        if v in BUILTIN_CODES:
            return v, BUILTIN_CODES[v], code_severity(v)
    norm = variants[2] if len(variants) > 2 else c
    return norm, "Kod nije pronadjen u bazi", "unknown"

def parse_errlog_line(line):
    """Parsira PS5 errlog odgovor, vraca hex kod ili None/'END'"""
    line = line.strip()
    parts = line.split()
    if not parts:
        return None

    if line.startswith("NG") and len(parts) >= 2:
        code = parts[1].split(':')[0].upper()
        # E0000xxx su EMC protokolski status kodovi, ne greske konzole
        if code and not code.startswith("E0000") and code != "00000000":
            try:
                int(code, 16)
                return code
            except ValueError:
                pass
        return None

    if not line.startswith("OK"):
        return None
    if len(parts) < 2:
        return None
    # OK FFFFFFFF[:CS] = kraj loga
    status = parts[1].split(':')[0].upper()
    if "FFFFFFFF" in status:
        return "END"
    if len(parts) < 3:
        return None
    # odredjeni PS5 firmware salje 'OK 00000000 80000009:3A ...' (checksum uz kod)
    code = parts[2].split(':')[0].upper()
    if "FFFFFFFF" in code:
        return "END"
    if not code or code == "00000000":
        return None
    try:
        int(code, 16)
        return code
    except ValueError:
        return None

def log_to_file(code, desc):
    ensure_dirs()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{ts}] {code} | {desc}\n")


class PS5UartApp(Gtk.Window):
    def __init__(self):
        super().__init__(title=tr("app_title", load_lang()) + " – Servis Port")
        self.set_default_size(1020, 740)
        self.set_border_width(0)
        self._apply_css()

        self.lang = load_lang()
        ensure_dirs()
        self.db = load_local_db()
        self.serial_conn = None
        self.monitoring = False
        self.emc_ready = False
        self.read_thread = None
        self.found_codes = []
        self._resp_queue = []
        self._resp_lock = threading.Lock()
        self._log_queue = []
        self._log_lock = threading.Lock()

        self._build_ui()
        self._refresh_ports()
        self._db_status("Lokalna baza ({} kodova)".format(len(self.db)))
        self.db = load_local_db()
        GLib.timeout_add(50, self._flush_log)
        GLib.idle_add(lambda: threading.Thread(target=self._bg_update_db, daemon=True).start())

    def _apply_css(self):
        css = b"""
        window { background-color: #12121f; }
        .hdr { background-color: #1a1a35; padding: 10px 18px; }
        .hdr-title { color: #e94560; font-size: 17px; font-weight: bold; }
        .hdr-sub   { color: #7f8ea3; font-size: 11px; }
        .panel { background-color: #1a1a35; border-radius: 8px;
                 padding: 14px; margin: 5px; }
        .ptitle { color: #e94560; font-size: 12px; font-weight: bold;
                  margin-bottom: 4px; }
        label { color: #dde3ef; }
        .sbar { background-color: #0e0e22; padding: 3px 12px; }
        .slbl { color: #7f8ea3; font-size: 11px; }
        button { background-color: #e94560; color: white; border: none;
                 border-radius: 6px; padding: 7px 14px; font-weight: bold; }
        button:hover { background-color: #c73652; }
        .btn-sec { background-color: #1e3a5f; }
        .btn-sec:hover { background-color: #254e80; }
        .btn-ok  { background-color: #1a6b3c; }
        .btn-ok:hover { background-color: #227a47; }
        .btn-del { background-color: #c0392b; color: white; }
        .btn-del:hover { background-color: #e74c3c; color: white; }
        .code-entry { background-color: #0e1628; color: #e2e8f0;
                      border: 1px solid #e94560; border-radius: 6px;
                      padding: 7px; font-family: monospace; font-size: 13px; }
        .logview { background-color: #0a0a18; color: #7ec8a0;
                   font-family: monospace; font-size: 12px; }
        .logo-btn { background: none; border: none; padding: 2px; }
        .logo-btn:hover { background-color: rgba(233,69,96,0.15); border-radius: 4px; }
        menu { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; }
        menu * { color: #000000; }
        menuitem { color: #000000; padding: 4px 12px; }
        menuitem:hover { background-color: #e94560; color: #ffffff; }
        menuitem label { color: inherit; }
        """
        p = Gtk.CssProvider()
        p.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), p,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _panel(self, title):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.get_style_context().add_class("panel")
        lbl = Gtk.Label(label=title)
        lbl.get_style_context().add_class("ptitle")
        lbl.set_halign(Gtk.Align.START)
        box.pack_start(lbl, False, False, 0)
        return box

    def _build_ui(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(root)

        # Window ikonica
        pb_icon = _logo_pixbuf(LOGO_48_B64, 48)
        if pb_icon:
            self.set_icon(pb_icon)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hdr.get_style_context().add_class("hdr")

        # Logo ikonica (klikabilna)
        pb_small = _logo_pixbuf(LOGO_32_B64, 32)
        if pb_small:
            logo_img = Gtk.Image.new_from_pixbuf(pb_small)
            logo_btn = Gtk.Button()
            logo_btn.set_image(logo_img)
            logo_btn.set_relief(Gtk.ReliefStyle.NONE)
            logo_btn.get_style_context().add_class("logo-btn")
            logo_btn.connect("clicked", lambda _: webbrowser.open("https://servisport.rs"))
            logo_btn.set_tooltip_text("servisport.rs")
            hdr.pack_start(logo_btn, False, False, 8)

        # Naslov i podnaslov
        hdr_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        self.lbl_app_title = Gtk.Label(label=tr("app_title", self.lang))
        self.lbl_app_title.get_style_context().add_class("hdr-title")
        self.lbl_app_title.set_halign(Gtk.Align.START)
        self.lbl_app_sub = Gtk.Label(label=tr("app_subtitle", self.lang))
        self.lbl_app_sub.get_style_context().add_class("hdr-sub")
        self.lbl_app_sub.set_halign(Gtk.Align.START)
        hdr_text.pack_start(self.lbl_app_title, False, False, 0)
        hdr_text.pack_start(self.lbl_app_sub, False, False, 0)
        hdr.pack_start(hdr_text, True, True, 0)

        # Dugme jezik
        self.btn_lang = Gtk.Button(label=tr("lang_toggle", self.lang))
        self.btn_lang.get_style_context().add_class("btn-sec")
        self.btn_lang.connect("clicked", lambda _: self._toggle_lang())
        self.btn_lang.set_margin_end(4)
        self.btn_lang.set_valign(Gtk.Align.CENTER)
        hdr.pack_end(self.btn_lang, False, False, 0)

        # Dugme Uputstvo
        self.btn_help_hdr = Gtk.Button(label=tr("btn_help", self.lang))
        self.btn_help_hdr.get_style_context().add_class("btn-sec")
        self.btn_help_hdr.connect("clicked", lambda _: self._show_help())
        self.btn_help_hdr.set_margin_end(4)
        self.btn_help_hdr.set_valign(Gtk.Align.CENTER)
        hdr.pack_end(self.btn_help_hdr, False, False, 0)

        root.pack_start(hdr, False, False, 0)
        root.pack_start(Gtk.Separator(), False, False, 0)

        # Kontejner koji se rekreira pri promeni jezika
        self._body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.pack_start(self._body, True, True, 0)
        self._root_box = root
        self._rebuild_body()

    def _rebuild_body(self):
        # Ukloni sve staro
        for w in self._body.get_children():
            w.destroy()

        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._body.pack_start(body, True, True, 0)

        # ── LEVA KOLONA ───────────────────────────────────────────────────────
        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left.set_size_request(295, -1)
        body.pack_start(left, False, False, 0)

        # Port
        pp = self._panel(tr("panel_port", self.lang))
        self.port_combo = Gtk.ComboBoxText()
        pp.pack_start(self.port_combo, False, False, 0)

        brow = Gtk.Box(spacing=6)
        brow.pack_start(Gtk.Label(label=tr("baud_label", self.lang)), False, False, 0)
        self.baud_entry = Gtk.Entry()
        self.baud_entry.set_text(str(BAUD_RATE))
        self.baud_entry.set_width_chars(8)
        brow.pack_start(self.baud_entry, True, True, 0)
        pp.pack_start(brow, False, False, 0)

        crow = Gtk.Box(spacing=6)
        self.btn_connect = Gtk.Button(label=tr("btn_connect", self.lang))
        self.btn_connect.connect("clicked", self._on_connect)
        btn_ref = Gtk.Button(label=tr("btn_refresh", self.lang))
        btn_ref.get_style_context().add_class("btn-sec")
        btn_ref.connect("clicked", lambda _: self._refresh_ports())
        btn_pin = Gtk.Button(label=tr("btn_pinout", self.lang))
        btn_pin.get_style_context().add_class("btn-sec")
        btn_pin.connect("clicked", lambda _: self._show_pinout())
        crow.pack_start(self.btn_connect, True, True, 0)
        crow.pack_start(btn_ref, False, False, 0)
        crow.pack_start(btn_pin, False, False, 0)
        pp.pack_start(crow, False, False, 0)

        self.conn_lbl = Gtk.Label(label=tr("conn_off", self.lang))
        self.conn_lbl.set_halign(Gtk.Align.START)
        pp.pack_start(self.conn_lbl, False, False, 0)

        self.emc_lbl = Gtk.Label(label=tr("emc_wait", self.lang))
        self.emc_lbl.set_halign(Gtk.Align.START)
        pp.pack_start(self.emc_lbl, False, False, 0)
        left.pack_start(pp, False, False, 0)

        # PS5 komande
        ap = self._panel(tr("panel_commands", self.lang))

        self.btn_read = Gtk.Button(label=tr("btn_read", self.lang))
        self.btn_read.get_style_context().add_class("btn-ok")
        self.btn_read.connect("clicked", self._on_read_codes)
        self.btn_read.set_sensitive(False)
        ap.pack_start(self.btn_read, False, False, 0)

        self.btn_clear_ps5 = Gtk.Button(label=tr("btn_clear_ps5", self.lang))
        self.btn_clear_ps5.get_style_context().add_class("btn-del")
        self.btn_clear_ps5.connect("clicked", self._on_clear_ps5)
        self.btn_clear_ps5.set_sensitive(False)
        ap.pack_start(self.btn_clear_ps5, False, False, 2)

        ap.pack_start(Gtk.Separator(), False, False, 4)
        lbl_cmd = Gtk.Label(label=tr("custom_cmd_label", self.lang))
        lbl_cmd.set_halign(Gtk.Align.START)
        ap.pack_start(lbl_cmd, False, False, 0)
        cmd_row = Gtk.Box(spacing=6)
        self.cmd_entry = Gtk.ComboBoxText.new_with_entry()
        for cmd in ["errlog 0", "errlog 1", "errlog 2", "errlog 3",
                    "errlog 4", "errlog 5", "errlog clear", "errlog count",
                    "errver"]:
            self.cmd_entry.append_text(cmd)
        entry_widget = self.cmd_entry.get_child()
        entry_widget.set_placeholder_text(tr("search_hint", self.lang))
        entry_widget.get_style_context().add_class("code-entry")
        entry_widget.connect("activate", self._on_send_cmd)
        btn_send = Gtk.Button(label=tr("btn_send", self.lang))
        btn_send.connect("clicked", self._on_send_cmd)
        cmd_row.pack_start(self.cmd_entry, True, True, 0)
        cmd_row.pack_start(btn_send, False, False, 0)
        ap.pack_start(cmd_row, False, False, 0)
        left.pack_start(ap, False, False, 0)

        # Rucna pretraga
        mp = self._panel(tr("panel_search", self.lang))
        self.manual_entry = Gtk.Entry()
        self.manual_entry.set_placeholder_text("npr. 80C00140")
        self.manual_entry.get_style_context().add_class("code-entry")
        self.manual_entry.connect("activate", self._on_manual_search)
        mp.pack_start(self.manual_entry, False, False, 0)
        btn_ms = Gtk.Button(label=tr("btn_search", self.lang))
        btn_ms.connect("clicked", self._on_manual_search)
        mp.pack_start(btn_ms, False, False, 2)
        left.pack_start(mp, False, False, 0)

        # DB
        dp = self._panel(tr("panel_db", self.lang))
        self.db_lbl = Gtk.Label(label=tr("db_local", self.lang, n=len(self.db)) if self.db else tr("db_loading", self.lang))
        self.db_lbl.set_halign(Gtk.Align.START)
        self.db_lbl.set_line_wrap(True)
        dp.pack_start(self.db_lbl, False, False, 0)
        self.btn_upd = Gtk.Button(label=tr("btn_update_db", self.lang))
        self.btn_upd.get_style_context().add_class("btn-sec")
        self.btn_upd.connect("clicked", lambda _: threading.Thread(
            target=self._bg_update_db, daemon=True).start())
        dp.pack_start(self.btn_upd, False, False, 2)
        left.pack_start(dp, False, False, 0)

        # ── DESNA KOLONA ──────────────────────────────────────────────────────
        body.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        body.pack_start(right, True, True, 0)

        # Lista kodova
        rp = self._panel(tr("panel_found", self.lang))
        code_tb = Gtk.Box(spacing=6)
        self.found_count_lbl = Gtk.Label(label=tr("found_count", self.lang, n=0))
        self.found_count_lbl.set_halign(Gtk.Align.START)
        btn_export = Gtk.Button(label=tr("btn_export", self.lang))
        btn_export.get_style_context().add_class("btn-sec")
        btn_export.connect("clicked", self._on_export)
        btn_clr_list = Gtk.Button(label=tr("btn_clear_list", self.lang))
        btn_clr_list.get_style_context().add_class("btn-del")
        btn_clr_list.connect("clicked", self._on_clear_list)
        code_tb.pack_start(self.found_count_lbl, True, True, 0)
        code_tb.pack_end(btn_clr_list, False, False, 0)
        code_tb.pack_end(btn_export, False, False, 0)
        rp.pack_start(code_tb, False, False, 0)

        # TreeView: col0=kod, col1=color(hidden), col2=opis, col3=vreme
        self.code_store = Gtk.ListStore(str, str, str, str)
        tv = Gtk.TreeView(model=self.code_store)
        tv.set_headers_visible(True)
        tv.override_background_color(
            Gtk.StateFlags.NORMAL, Gdk.RGBA(0.039, 0.039, 0.094, 1))

        # Kod kolona sa bojom
        cell_code = Gtk.CellRendererText()
        cell_code.set_property("font", "monospace bold 11")
        col_code = Gtk.TreeViewColumn(tr("col_code", self.lang), cell_code, text=0, foreground=1)
        col_code.set_min_width(130)
        col_code.set_resizable(True)
        tv.append_column(col_code)

        # Opis
        cell_desc = Gtk.CellRendererText()
        cell_desc.set_property("ellipsize", Pango.EllipsizeMode.END)
        col_desc = Gtk.TreeViewColumn(tr("col_desc", self.lang), cell_desc, text=2)
        col_desc.set_expand(True)
        col_desc.set_resizable(True)
        tv.append_column(col_desc)

        # Vreme
        cell_ts = Gtk.CellRendererText()
        col_ts = Gtk.TreeViewColumn(tr("col_time", self.lang), cell_ts, text=3)
        col_ts.set_min_width(75)
        tv.append_column(col_ts)

        tv.connect("row-activated", self._on_row_activated)

        sc_tv = Gtk.ScrolledWindow()
        sc_tv.set_min_content_height(190)
        sc_tv.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sc_tv.add(tv)
        rp.pack_start(sc_tv, True, True, 0)
        right.pack_start(rp, True, True, 0)

        # Detalji
        res_p = self._panel(tr("panel_details", self.lang))
        self.res_code_lbl = Gtk.Label(label="—")
        self.res_code_lbl.set_halign(Gtk.Align.CENTER)
        self.res_sev_lbl = Gtk.Label(label="")
        self.res_sev_lbl.set_halign(Gtk.Align.CENTER)
        self.res_desc_lbl = Gtk.Label(label=tr("details_hint", self.lang))
        self.res_desc_lbl.set_halign(Gtk.Align.CENTER)
        self.res_desc_lbl.set_line_wrap(True)
        self.res_desc_lbl.set_max_width_chars(70)
        res_p.pack_start(self.res_code_lbl, False, False, 2)
        res_p.pack_start(self.res_sev_lbl, False, False, 0)
        res_p.pack_start(Gtk.Separator(), False, False, 4)
        res_p.pack_start(self.res_desc_lbl, False, False, 2)
        right.pack_start(res_p, False, False, 0)

        # Log
        lp = self._panel(tr("panel_log", self.lang))
        sc_log = Gtk.ScrolledWindow()
        sc_log.set_min_content_height(160)
        sc_log.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_cursor_visible(False)
        self.log_view.get_style_context().add_class("logview")
        self.log_view.set_monospace(True)
        self.log_view.override_background_color(
            Gtk.StateFlags.NORMAL, Gdk.RGBA(0.039, 0.039, 0.094, 1))  # #0a0a18
        self.log_view.override_color(
            Gtk.StateFlags.NORMAL, Gdk.RGBA(0.494, 0.784, 0.627, 1))  # #7ec8a0
        self.log_buf = self.log_view.get_buffer()
        sc_log.add(self.log_view)
        lp.pack_start(sc_log, True, True, 0)
        btn_clr_log = Gtk.Button(label=tr("btn_clear_log", self.lang))
        btn_clr_log.get_style_context().add_class("btn-del")
        btn_clr_log.connect("clicked", lambda _: self.log_buf.set_text(""))
        lp.pack_start(btn_clr_log, False, False, 2)
        right.pack_start(lp, True, True, 0)

        # Status bar
        sb = Gtk.Box()
        sb.get_style_context().add_class("sbar")
        self.status_lbl = Gtk.Label(label=tr("status_ready", self.lang))
        self.status_lbl.get_style_context().add_class("slbl")
        self.status_lbl.set_halign(Gtk.Align.START)
        sb.pack_start(self.status_lbl, True, True, 6)
        ts_lbl = Gtk.Label(label=datetime.now().strftime("%d.%m.%Y"))
        ts_lbl.get_style_context().add_class("slbl")
        sb.pack_end(ts_lbl, False, False, 8)
        self._body.pack_end(sb, False, False, 0)

        self.show_all()
        GLib.idle_add(self._refresh_ports)

    # ── Port ──────────────────────────────────────────────────────────────────
    def _refresh_ports(self):
        self.port_combo.remove_all()
        all_ports = serial.tools.list_ports.comports()
        ports = [p for p in all_ports if
                 p.device.startswith("/dev/ttyUSB") or
                 p.device.startswith("/dev/ttyACM") or
                 (p.hwid and "USB" in p.hwid.upper())]
        for p in ports:
            desc = p.description or ""
            label = "{} – {}".format(p.device, desc[:30]) if desc and desc != "n/a" else p.device
            self.port_combo.append_text(label)
        if ports:
            self.port_combo.set_active(0)
            self._log_main(tr("log_port_found", self.lang, n=len(ports)))
        else:
            self.port_combo.append_text(tr("no_devices", self.lang))
            self.port_combo.set_active(0)

    def _on_connect(self, _):
        if self.serial_conn and self.serial_conn.is_open:
            self._disconnect()
            return
        label = self.port_combo.get_active_text() or ""
        if "nema" in label.lower() or not label:
            self._status("Izaberite serijski port.")
            return
        # Izvuci samo putanju (/dev/ttyUSBx) iz labele "device – opis"
        port = label.split(" – ")[0].strip()
        try:
            baud = int(self.baud_entry.get_text())
        except ValueError:
            baud = BAUD_RATE
        try:
            self.serial_conn = serial.Serial(
                port, baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False)
            # RTS i DTR moraju biti LOW da ne bi resetovali adapter
            self.serial_conn.rts = False
            self.serial_conn.dtr = False
            # Ocisti bafer
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()

            self.monitoring = True
            self.emc_ready = False
            self.btn_connect.set_label(tr("btn_disconnect", self.lang))
            self.conn_lbl.set_markup('<span foreground="#2ecc71">{}</span>'.format(tr("status_connected", self.lang, port=port, baud="")))
            self._emc_status(False)
            self._status(tr("status_connected", self.lang, port=port, baud=baud))
            self._log_main(tr("log_connected", self.lang, port=port, baud=baud))

            self.read_thread = threading.Thread(
                target=self._monitor_loop, daemon=True)
            self.read_thread.start()

            # Aktivni wake — posalji Ctrl+E nakon kratke pauze
            # PS5 mozda vec ceka, probamo odmah
            threading.Thread(target=self._active_wake, daemon=True).start()

        except serial.SerialException as e:
            self._status("{}: {}".format(tr("err_serial", self.lang), e))
            self._err_dialog(tr("err_serial", self.lang), str(e))

    @staticmethod
    def _csum(cmd):
        return sum(ord(c) for c in cmd) % 256

    def _active_wake(self):
        """
        Strategija konektovanja:
        1. Odmah posalji probe komandu sa checksum-om — ako je EMC vec aktivan,
           odgovorice OK i necemo morati da cekamo CMD READY.
        2. Paralelno saljemo Ctrl+E za slucaj da PS5 tek startuje.
        3. Ponavljamo dok ne dobijemo odgovor ili ne odustanemo.
        """
        probe = "errlog 0"
        probe_wire = "{}:{:02X}\n".format(probe, self._csum(probe)).encode("ascii")

        for attempt in range(20):
            if not self.monitoring or self.emc_ready:
                return
            time.sleep(1)
            if not self.monitoring or self.emc_ready:
                return
            # Svaki drugi pokusaj: probe komanda (za vec-ukljucenu PS5)
            # Svaki pokusaj: Ctrl+E (za PS5 koja upravo startuje)
            self._send_raw(b"\x05")
            if attempt % 2 == 0:
                time.sleep(0.1)
                self._send_raw(probe_wire)
                GLib.idle_add(self._log_main,
                    "[WAKE] probe errlog 0 (pokusaj {})\n".format(attempt + 1))
            else:
                GLib.idle_add(self._log_main,
                    tr("log_wake", self.lang, n=attempt + 1))

    def _disconnect(self):
        self.monitoring = False
        self.emc_ready = False
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except Exception:
                pass
        self.serial_conn = None
        self.btn_connect.set_label(tr("btn_connect", self.lang))
        self.conn_lbl.set_markup('<span foreground="#95a5a6">{}</span>'.format(tr("conn_off", self.lang)))
        self._emc_status(False)
        self._status(tr("status_disconnected", self.lang))
        self._log_main(tr("log_disconnected", self.lang))

    # ── Monitor loop ──────────────────────────────────────────────────────────
    def _monitor_loop(self):
        while self.monitoring and self.serial_conn and self.serial_conn.is_open:
            try:
                raw = self.serial_conn.readline()
                if raw:
                    line = raw.decode("ascii", errors="replace").strip()
                    if line:
                        with self._resp_lock:
                            self._resp_queue.append(line)
                        GLib.idle_add(self._on_monitor_line, line)
            except serial.SerialException:
                GLib.idle_add(self._disconnect)
                break
            except Exception:
                time.sleep(0.1)

    def _on_monitor_line(self, line):
        self._log_main("[RX] {}\n".format(line))
        line_up = line.upper()
        if any(x in line_up for x in ["UART CMD READY", "CMD READY", "MANU", "[MANU]"]):
            if not self.emc_ready:
                time.sleep(0.1)
                self._send_raw(b"\x05")
                time.sleep(0.2)
                self._emc_status(True)
                self._log_main(tr("log_emc_ready", self.lang))
        if line.startswith("OK") and not self.emc_ready:
            self._emc_status(True)
            self._log_main(tr("log_emc_active", self.lang))
        code = parse_errlog_line(line)
        if code and code != "END":
            self._add_code_to_list(code)
            return
        # skenira sve tokene u liniji — PS5 moze da izbaci kod u bilo kom formatu
        skip = {"00000000", "FFFFFFFF", "DEADBEEF"}
        seen = set()
        for token in re.findall(r'\b([0-9A-Fa-f]{8})\b', line_up):
            if token in skip or token.startswith("E0000") or token in seen:
                continue
            seen.add(token)
            if token in self.db:
                self._add_code_to_list(token)

    def _emc_status(self, ready):
        self.emc_ready = ready
        if ready:
            self.emc_lbl.set_markup('<span foreground="#2ecc71">{}</span>'.format(tr("emc_ready", self.lang)))
            self.btn_read.set_sensitive(True)
            self.btn_clear_ps5.set_sensitive(True)
        else:
            self.emc_lbl.set_markup('<span foreground="#f39c12">{}</span>'.format(tr("emc_wait", self.lang)))
            self.btn_read.set_sensitive(False)
            self.btn_clear_ps5.set_sensitive(False)

    # ── Slanje ────────────────────────────────────────────────────────────────
    def _send_raw(self, data):
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(data)
            except Exception as e:
                self._log_main("[GRESKA] Slanje: {}\n".format(e))

    def _send_cmd(self, cmd):
        if not self.serial_conn or not self.serial_conn.is_open:
            self._status(tr("err_no_port", self.lang))
            return
        cmd = cmd.strip()
        csum = sum(ord(c) for c in cmd) % 256
        wire = "{:s}:{:02X}\n".format(cmd, csum)
        self._send_raw(wire.encode("ascii"))
        self._log_main("[TX] {}\n".format(wire.strip()))

    def _on_send_cmd(self, _):
        cmd = self.cmd_entry.get_child().get_text().strip()
        if cmd:
            self._send_cmd(cmd)
            self.cmd_entry.get_child().set_text("")

    # ── Citanje svih gresaka ──────────────────────────────────────────────────
    def _on_read_codes(self, _):
        if not self.serial_conn or not self.serial_conn.is_open:
            self._status(tr("err_no_port", self.lang))
            return
        self.btn_read.set_sensitive(False)
        self._status("Citam greske sa PS5...")
        self._log_main("[CITANJE] Pokrenuto...\n")
        threading.Thread(target=self._read_codes_thread, daemon=True).start()

    def _read_codes_thread(self):
        # E0000xxx = EMC protokolski status; retry ako PS5 jos nije spremna
        RETRY_CODES = {"E0000001", "E0000002", "E0000003", "E0000004"}
        idx = 0
        found_any = False
        while idx < 32:
            cmd = "errlog {}".format(idx)
            retries = 0
            while retries < 5:
                self._send_cmd(cmd)
                response = self._wait_response(timeout=3.0)
                if response is None:
                    GLib.idle_add(self._log_main,
                        "[TIMEOUT] Nema odgovora na '{}'\n".format(cmd))
                    break
                code = parse_errlog_line(response)
                raw_code = response.split()[1].split(':')[0].upper() if response.startswith("NG") and len(response.split()) >= 2 else ""
                if response.startswith("NG") and raw_code in RETRY_CODES:
                    retries += 1
                    GLib.idle_add(self._log_main,
                        "[RETRY {}/5] {} -> pokusavam ponovo...\n".format(retries, raw_code))
                    time.sleep(1.5)
                    continue
                break
            if response is None:
                break
            code = parse_errlog_line(response)
            if code == "END" or (code is None and "FFFFFFFF" in response.upper()):
                GLib.idle_add(self._log_main, tr("log_read_end", self.lang))
                break
            if code:
                found_any = True
                GLib.idle_add(self._add_code_to_list, code)
            idx += 1

        msg = tr("read_done_msg", self.lang, n=idx) + (tr("read_no_errors", self.lang) if not found_any else "")
        GLib.idle_add(self._status, msg)
        GLib.idle_add(self._log_main, tr("log_read_done", self.lang, msg=msg))
        GLib.idle_add(self.btn_read.set_sensitive, True)

    def _wait_response(self, timeout=3.0):
        """Ceka liniju OK/NG iz _resp_queue."""
        end = time.time() + timeout
        while time.time() < end:
            with self._resp_lock:
                for i, line in enumerate(self._resp_queue):
                    if line.startswith("OK") or line.startswith("NG"):
                        self._resp_queue.pop(i)
                        return line
            time.sleep(0.05)
        return None

    # ── Brisanje gresaka sa PS5 ───────────────────────────────────────────────
    def _on_clear_ps5(self, _):
        dlg = Gtk.Dialog(
            title=tr("dlg_clear_title", self.lang),
            transient_for=self, flags=0)
        dlg.add_buttons(tr("dlg_yes", self.lang), Gtk.ResponseType.YES,
                        tr("dlg_no", self.lang), Gtk.ResponseType.NO)
        box = dlg.get_content_area()
        box.set_spacing(8)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        title_lbl = Gtk.Label()
        title_lbl.set_markup("<b>Obrisi greske sa PS5?</b>")
        title_lbl.set_halign(Gtk.Align.START)
        title_lbl.override_color(Gtk.StateFlags.NORMAL,
            Gdk.RGBA(0, 0, 0, 1))
        body_lbl = Gtk.Label(
            label=tr("dlg_clear_body", self.lang))
        body_lbl.set_halign(Gtk.Align.START)
        body_lbl.set_line_wrap(True)
        body_lbl.override_color(Gtk.StateFlags.NORMAL,
            Gdk.RGBA(0, 0, 0, 1))
        box.pack_start(title_lbl, False, False, 0)
        box.pack_start(body_lbl, False, False, 0)
        dlg.show_all()
        resp = dlg.run()
        dlg.destroy()
        if resp != Gtk.ResponseType.YES:
            return
        self.btn_clear_ps5.set_sensitive(False)
        self._log_main("[BRISANJE] Saljem 'errlog clear'...\n")
        threading.Thread(target=self._clear_thread, daemon=True).start()

    def _clear_thread(self):
        self._send_cmd("errlog clear")
        response = self._wait_response(timeout=5.0)
        if response:
            GLib.idle_add(self._log_main,
                "[BRISANJE] Odgovor: {}\n".format(response))
            if response.startswith("OK"):
                GLib.idle_add(self._status, tr("status_cleared", self.lang))
                GLib.idle_add(self._log_main, tr("log_cleared_ok", self.lang))
            else:
                GLib.idle_add(self._status,
                    "Greska pri brisanju: {}".format(response))
        else:
            GLib.idle_add(self._log_main, "[BRISANJE] Nema odgovora (timeout).\n")
            GLib.idle_add(self._status, "Timeout – nema odgovora od PS5.")
        GLib.idle_add(self.btn_clear_ps5.set_sensitive, True)

    # ── Lista kodova ──────────────────────────────────────────────────────────
    def _add_code_to_list(self, raw_code):
        norm, desc, sev = lookup_code(raw_code, self.db)
        color = SEVERITY_COLORS.get(sev, SEVERITY_COLORS["unknown"])
        ts = datetime.now().strftime("%H:%M:%S")
        self.code_store.append([norm, color, desc, ts])
        self.found_codes.append({"code": norm, "desc": desc, "severity": sev, "time": ts})
        self.found_count_lbl.set_text("{} kodova".format(len(self.found_codes)))
        if len(self.found_codes) == 1:
            self._show_result(norm, desc, sev)
        log_to_file(norm, desc)
        self._status(tr("status_found", self.lang, code=norm, desc=desc[:50]))

    def _on_row_activated(self, tv, path, col):
        it = self.code_store.get_iter(path)
        code  = self.code_store.get_value(it, 0)
        color = self.code_store.get_value(it, 1)
        desc  = self.code_store.get_value(it, 2)
        sev = next((k for k, v in SEVERITY_COLORS.items() if v == color), "unknown")
        self._show_result(code, desc, sev)

    def _on_clear_list(self, _):
        self.code_store.clear()
        self.found_codes.clear()
        self.found_count_lbl.set_text("0 kodova")

    def _on_manual_search(self, _):
        raw = self.manual_entry.get_text().strip()
        if not raw:
            return
        norm, desc, sev = lookup_code(raw, self.db)
        self._show_result(norm, desc, sev)
        self._log_main("[RUCNO] {} -> {}\n".format(norm, desc))

    def _show_result(self, code, desc, sev):
        color = SEVERITY_COLORS.get(sev, SEVERITY_COLORS["unknown"])
        sev_labels = {
            "critical": "KRITICNA GRESKA",
            "warning":  "UPOZORENJE",
            "info":     "INFO",
            "unknown":  "NEPOZNATO",
        }
        self.res_code_lbl.set_markup(
            '<span foreground="{}" font_desc="monospace bold 20">{}</span>'.format(
                color, code))
        self.res_sev_lbl.set_markup(
            '<span foreground="{}" font_desc="bold 12">{}</span>'.format(
                color, sev_labels.get(sev, sev.upper())))
        self.res_desc_lbl.set_text(desc)

    # ── Export ────────────────────────────────────────────────────────────────
    def _on_export(self, _):
        if not self.found_codes:
            self._status(tr("status_no_codes", self.lang))
            return
        dlg = Gtk.FileChooserDialog(
            title="Sacuvaj izvestaj", parent=self,
            action=Gtk.FileChooserAction.SAVE)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dlg.set_current_name("ps5_uart_{}.txt".format(ts))
        if dlg.run() == Gtk.ResponseType.OK:
            path = dlg.get_filename()
            try:
                with open(path, "w") as f:
                    f.write("PS5 UART Dijagnoza\nServis Port Sabac\n")
                    f.write("Datum: {}\n".format(
                        datetime.now().strftime("%d.%m.%Y %H:%M:%S")))
                    f.write("=" * 50 + "\n\n")
                    for e in self.found_codes:
                        f.write("KOD:   {}\nOPIS:  {}\nVREME: {}\n{}\n".format(
                            e["code"], e["desc"], e["time"], "-" * 40))
                self._status("Sacuvano: {}".format(path))
            except Exception as ex:
                self._err_dialog("Greska pri cuvanju", str(ex))
        dlg.destroy()

    # ── DB ────────────────────────────────────────────────────────────────────
    def _bg_update_db(self):
        GLib.idle_add(self._db_status, "Preuzimanje baze...")
        data, ok = fetch_online_db()
        if ok and data:
            self.db = data
            GLib.idle_add(self._db_status, tr("db_online", self.lang, n=len(data)))
            GLib.idle_add(self._log_main,
                "[DB] Baza azurirana: {} kodova\n".format(len(data)))
        else:
            self.db = load_local_db()
            GLib.idle_add(self._db_status, tr("db_offline", self.lang, n=len(self.db)))
            GLib.idle_add(self._log_main, "[DB] Offline baza aktivna.\n")

    def _db_status(self, msg):
        self.db_lbl.set_text(msg)

    def _log_main(self, text):
        ts = datetime.now().strftime("%H:%M:%S")
        with self._log_lock:
            self._log_queue.append("[{}] {}".format(ts, text))

    def _flush_log(self):
        with self._log_lock:
            if not self._log_queue:
                return True
            lines = self._log_queue[:]
            self._log_queue.clear()
        buf = self.log_buf
        it = buf.get_end_iter()
        buf.insert(it, "".join(lines))
        mark = buf.get_insert()
        self.log_view.scroll_mark_onscreen(mark)
        return True  # ponovi timer

    def _status(self, msg):
        GLib.idle_add(self.status_lbl.set_text, msg)

    def _err_dialog(self, title, msg):
        dlg = Gtk.MessageDialog(
            transient_for=self, flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK, text=title)
        dlg.format_secondary_text(msg)
        dlg.run()
        dlg.destroy()

    def _show_pinout(self):
        win = Gtk.Window(title="PS5 UART Pinout")
        win.set_default_size(860, 720)
        win.set_border_width(0)

        pages = [
            ("EDM-010 / EDM-020", self._draw_010),
            ("EDM-030 / EDM-03x", self._draw_030),
            ("EDM-040 / EDM-041 (Slim)", self._draw_040),
            ("Spajanje adaptera", self._draw_wiring),
        ]
        state = {"idx": 0}

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        win.add(root)

        # Gornja navigacija
        nav = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        nav.set_margin_top(10)
        nav.set_margin_bottom(6)
        nav.set_margin_start(16)
        nav.set_margin_end(16)

        btn_prev = Gtk.Button(label="  ◀  ")
        btn_next = Gtk.Button(label="  ▶  ")
        title_lbl = Gtk.Label()
        title_lbl.set_markup('<span font="14" weight="bold">{}</span>'.format(
            pages[0][0]))
        page_lbl = Gtk.Label()
        page_lbl.set_markup('<span font="11" foreground="#7f8ea3">1 / {}</span>'.format(
            len(pages)))

        nav.pack_start(btn_prev, False, False, 0)
        nav.pack_start(Gtk.Box(), True, True, 0)
        nav.pack_start(title_lbl, False, False, 8)
        nav.pack_start(Gtk.Box(), True, True, 0)
        nav.pack_start(page_lbl, False, False, 8)
        nav.pack_start(btn_next, False, False, 0)
        root.pack_start(nav, False, False, 0)
        root.pack_start(Gtk.Separator(), False, False, 0)

        # DrawingArea
        da = Gtk.DrawingArea()
        da.set_vexpand(True)
        root.pack_start(da, True, True, 0)

        def refresh():
            i = state["idx"]
            title_lbl.set_markup(
                '<span font="14" weight="bold">{}</span>'.format(pages[i][0]))
            page_lbl.set_markup(
                '<span font="11" foreground="#7f8ea3">{} / {}</span>'.format(
                    i + 1, len(pages)))
            btn_prev.set_sensitive(i > 0)
            btn_next.set_sensitive(i < len(pages) - 1)
            # Reconnect draw signal
            for hid in getattr(da, "_draw_handlers", []):
                da.disconnect(hid)
            hid = da.connect("draw", pages[i][1])
            da._draw_handlers = [hid]
            da.queue_draw()

        def on_prev(_):
            if state["idx"] > 0:
                state["idx"] -= 1
                refresh()

        def on_next(_):
            if state["idx"] < len(pages) - 1:
                state["idx"] += 1
                refresh()

        # Tastatura: levo/desno strelice
        def on_key(w, event):
            if event.keyval == 65361:  # levo
                on_prev(None)
            elif event.keyval == 65363:  # desno
                on_next(None)

        btn_prev.connect("clicked", on_prev)
        btn_next.connect("clicked", on_next)
        win.connect("key-press-event", on_key)

        refresh()
        win.show_all()

    # ── Cairo boje ────────────────────────────────────────────────────────────
    def _set_tx(self, cr):    cr.set_source_rgb(0.118, 0.620, 0.459)
    def _set_rx(self, cr):    cr.set_source_rgb(0.937, 0.624, 0.153)
    def _set_gnd(self, cr):   cr.set_source_rgb(0.45, 0.45, 0.45)
    def _set_other(self, cr): cr.set_source_rgb(0.2, 0.2, 0.35)
    def _set_bg(self, cr):    cr.set_source_rgb(0.1, 0.1, 0.2)
    def _set_fg(self, cr):    cr.set_source_rgb(0.87, 0.89, 0.94)
    def _set_warn(self, cr):  cr.set_source_rgb(0.937, 0.624, 0.153)

    def _pad(self, cr, cx, cy, r, kind):
        import math
        if kind == "tx":    self._set_tx(cr)
        elif kind == "rx":  self._set_rx(cr)
        elif kind == "gnd": self._set_gnd(cr)
        else:               self._set_other(cr)
        cr.arc(cx, cy, r, 0, 2*math.pi)
        cr.fill()
        cr.set_source_rgb(1, 1, 1)
        cr.arc(cx, cy, r, 0, 2*math.pi)
        cr.set_line_width(1.5 if kind in ("tx","rx","gnd") else 0.8)
        cr.stroke()

    def _label(self, cr, x, y, text, size=12, bold=False):
        import gi
        gi.require_version('Pango', '1.0')
        gi.require_version('PangoCairo', '1.0')
        from gi.repository import Pango, PangoCairo
        cr.save()
        cr.move_to(x, y)
        layout = PangoCairo.create_layout(cr)
        weight = "Bold " if bold else ""
        desc = Pango.FontDescription("Sans {}{}".format(weight, size))
        layout.set_font_description(desc)
        layout.set_text(text, -1)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

    def _draw_bg(self, cr, w, h):
        self._set_bg(cr)
        cr.rectangle(0, 0, w, h)
        cr.fill()

    def _legend(self, cr, x, y):
        import math
        items = [("TX  → RX adaptera", "tx"),
                 ("RX  ← TX adaptera", "rx"),
                 ("GND",               "gnd"),
                 ("ostali padovi",     "other")]
        for i, (txt, kind) in enumerate(items):
            cx = x + i * 200
            self._pad(cr, cx, y, 8, kind)
            self._set_fg(cr)
            cr.move_to(cx + 14, y - 6)
            self._label(cr, cx + 14, y - 7, txt, 11)

    # ── EDM-010 / 020 ─────────────────────────────────────────────────────────
    def _draw_010(self, da, cr):
        w = da.get_allocated_width()
        h = da.get_allocated_height()
        self._draw_bg(cr, w, h)

        # WiFi modul (referentna tacka)
        cr.set_source_rgba(0.15, 0.55, 0.35, 0.3)
        cr.rectangle(100, 60, 200, 120)
        cr.fill()
        cr.set_source_rgba(0.15, 0.55, 0.35, 0.6)
        cr.rectangle(100, 60, 200, 120)
        cr.set_line_width(1)
        cr.stroke()
        self._set_fg(cr)
        self._label(cr, 158, 116, "WiFi modul", 11)

        # 3x3 grid padova ispod WiFi modula
        ox, oy, sp = 110, 220, 44
        grid = [
            ["other", "other", "gnd"],
            ["other", "other", "tx"],
            ["other", "other", "rx"],
        ]
        for row in range(3):
            for col in range(3):
                self._pad(cr, ox + col*sp, oy + row*sp, 14, grid[row][col])

        # Labele u koloni desno, jedna ispod druge
        lx = ox + 3*sp + 30
        ly = oy - 10
        items = [("gnd", "GND"),
                 ("tx",  "TX  →  RX adaptera"),
                 ("rx",  "RX  ←  TX adaptera")]
        for kind, txt in items:
            # Tacka
            if kind == "tx":   self._set_tx(cr)
            elif kind == "rx": self._set_rx(cr)
            else:              self._set_gnd(cr)
            cr.arc(lx - 10, ly + 8, 5, 0, 2*3.14159)
            cr.fill()
            self._set_fg(cr)
            self._label(cr, lx, ly, txt, 12)
            ly += 26

        self._set_warn(cr)
        self._label(cr, 40, h - 52,
            "Padovi pored WiFi modula, desna kolona  |  3.3V logika!", 11)
        self._legend(cr, 40, h - 20)

    # ── EDM-030 / 03x ─────────────────────────────────────────────────────────
    def _draw_030(self, da, cr):
        w = da.get_allocated_width()
        h = da.get_allocated_height()
        self._draw_bg(cr, w, h)

        # Fan konektor
        cr.set_source_rgba(0.1, 0.1, 0.15, 0.8)
        cr.rectangle(110, 60, 80, 70)
        cr.fill()
        cr.set_source_rgba(0.6, 0.6, 0.7, 0.7)
        cr.rectangle(110, 60, 80, 70)
        cr.set_line_width(1.2)
        cr.stroke()
        self._set_fg(cr)
        self._label(cr, 120, 91, "Fan konektor", 10)

        # Red 1: GND, TX, other, other
        oy1, oy2 = 180, 230
        pads1 = ["gnd", "other", "tx", "other"]
        pads2 = ["other", "other", "rx", "other"]
        xs = [110, 154, 198, 242]
        for i, kind in enumerate(pads1):
            self._pad(cr, xs[i], oy1, 14, kind)
        for i, kind in enumerate(pads2):
            self._pad(cr, xs[i], oy2, 14, kind)

        # Labele u koloni desno
        lx = xs[-1] + 40
        ly = oy1 - 10
        items = [("gnd", "GND  (levi pad, red 1)"),
                 ("tx",  "TX  →  RX adaptera"),
                 ("rx",  "RX  ←  TX adaptera")]
        for kind, txt in items:
            if kind == "tx":   self._set_tx(cr)
            elif kind == "rx": self._set_rx(cr)
            else:              self._set_gnd(cr)
            cr.arc(lx - 10, ly + 8, 5, 0, 2*3.14159)
            cr.fill()
            self._set_fg(cr)
            self._label(cr, lx, ly, txt, 12)
            ly += 26

        self._set_warn(cr)
        self._label(cr, 40, h - 52,
            "Padovi ispod fan konektora, u dva reda  |  3.3V logika!", 11)
        self._legend(cr, 40, h - 20)

    # ── EDM-040 / Slim ────────────────────────────────────────────────────────
    def _draw_040(self, da, cr):
        import math
        w = da.get_allocated_width()
        h = da.get_allocated_height()
        self._draw_bg(cr, w, h)

        # Vijak (referentna tacka)
        cr.set_source_rgba(0.7, 0.65, 0.4, 0.6)
        cr.arc(340, 80, 18, 0, 2*math.pi)
        cr.fill()
        cr.set_source_rgba(0.5, 0.45, 0.2, 0.9)
        cr.arc(340, 80, 18, 0, 2*math.pi)
        cr.set_line_width(1)
        cr.stroke()
        cr.arc(340, 80, 8, 0, 2*math.pi)
        cr.set_line_width(0.8)
        cr.stroke()
        self._set_fg(cr)
        self._label(cr, 365, 74, "vijak (montaza)", 10)

        # Red 1: TX, RX, other, other
        oy1, oy2 = 180, 230
        xs = [110, 154, 198, 242]
        pads1 = ["tx", "rx", "other", "other"]
        pads2 = ["other", "gnd", "other", "other"]
        for i, kind in enumerate(pads1):
            self._pad(cr, xs[i], oy1, 14, kind)
        for i, kind in enumerate(pads2):
            self._pad(cr, xs[i], oy2, 14, kind)

        # Labele u koloni desno
        lx = xs[-1] + 40
        ly = oy1 - 10
        items = [("tx",  "TX  →  RX adaptera (levi)"),
                 ("rx",  "RX  ←  TX adaptera"),
                 ("gnd", "GND  (ispod, sredina)")]
        for kind, txt in items:
            if kind == "tx":   self._set_tx(cr)
            elif kind == "rx": self._set_rx(cr)
            else:              self._set_gnd(cr)
            cr.arc(lx - 10, ly + 8, 5, 0, 2*3.14159)
            cr.fill()
            self._set_fg(cr)
            self._label(cr, lx, ly, txt, 12)
            ly += 26

        self._set_warn(cr)
        self._label(cr, 40, h - 52,
            "Fan adapter mora biti pricvrscen vijkom  |  3.3V logika!", 11)
        self._legend(cr, 40, h - 20)

        # ── Dijagram spajanja ─────────────────────────────────────────────────────
    def _draw_wiring(self, da, cr):
        import math
        w = da.get_allocated_width()
        h = da.get_allocated_height()
        self._draw_bg(cr, w, h)

        # PS5 box
        cr.set_source_rgba(0.05, 0.35, 0.65, 0.25)
        cr.rectangle(60, 100, 220, 260)
        cr.fill()
        cr.set_source_rgba(0.05, 0.35, 0.65, 0.7)
        cr.rectangle(60, 100, 220, 260)
        cr.set_line_width(1.5)
        cr.stroke()
        self._set_fg(cr)
        cr.move_to(115, 130)
        self._label(cr, 115, 126, "PS5 konzola", 13, bold=True)

        # Adapter box
        cr.set_source_rgba(0.55, 0.25, 0.05, 0.25)
        cr.rectangle(520, 100, 220, 260)
        cr.fill()
        cr.set_source_rgba(0.55, 0.25, 0.05, 0.7)
        cr.rectangle(520, 100, 220, 260)
        cr.set_line_width(1.5)
        cr.stroke()
        self._set_fg(cr)
        cr.move_to(545, 130)
        self._label(cr, 545, 126, "USB/RS232 adapter", 13, bold=True)

        # Pinovi sa labelama
        pins = [
            (170, "TX", "tx",   "RX", "rx"),
            (230, "RX", "rx",   "TX", "tx"),
            (290, "GND","gnd",  "GND","gnd"),
        ]
        for py, lps5, kps5, ladp, kadp in pins:
            # PS5 pin
            self._pad(cr, 280, py, 12, kps5)
            self._set_fg(cr)
            cr.move_to(155, py - 7)
            self._label(cr, 155, py - 8, lps5, 13, bold=True)

            # Adapter pin
            self._pad(cr, 520, py, 12, kadp)
            cr.move_to(540, py - 7)
            self._label(cr, 540, py - 8, ladp, 13, bold=True)

            # Zica (linija)
            if kps5 == "tx":   self._set_tx(cr)
            elif kps5 == "rx": self._set_rx(cr)
            else:              self._set_gnd(cr)
            cr.set_line_width(2.5)
            cr.move_to(292, py)
            cr.line_to(508, py)
            cr.stroke()

        # Napomena
        self._set_warn(cr)
        cr.move_to(60, 420)
        self._label(cr, 60, 418,
            "TX i RX su uvek ukrsteni!  TX (PS5) ide na RX (adapter) i obrnuto.", 12)
        self._set_fg(cr)
        cr.move_to(60, 448)
        self._label(cr, 60, 446,
            "Baud rate: 115200  |  8N1  |  3.3V TTL logika  (ne 5V!)", 12)

    def _show_help(self):
        win = Gtk.Window(title=tr("help_title", self.lang))
        win.set_default_size(500, 640)
        win.set_border_width(0)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        win.add(outer)

        # Header
        hdr = Gtk.Box()
        hdr.get_style_context().add_class("hdr")
        lbl = Gtk.Label(label=tr("help_title", self.lang))
        lbl.get_style_context().add_class("hdr-title")
        lbl.set_halign(Gtk.Align.START)
        lbl.set_margin_start(16)
        lbl.set_margin_top(10)
        lbl.set_margin_bottom(10)
        hdr.pack_start(lbl, True, True, 0)
        outer.pack_start(hdr, False, False, 0)
        outer.pack_start(Gtk.Separator(), False, False, 0)

        # Tekst
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        tv = Gtk.TextView()
        tv.set_editable(False)
        tv.set_cursor_visible(False)
        tv.set_wrap_mode(Gtk.WrapMode.WORD)
        tv.set_monospace(False)
        tv.set_left_margin(16)
        tv.set_right_margin(16)
        tv.set_top_margin(12)
        tv.set_bottom_margin(12)
        # Bela pozadina, crni tekst
        tv.override_background_color(
            Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
        buf = tv.get_buffer()

        # Tagovi za formatiranje
        tag_bold = buf.create_tag("bold", weight=700,
                                  foreground="#c0392b",
                                  size_points=11)
        tag_norm = buf.create_tag("norm", foreground="#222222",
                                  size_points=10)

        help_text = HELP_TEXTS.get(self.lang, HELP_TEXTS["sr"])
        for line in help_text.strip().split("\n"):
            end = buf.get_end_iter()
            if line.startswith("PS5 UART") or line.startswith("SPAJANJE") or                line.startswith("KORACI") or line.startswith("UART ") or                line.startswith("PINOUT") or line.startswith("RESAVANJE"):
                buf.insert_with_tags(end, line + "\n", tag_bold)
            elif line.startswith("━"):
                buf.insert_with_tags(end, line + "\n", tag_bold)
            else:
                buf.insert_with_tags(end, line + "\n", tag_norm)

        scroll.add(tv)
        outer.pack_start(scroll, True, True, 0)

        # Footer – link
        foot = Gtk.Box()
        foot.set_margin_start(16)
        foot.set_margin_end(16)
        foot.set_margin_top(8)
        foot.set_margin_bottom(8)
        link = Gtk.LinkButton.new_with_label("https://servisport.rs", "servisport.rs")
        foot.pack_start(link, False, False, 0)
        btn_close = Gtk.Button(label=tr("btn_close", self.lang))
        btn_close.get_style_context().add_class("btn-sec")
        btn_close.connect("clicked", lambda _: win.destroy())
        foot.pack_end(btn_close, False, False, 0)
        outer.pack_start(foot, False, False, 0)

        win.show_all()

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "sr" else "sr"
        save_lang(self.lang)
        # Azuriraj header
        self.btn_lang.set_label(tr("lang_toggle", self.lang))
        self.btn_help_hdr.set_label(tr("btn_help", self.lang))
        self.lbl_app_title.set_label(tr("app_title", self.lang))
        self.lbl_app_sub.set_label(tr("app_subtitle", self.lang))
        self.set_title(tr("app_title", self.lang) + " – Servis Port")
        # Rekreira ceo body
        self._rebuild_body()

    def on_delete(self, *_):
        self.monitoring = False
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except Exception:
                pass
        Gtk.main_quit()


if __name__ == "__main__":
    app = PS5UartApp()
    app.connect("delete-event", app.on_delete)
    Gtk.main()
