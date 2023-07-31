'''
Created on 26 Jul 2023

@author: GHJ Morsink
'''
import sys
import optparse
import math

from sio import SIOdriver

ESC = chr(27)
CTRLG = chr(7)
SendStrings = [ESC+ESC+CTRLG,   # Graphics
               'C0',            # black pen
               'X2,10,40',      # X axis  10 , 40 points    
               'M180,-100',     # center of paper
               'X0,10,20',      # Y axis
               'H*C0'           # home, and color blue
               ]
SendStrings2 = ['H*C0',         # home, color black 
                'M0,-80',       # go to line under graph
                'A',            # text mode
                '  SIN,COS Relationship'  # title text
               ]


def Plotexample():
    """ The plotting app """

    parser = optparse.OptionParser(
        usage = "%prog [port]",
        description = "Plotting on Atari 1020 example\n" + \
                  " Plots some sine/cosine graphs.")
    parser.add_option("-p", "--port", dest = "port",
                      help = "port, a number (default 0) or a device name",
                      default = 'COM3')

    (options, _) = parser.parse_args()

    port = options.port

    try:
        config = { 'PORT':port, 'BAUDRATE':19200, 'PARITY':'N' }
        sio = SIOdriver(config)
    except:
        sys.stderr.write("could not open port %r\n" % (port))
        sys.exit(1)

    sio.start()
    for ss in SendStrings:
        sio.send(ss.encode('utf-8'))
        
    for angle in range(0,400):
        point = 'D%d,%d' % (angle, int(60*math.sin(math.radians(3*angle))))
        sio.send(point.encode('utf-8'))
    sio.send('H*C0'.encode('utf-8'))    # green pen
    for angle in range(0,400):
        point = 'D%d,%d' % (angle, int(60*math.cos(math.radians(3*angle))))
        sio.send(point.encode('utf-8'))

    for ss in SendStrings2:
        sio.send(ss.encode('utf-8'))
   
    sio.stop()        
    print('Ending')

if __name__ == '__main__':
    Plotexample()