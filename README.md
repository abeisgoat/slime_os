# slime_os

Slime OS is an app launcher for the PicoVision. It was originally designed for the [Slimedeck Zero](https://youtu.be/rnwPmoWMGqk), a mini cyberdeck project. However I hope to expand it to other devices and form factors.

## Software

Slime OS runs in a limited 32-color mode with a 400x240 internal resolution which is interlaced up to 800x480. This resolution should scale well on most HDMI displays.

### Setup

1. Flash the [widescreen build](https://github.com/pimoroni/picovision/releases) of the PicoVision firmware to your PicoVision CPU.
2. Use [Thonny](https://thonny.org/) to replace the contents of your PicoVision Micropython filesystem with the files in `src`. 

### Issues

This software is experimental and does not work completely, specifically issues include...

* Input is only supported via an i2c keyboard, which is not documented (hoping to add USB keyboard soon)
* Some apps are upside down due to the Slimedeck having the screen rotated 180 degrees. Newer apps use the `sos.graphics.*` methods which support the `display/flipped` value in `config.py`. Older apps use `self.display.*` and have wild math to rotate everything manually.
* Everything is generally incomplete

## Hardware

Currently this project uses a very specific set of hardware, however I'd like to expand it to support other RP2040 and RP2350 boards in the future. Feel free to do PRs to add more general hardware support.

### Mainboard

This project is currently only tested on the [PicoVision](https://collabs.shop/fca3j3). 

### Keyboard

The (currently) only support keyboard is based off this [XRT500 remote](https://www.amazon.com/dp/B01IOZBNBC/?tag=boosteroven-20). There are a few variants of this same "version" of remote, but I've only used this exact one.

Along with the remote, you will need an [MCP23017](https://www.adafruit.com/product/732) to convert the key matrix to I2C. I have a few extra of the [keyboard PCBs available for sale](https://abe.today/products/mcp23017-port-expander-for-xrt500-tv-remote). You could also pick up an [Adafruit MCP23017 board](https://www.adafruit.com/product/5346) and wire it to the keyboard PCB by hand.

I would like to add more input types in the future.

### Expansion Port

The expansion port used on the Slimedeck is the [5-pin Dk925A-10M](https://cdn.shopify.com/s/files/1/0174/1800/files/DK925A-10M.pdf?v=1643016288) which, as far as I can tell, are only [sold via Pimoroni](https://collabs.shop/knlijz).

The pinout used for an expansion read left to right, with the edge connector facing you is...

> 5V - SDA/TX/CPU:GP0 - SCL/RX/CPU:GP1 - CTRL/GPU:GP29 - GND

A 4.7k resistor should be placed on the PicoVision connecting the GPU's GP29 to GND while the expansion side should place a 4.7k resistor between CTRL (GP29) and 5v.

Although the plan is to eventually support various resistor values for different protocols / speeds, due to a design mistake this is not currently reliable. The PicoVision only has one ADC pin exposed (GPU:GP29) which is used as CTRL, however to reliably determine the value of the expansion resistor we also need a second ADC to act as a VREF (voltage reference) so we can determine the true voltage of our 5v line. As it stands if the 5v line is 5.2v or 4.9v due to load it may shift the value of our expansion voltage divider out of the expected range and the expansion may be incorrectly recognized. This is easily remidied with an external i2c ADC, but it is not currently implemented.

## License

This software is licensed as MIT.

App icons are from [PiiiXL on Itch.io](https://piiixl.itch.io/mega-1-bit-icons-bundle) and are licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.en)
