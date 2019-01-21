
This is a set of awfully chaotic code to read an antique ATI force-torque sensor (FT04714) on an equally antique NI E-series PCI-6036E acquisition card.
We do this on Linux.

1. Downloaded and compiled `comedilib` (not `comedi`). Ensured that the python bindings therein also compiled.
2. Butchered example from comedilib/demo/python ... and that basically worked.

