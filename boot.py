import machine, neopixel
_led = neopixel.NeoPixel(machine.Pin(16), 1)
_led[0] = (0, 0, 0)
_led.write()
