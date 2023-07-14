"""
Script to help using the USBcounter as timestamp device. Modded from QO Lab Script, C package dependencies removed from this package,
due to Windows compatability issue.
"""
# Origin: QO Lab NUS, Alessandro Cere
# Current Author: Chin Chean Lim
# Modified Date: 07/06/2019

import time
import csv
from numpy import int_
import serial_device


class FPGA_counter(serial_device.SerialDevice):
    def __init__(self, device: object = None) -> object:
        if device is None:
            try:
                device = 'COM1'
                #'/dev/ttyS2'   # set correct serial address, note the difference in Windows and Unix environment.
                # In Windows it is usually COM(x), in MAC /dev/tty.usbmodemTDC1..., in Ubuntu /dev/serial/by-id/usb-S-Fifteen_Instruments.......
                # In Linux, the path changes quite often and it is easier to just check the path by id, note line above
                # Please update this before you do anything.
            except IndexError:
                print('No suitable device found!')
            self._device = device
            serial_device.SerialDevice.__init__(self, device)
            self.timeout = .1  # necessary for python2
        # check what mode is the device in
        #self.mode
        #elf.int_time

    def startport(self, port):
         self.closeport()
         serial_device.SerialDevice.__init__(self, port)
         self.int_time
         print("Current Integration Time (ms): " +str(self._int_time))

    def closeport(self):
        self._closeport()

    @property
    def mode(self):
        self._mode = int(self._getresponse('MODE?')[0].decode().strip())
        return self._mode

    @mode.setter
    def mode(self, value):
        if value.lower() == 'singles':
            self.write(b'singles\n')
            self._mode = 0
        if value.lower() == 'pairs':
            self._mode = 1
            self.write(b'pairs\n')
        if value.lower() == 'timestamp':
            self._mode = 3
            self.write(b'timestamp\n')

    @property
    def level(self):
        """ Set the kind of pulses to count"""
        return self._getresponse('LEVEL?')[0].decode().strip()

    @level.setter
    def level(self, value):
        if value.lower() == 'nim':
            self.write(b'NIM\n')
        elif value.lower() == 'ttl':
            self.write(b'TTL\n')
        else:
            print('Acceptable input is either \'TTL\' or \'NIM\'')

    @property
    def clock(self):
        """ Choice of clock"""
        return self._getresponse('REFCLK?')[0].decode().strip()

    @clock.setter
    def clock(self, value):
        self.write('REFCLK {}\n'.format(value).encode())

    """ Functions for the counter mode"""
    @property
    def int_time(self):
        self._int_time = int(self._getresponse('TIME?')[0].decode().strip())
        return self._int_time

    @int_time.setter
    def int_time(self, value):
        self.write('TIME {}\n'.format(int(value)).encode())

    @property
    def counts(self):
        """
        Return the actual number of count read from the device buffer.
        :return: a three-element array of int
        """
        if self._mode == 3:
            print('The FPGA is set to timestamp mode!')
            return -1
        self.write('counts?\n'.encode())
        t_start = time.time()
        while time.time() - t_start < self._int_time * 1.2:
            if self.in_waiting != 0:
                return int_(self.readline().split())
        print('A timeout occured!\n')
        print(self.readlines())

# Sends serial command, assuming TTL signal.
    def timestamp_acq_python(self,t_int,signal):
        t_sleep = int(t_int)/1000 + 0.01  # waiting time in integration time (seconds) + 0.2 s
        self.timestamp = self._getresponseTime('*RST;'+'INPKT;'+signal+';TIME'+str(t_int)+';TIMESTAMP;COUNTS?' , t_sleep )
        bytes_hex = self.timestamp[::-1].hex()
        split_hex = [bytes_hex[i:i + 8] for i in range(0, len(bytes_hex), 8)][::-1]
        # 1 hex nibble is 4 bits. 4 hex for 1 event. code above split the long messages into individual events.
        num_of_bits =32
        scale = 32
        # Turning 8 nibbles to 32 bits, padding zeros.
        split_bin = [bin(int(split_hex[i], 16))[2:].zfill(num_of_bits) for i in range(0, len(split_hex),1)]

# Sends timestamp in ns, this takes into account of periodic repeats after 2^27 timer clicks. Period can be changed depending on device used.
# For TDC1 period is 2^27 * 2 ns.
        n=0
        timestamp_int = []
        pattern = []
        period = 2**28
        for i in range(len(split_bin)):
            retval = int(split_bin[i][:27], 2) * 2
            current_time = retval + n * period
            if len(timestamp_int) != 0:
                if split_bin[i][27]=="0":
                    if current_time < timestamp_int[-1]:
                         n = n+1
                         current_time = retval  + n*period
                else:
                    if retval == 7920:
                        n = n+1
                        current_time = retval  + n*period
                    else:
                        if pattern[-1][0]=="0":
                            n = n + 1
                        current_time = retval  + n*period
            timestamp_int.append(current_time) # making a list of time events in units of ns.
            pattern.append(split_bin[i][27:])   # signal pattern identified by timestamp
        return timestamp_int,pattern

# Pure python g2 histogram sorting script.
    def g2(self,timestamp_int,pattern,window,binwidth,maxbins):
        binwidth = int(binwidth)
        maxbins= int(maxbins)
        maxdelay = binwidth * maxbins
        histo = [0] * maxbins  # this stores the g2 histogram
        histoneg = [0] * maxbins  # this stores the g2 histogram
        cnt1 = 0
        cnt2 = 0
        coincidence = 0
        list1 = []
        list2 = []
        t1=0
        Norm = 0
        for i in range(len(timestamp_int)-1):
            t1 = timestamp_int[i]
            # This is where the window is moved with respect to maxdelay, older values from list1 and list2 are removed during calculation.
            # This assumes that no interesting coincidence happen beyond maxdelay.
            while list1:
                if (t1 - list1[0] >= maxdelay):
                    list1.pop(0)  # remove entries that are too old
                else:
                    break
            while list2:
                if (t1 - list2[0] >= maxdelay):
                    list2.pop(0)  # remove entries that are too old
                else:
                    break
            # Populating the timebins within maxdelay.
            for chan1time in list1:
                 delay = t1 - chan1time
                 histo[delay // binwidth] += 1
                 if delay < int(window):
                    coincidence += 1
            for chan2time in list2:
                 delay2 = t1 - chan2time
                 histoneg[delay2 // binwidth] += 1
                 if delay2 < int(window):
                    coincidence += 1

            # Channel 1 event. Append to list 1.
            if (pattern[i] == "00001"):  # just store
                cnt1 += 1
                list1.append(t1)
            # Channel 2 event, or events with simultaneous peaks.
            if (pattern[i] == "00010") or (pattern[i] == "00011"):  # for strict g2, no need to store. just iterate through list1 and perform g2
                if (pattern[i] == "00010"):
                    cnt2 += 1
                    list2.append(t1)
                else:
                    cnt1 += 1
                    cnt2 += 1
                    list1.append(t1)
                    list2.append(t1)
        # Calculating the norm for coincidence.
        if cnt1==0 or cnt2==0:
            print('Zero Counts in Channel 1 or Channel 2!')
        else:
            Norm = 1/(cnt1*cnt2*binwidth*1e6/t1)
        # This assumes positive delay happens when event at Channel 2 happens after Channel 1.
        histoN = [h*Norm for h in histo]
        histonegN = [h*Norm for h in histoneg]
        histonegN.reverse()
        return histoN, histonegN, cnt1, cnt2, coincidence, binwidth, maxbins


