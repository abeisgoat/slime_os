# slime_os

Replace the contents of your PicoVision Micropython filesystem with the files in `src`.

## Issues

This software is experimental and does not work completely, specifically issues include...

* Input is only supported via an i2c keyboard, which is not documented
* Some apps use `display.*` methods directly instead of `sos.graphics.*` so they do not support flipping the display

## Hardware

This project is currently only tested on the [PicoVision](https://collabs.shop/fca3j3). 

I have a few extra of the [keyboard PCBs available for sale](https://abe.today/products/mcp23017-port-expander-for-xrt500-tv-remote) if you are an intrepid hacker.

## License

This software is licensed as MIT.

App icons are from [PiiiXL on Itch.io](https://piiixl.itch.io/mega-1-bit-icons-bundle) and are licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.en)
