'''
SIO Driver for printing/plotting to COM port
-------------------------------------

.. autoclass:: SIOdriver
   :members:
   
   
'''
#Created on 25 july 2023
#author: GHJ Morsink
import optparse
import threading
import serial
import sys
import time

PRINTERID = 0x40
WRITECOMMAND = 0x57
STATUS = 0x53
AUX1 = 0
AUX2 = 0x4E
EOL = 0x9B
ACK = 0x41
NAK = 0x4E
COMPLETE = 0x43
ERR = 0x45
CR = 0x0D
SPACE = 0x20


class SIOdriver(threading.Thread):
    ''' The NMEA reader '''
  
    def __init__(self, config, useDummy=False):  
        ''' constructor '''
        threading.Thread.__init__(self)
        #self.name("SIOdriver")
    
        self.__dummy = useDummy
        if not useDummy:
            try:
                self.serial = serial.Serial( config['PORT'],
                                             config['BAUDRATE'], 
                                             parity=config['PARITY'], 
                                             rtscts=False, xonxoff=False, timeout=0.1)
                self.serial.rts = False
            except:
                print('Got no serial connection!')
                self.__dummy = True # Read internally no data
        self.currentline = []
        self._stop = False
        self._lock = threading.Lock()
    
    def stop(self):
        ''' Stopping this thread '''
        self._stop = True  
    
    def run(self):
        """ The main thread running application
        This thread runs until it is stopped through a call to **stop()**
        It waits for characters from the serial port and adds it to the currentline.
        Note: because this can be through hardware buffering (USB or 16C550 derivates)
        characters can be delayed and can come in together. Do not depend on exact timing. 
        """
        while not self._stop:
            self.currentline = []
            self.reader()  #read a line       
  
    def reader(self):
        """ loop and copy serial->line"""
        while not self._stop:
            data = []
            if not self.__dummy:
                try:
                    data = self.serial.read(1)
                except:
                    data = []
                if data != '':
                    with self._lock:
                        self.currentline += data
            else:
                time.sleep(0.1)
                
    def waitforChar(self, expected, timeoutcount = 50):
        ''' wait fo max 0.5s for a ACK/COMPLETE '''
        count = 0
        while count < timeoutcount:  # timeout = 500ms
            if len(self.currentline) > 0:
                if self.currentline[0] == expected:
                    with self._lock:
                        self.currentline = self.currentline[1:] # remove the expected char
                    return True
                else:
                    print('no %s but %s received' % (expected, self.currentline[0]) )
                    self.currentline = []   # reset
                    return False
            time.sleep(0.01)
            count += 1
        print('Time-out! (%s)' % chr(expected))
        return False
                    
            
    def calcchk(self, datablock):
        ''' calculate checksum of a datablock
        '''
        chk = 0
        count = 0
        while count < len(datablock):
            chk = chk + datablock[count]
            if chk > 0xFF:
                chk = (chk + 1) & 0xFF
            count += 1
        return bytes([chk])

    def send(self, sendarray):
        """ Sending through protocol """
        self.currentline = []
        commandframe = [PRINTERID, WRITECOMMAND, AUX1, AUX2]
        commandframe += self.calcchk(commandframe)
        self.serial.rts = True      #set command line low
        time.sleep(0.001)
        self.serial.write(commandframe)
        self.serial.flush()         # wait for everything written
        time.sleep(0.001)
        self.serial.rts = False
        if not self.waitforChar(ACK):
            print('Command not accepted')
            return
        sendarray += bytes([EOL])
        while len(sendarray) < 40:
            sendarray += bytes([SPACE]) 
        sendarray += self.calcchk(sendarray)
        # self.currentline = []
        self.serial.write(sendarray)
        self.serial.flush()         # wait for everything written
        if not self.waitforChar(ACK):
            print('Data not accepted')
            return 
        # self.currentline = []
        self.waitforChar(COMPLETE, 1000) # may take up to 4 sec 
        return
        
  
def main():
    """ The app (only for testing text mode) """

    parser = optparse.OptionParser(
        usage = "%prog [options] [port [baudrate]]",
        description = "SIOdriver - A simple terminal program" + \
                  " for printing messages to Atari printer from the serial port.")

    parser.add_option("-p", "--port", dest = "port",
                      help = "port, a number (default 0) or a device name",
                      default = None)

    parser.add_option("-b", "--baud", dest = "baudrate", action = "store", 
                      type = 'int', help = "set baud rate, default %default", default = 19200)

    parser.add_option("--parity", dest = "parity", action = "store",
                      help = "set parity, one of [N, E, O, S, M], default=N", default = 'N')

    (options, args) = parser.parse_args()

    options.parity = options.parity.upper()
    if options.parity not in 'NEOSM':
        parser.error("invalid parity")

    port = options.port
    baudrate = options.baudrate
    if args:
        if options.port is not None:
            parser.error("no arguments are allowed, options only when --port is given")
        port = args.pop(0)
        if args:
            try:
                baudrate = int(args[0])
            except ValueError:
                parser.error("baud rate must be a number, not %r" % args[0])
            args.pop(0)
        if args:
            parser.error("too many arguments")
    else:
        if port is None: 
            port = 0


    try:
        config = { 'PORT':port, 'BAUDRATE':baudrate, 'PARITY':options.parity }
        sio = SIOdriver(config)
    except (serial.SerialException) as e:
        sys.stderr.write("could not open port %r: %s\n" % (port, e))
        sys.exit(1)

    sio.start()
    inputstr=''
    while inputstr != 'Q':
        inputstr = input('Send to printer:')
        if inputstr != 'Q':
            sio.send(list(inputstr.encode('utf-8')))

    sio.stop()        
    print('Ending')

if __name__ == '__main__':
    main()

