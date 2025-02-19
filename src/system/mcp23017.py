"""
MicroPython MCP23017 16-bit I/O Expander
https://github.com/mcauser/micropython-mcp23017

MIT License
Copyright (c) 2019 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = '0.1.4'

# register addresses in port=0, bank=1 mode (easier maths to convert)
_MCP_IODIR        = const(0x00) # R/W I/O Direction Register
_MCP_IPOL         = const(0x01) # R/W Input Polarity Port Register
_MCP_GPINTEN      = const(0x02) # R/W Interrupt-on-Change Pins
_MCP_DEFVAL       = const(0x03) # R/W Default Value Register
_MCP_INTCON       = const(0x04) # R/W Interrupt-on-Change Control Register
_MCP_IOCON        = const(0x05) # R/W Configuration Register
_MCP_GPPU         = const(0x06) # R/W Pull-Up Resistor Register
_MCP_INTF         = const(0x07) # R   Interrupt Flag Register (read clears)
_MCP_INTCAP       = const(0x08) # R   Interrupt Captured Value For Port Register
_MCP_GPIO         = const(0x09) # R/W General Purpose I/O Port Register
_MCP_OLAT         = const(0x0a) # R/W Output Latch Register

# Config register (IOCON) bits
_MCP_IOCON_INTPOL = const(2)
_MCP_IOCON_ODR    = const(4)
# _MCP_IOCON_HAEN = const(8) # no used - for spi flavour of this chip
_MCP_IOCON_DISSLW = const(16)
_MCP_IOCON_SEQOP  = const(32)
_MCP_IOCON_MIRROR = const(64)
_MCP_IOCON_BANK   = const(128)


class Port():
    # represents one of the two 8-bit ports
    def __init__(self, port, mcp):
        self._port = port & 1  # 0=PortA, 1=PortB
        self._mcp = mcp

    def _which_reg(self, reg):
        if self._mcp._config & 0x80 == 0x80:
            # bank = 1
            return reg | (self._port << 4)
        else:
            # bank = 0
            return (reg << 1) + self._port

    def _flip_property_bit(self, reg, condition, bit):
        if condition:
            setattr(self, reg, getattr(self, reg) | bit)
        else:
            setattr(self, reg, getattr(self, reg) & ~bit)

    def _read(self, reg):
        return self._mcp._i2c.readfrom_mem(self._mcp._address, self._which_reg(reg), 1)[0]

    def _write(self, reg, val):
        val &= 0xff
        self._mcp._i2c.writeto_mem(self._mcp._address, self._which_reg(reg), bytearray([val]))
        # if writing to the config register, make a copy in mcp so that it knows
        # which bank you're using for subsequent writes
        if reg == _MCP_IOCON:
            self._mcp._config = val

    @property
    def mode(self):
        return self._read(_MCP_IODIR)
    @mode.setter
    def mode(self, val):
        self._write(_MCP_IODIR, val)

    @property
    def input_polarity(self):
        return self._read(_MCP_IPOL)
    @input_polarity.setter
    def input_polarity(self, val):
        self._write(_MCP_IPOL, val)

    @property
    def interrupt_enable(self):
        return self._read(_MCP_GPINTEN)
    @interrupt_enable.setter
    def interrupt_enable(self, val):
        self._write(_MCP_GPINTEN, val)

    @property
    def default_value(self):
        return self._read(_MCP_DEFVAL)
    @default_value.setter
    def default_value(self, val):
        self._write(_MCP_DEFVAL, val)

    @property
    def interrupt_compare_default(self):
        return self._read(_MCP_INTCON)
    @interrupt_compare_default.setter
    def interrupt_compare_default(self, val):
        self._write(_MCP_INTCON, val)

    @property
    def io_config(self):
        return self._read(_MCP_IOCON)
    @io_config.setter
    def io_config(self, val):
        self._write(_MCP_IOCON, val)

    @property
    def pullup(self):
        return self._read(_MCP_GPPU)
    @pullup.setter
    def pullup(self, val):
        self._write(_MCP_GPPU, val)

    # read only
    @property
    def interrupt_flag(self):
        return self._read(_MCP_INTF)

    # read only
    @property
    def interrupt_captured(self):
        return self._read(_MCP_INTCAP)

    @property
    def gpio(self):
        return self._read(_MCP_GPIO)
    @gpio.setter
    def gpio(self, val):
        # writing to this register modifies the OLAT register for pins configured as output
        self._write(_MCP_GPIO, val)

    @property
    def output_latch(self):
        return self._read(_MCP_OLAT)
    @output_latch.setter
    def output_latch(self, val):
        # modifies the output latches on pins configured as outputs
        self._write(_MCP_OLAT, val)


class MCP23017():
    def __init__(self, i2c, address=0x20):
        self._i2c = i2c
        self._address = address
        self._config = 0x00
        self._virtual_pins = {}
        self.init()

    def init(self):
        # error if device not found at i2c addr
        if self._i2c.scan().count(self._address) == 0:
            raise OSError('MCP23017 not found at I2C address {:#x}'.format(self._address))

        self.porta = Port(0, self)
        self.portb = Port(1, self)

        self.io_config = 0x00      # io expander configuration - same on both ports, only need to write once

        # Reset to all inputs with no pull-ups and no inverted polarity.
        self.mode = 0xFFFF                       # in/out direction (0=out, 1=in)
        self.input_polarity = 0x0000             # invert port input polarity (0=normal, 1=invert)
        self.interrupt_enable = 0x0000           # int on change pins (0=disabled, 1=enabled)
        self.default_value = 0x0000              # default value for int on change
        self.interrupt_compare_default = 0x0000  # int on change control (0=compare to prev val, 1=compare to def val)
        self.pullup = 0x0000                     # gpio weak pull up resistor - when configured as input (0=disabled, 1=enabled)
        self.gpio = 0x0000                       # port (0=logic low, 1=logic high)

    def config(self, interrupt_polarity=None, interrupt_open_drain=None, sda_slew=None, sequential_operation=None, interrupt_mirror=None, bank=None):
        io_config = self.porta.io_config

        if interrupt_polarity is not None:
            # configre INT as push-pull
            # 0: Active low
            # 1: Active high
            io_config = self._flip_bit(io_config, interrupt_polarity, _MCP_IOCON_INTPOL)
            if interrupt_polarity:
                # if setting to 1, unset ODR bit - interrupt_open_drain
                interrupt_open_drain = False
        if interrupt_open_drain is not None:
            # configure INT as open drain, overriding interrupt_polarity
            # 0: INTPOL sets the polarity
            # 1: Open drain, INTPOL ignored
            io_config = self._flip_bit(io_config, interrupt_open_drain, _MCP_IOCON_ODR)
        if sda_slew is not None:
            # 0: Slew rate function on SDA pin enabled
            # 1: Slew rate function on SDA pin disabled
            io_config = self._flip_bit(io_config, sda_slew, _MCP_IOCON_DISSLW)
        if sequential_operation is not None:
            # 0: Enabled, address pointer increments
            # 1: Disabled, address pointer fixed
            io_config = self._flip_bit(io_config, sequential_operation, _MCP_IOCON_SEQOP)
        if interrupt_mirror is not None:
            # 0: Independent INTA,INTB pins
            # 1: Internally linked INTA,INTB pins
            io_config = self._flip_bit(io_config, interrupt_mirror, _MCP_IOCON_MIRROR)
        if bank is not None:
            # 0: Registers alternate between A and B ports
            # 1: All port A registers first then all port B
            io_config = self._flip_bit(io_config, bank, _MCP_IOCON_BANK)

        # both ports share the same register, so you only need to write on one
        self.porta.io_config = io_config
        self._config = io_config

    def _flip_bit(self, value, condition, bit):
        if condition:
            value |= bit
        else:
            value &= ~bit
        return value

    def pin(self, pin, mode=None, value=None, pullup=None, polarity=None, interrupt_enable=None, interrupt_compare_default=None, default_value=None):
        assert 0 <= pin <= 15
        port = self.portb if pin // 8 else self.porta
        bit = (1 << (pin % 8))
        if mode is not None:
            # 0: Pin is configured as an output
            # 1: Pin is configured as an input
            port._flip_property_bit('mode', mode & 1, bit)
        if value is not None:
            # 0: Pin is set to logic low
            # 1: Pin is set to logic high
            port._flip_property_bit('gpio', value & 1, bit)
        if pullup is not None:
            # 0: Weak pull-up 100k ohm resistor disabled
            # 1: Weak pull-up 100k ohm resistor enabled
            port._flip_property_bit('pullup', pullup & 1, bit)
        if polarity is not None:
            # 0: GPIO register bit reflects the same logic state of the input pin
            # 1: GPIO register bit reflects the opposite logic state of the input pin
            port._flip_property_bit('input_polarity', polarity & 1, bit)
        if interrupt_enable is not None:
            # 0: Disables GPIO input pin for interrupt-on-change event
            # 1: Enables GPIO input pin for interrupt-on-change event
            port._flip_property_bit('interrupt_enable', interrupt_enable & 1, bit)
        if interrupt_compare_default is not None:
            # 0: Pin value is compared against the previous pin value
            # 1: Pin value is compared against the associated bit in the DEFVAL register
            port._flip_property_bit('interrupt_compare_default', interrupt_compare_default & 1, bit)
        if default_value is not None:
            # 0: Default value for comparison in interrupt, when configured to compare against DEFVAL register
            # 1: Default value for comparison in interrupt, when configured to compare against DEFVAL register
            port._flip_property_bit('default_value', default_value & 1, bit)
        if value is None:
            return port.gpio & bit == bit

    def interrupt_triggered_gpio(self, port):
        # which gpio triggered the interrupt
        # only 1 bit will be set
        port = self.portb if port else self.porta
        return port.interrupt_flag

    def interrupt_captured_gpio(self, port):
        # captured gpio values at time of int
        # reading this will clear the current interrupt
        port = self.portb if port else self.porta
        return port.interrupt_captured

    # mode (IODIR register)
    @property
    def mode(self):
        return self.porta.mode | (self.portb.mode << 8)
    @mode.setter
    def mode(self, val):
        self.porta.mode = val
        self.portb.mode = (val >> 8)

    # input_polarity (IPOL register)
    @property
    def input_polarity(self):
        return self.porta.input_polarity | (self.portb.input_polarity << 8)
    @input_polarity.setter
    def input_polarity(self, val):
        self.porta.input_polarity = val
        self.portb.input_polarity = (val >> 8)

    # interrupt_enable (GPINTEN register)
    @property
    def interrupt_enable(self):
        return self.porta.interrupt_enable | (self.portb.interrupt_enable << 8)
    @interrupt_enable.setter
    def interrupt_enable(self, val):
        self.porta.interrupt_enable = val
        self.portb.interrupt_enable = (val >> 8)

    # default_value (DEFVAL register)
    @property
    def default_value(self):
        return self.porta.default_value | (self.portb.default_value << 8)
    @default_value.setter
    def default_value(self, val):
        self.porta.default_value = val
        self.portb.default_value = (val >> 8)

    # interrupt_compare_default (INTCON register)
    @property
    def interrupt_compare_default(self):
        return self.porta.interrupt_compare_default | (self.portb.interrupt_compare_default << 8)
    @interrupt_compare_default.setter
    def interrupt_compare_default(self, val):
        self.porta.interrupt_compare_default = val
        self.portb.interrupt_compare_default = (val >> 8)

    # io_config (IOCON register)
    # This register is duplicated in each port. Changing one changes both.
    @property
    def io_config(self):
        return self.porta.io_config
    @io_config.setter
    def io_config(self, val):
        self.porta.io_config = val

    # pullup (GPPU register)
    @property
    def pullup(self):
        return self.porta.pullup | (self.portb.pullup << 8)
    @pullup.setter
    def pullup(self, val):
        self.porta.pullup = val
        self.portb.pullup = (val >> 8)

    # interrupt_flag (INTF register)
    # read only
    @property
    def interrupt_flag(self):
        return self.porta.interrupt_flag | (self.portb.interrupt_flag << 8)

    # interrupt_captured (INTCAP register)
    # read only
    @property
    def interrupt_captured(self):
        return self.porta.interrupt_captured | (self.portb.interrupt_captured << 8)

    # gpio (GPIO register)
    @property
    def gpio(self):
        return self.porta.gpio | (self.portb.gpio << 8)
    @gpio.setter
    def gpio(self, val):
        self.porta.gpio = val
        self.portb.gpio = (val >> 8)

    # output_latch (OLAT register)
    @property
    def output_latch(self):
        return self.porta.output_latch | (self.portb.output_latch << 8)
    @output_latch.setter
    def output_latch(self, val):
        self.porta.output_latch = val
        self.portb.output_latch = (val >> 8)

    # list interface
    # mcp[pin] lazy creates a VirtualPin(pin, port)
    def __getitem__(self, pin):
        assert 0 <= pin <= 15
        if not pin in self._virtual_pins:
            self._virtual_pins[pin] = VirtualPin(pin, self.portb if pin // 8 else self.porta)
        return self._virtual_pins[pin]

class VirtualPin():
    def __init__(self, pin, port):
        self._pin = pin % 8
        self._bit = 1 << self._pin
        self._port = port
    def __call__(self):
        return self.value()

    def _flip_bit(self, value, condition):
        return value | self._bit if condition else value & ~self._bit

    def _get_bit(self, value):
        return (value & self._bit) >> self._pin

    def value(self, val=None):
        # if val, write, else read
        if val is not None:
            self._port.gpio = self._flip_bit(self._port.gpio, val & 1)
        else:
            return self._get_bit(self._port.gpio)

    def input(self, pull=None):
        # if pull, enable pull up, else read
        self._port.mode = self._flip_bit(self._port.mode, 1) # mode = input
        if pull is not None:
            self._port.pullup = self._flip_bit(self._port.pullup, pull & 1) # toggle pull up

    def output(self, val=None):
        # if val, write, else read
        self._port.mode = self._flip_bit(self._port.mode, 0) # mode = output
        if val is not None:
            self._port.gpio = self._flip_bit(self._port.gpio, val & 1)
