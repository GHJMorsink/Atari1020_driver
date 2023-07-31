# Atari1020_driver
Python software driver for Atari 1020 printer/plotter.



This project shows a revival of a Atari 1020 plotter as an peripheral of a normal PC.

The hardware of the plotter mechanism is already described in many different other reviving projects; here the connection
and driver towards a normal PC is described. For the Atari SIO protocol a serial connection is needed. In this project
a TTL-232R-3V3 from FTDI-chip <https://www.ftdichip.com/Support/Documents/DataSheets/Cables/DS_TTL-232R_CABLES.pdf> is used. You can directly connect this to the plotter using:
  - pin 1 of TTL-232R (GND) goes to pin 4 or 6 Atari1020,
  - pin 4 of TTL-232R (TxD) goes to pin 5 of Atari1020,
  - pin 5 of TTL-232R (RxD) goes to pin 3 of Atari1020, and
  - pin 7 of TTL-232R (RTS#) goes to pin 7 (COMMAND) of Atari1020.

  
A description of the hardware can be found in the `docs` in `atari_1020_Field_Service_manual.pdf`; the protocol is originally described in `SIOspecs.pdf`.
A scanned datasheet, given by a reseller of the ALPS plotter, can be found in `ALPS_datasheet.pdf`
  
The software driver, written in python, can be found in `src` as `sio.py`. It contains also a test application for
printing in character mode. A nice plotting program, using the same driver is in `Plotexample.py`
  
For this project you need **Python3.xx** and the **pyserial** package. It is tested on Windows10 and should run on any system running Python3.
  
