# slime_os

Replace the contents of your PicoVision Micropython filesystem with the files in `src`.

This software is experimental and does not work completely, specifically issues include...

* Input is only supported via an i2c keyboard, which is not documented
* Some apps use `display.*` methods directly instead of `sos.graphics.*` so they do not support flipping the display
