#!/usr/bin/python2

'''
    Changed: July 30, 2018

    Class to interract with setup.txt file
    Parses according to the following format list:
    [parameter]=[value][\n(Linux)\r\n(Windows)]
    ...

    Loading the parameter-value list into arrays
    Index of is used to loop throught and retrieve data
    This class relies on currect system time to calculate
    sleep and recording interval from the file

    Testing:
    The class can be run by itselt
    accepts the setup file path as a parameter
    prints all gathered data to the monitor

''' 

import datetime, sys

class SetupFile():

    # default parameters
    # overwritten by parsed data from setup file
    filepath = "/home/pi/USB/setup.txt"
    delim = '='     
    param = []
    value = []
    start = "08:00"
    end = "17:00"


    # Constructor
    # opens the file and loads all the data into arrays
    def __init__(self, path):
        self.filepath = path
        # Openning the file as Universal format
        # since Windows uses /r/n convention and Unix/Linux only /n
        # loading parameter-value pair into corresponding array
        with open(self.filepath, 'rU') as _file:
            # loop throught each line
            # if a line starts with a character
            for line in _file:
                if line and line[0].isalpha():
                    try:
                        # split each line using delimiter (=)
                        # remove white spaces
                        p,val = line.split(self.delim)
                        p = p.replace(" ", "")
                        val = val.replace(" ", "")
                        val = val.replace("\n", "")
                        # load parameter and value into arrrays
                        self.param.append(p)
                        self.value.append(val)
                        # save special parameters into separate variables
                        if(p == "start"): self.start = val
                        if(p == "end"): self.end = val
                        if(p == "release"): self.release = val
                    except: pass


    # Return value based on parameter name
    # runs throught the array and searches for parameter
    # return 0 if parameter not found
    def getParam(self, parameter):
        try:
            # returning calculated sleep and recording interval
            # calculation based on start-end time, format: [hour]:[minute]
            if(parameter == "sleep"): return self.calcSleep()
            if(parameter == "recording"): return self.calcRec()
            # returnning release time from setup file
            # format: [hr, min]
            if(parameter == "release"): 
                try:
                    rls = self.release.split(":")
                    return [int(rls[0]), int(rls[1])]
                except: pass
                return 0
            # returning any other parameter from the file
            for i in range(len(self.param)):
                if(self.param[i] == parameter): return int(self.value[i])

        except Exception as e:
            print e
        
        # return 0 if a parmeter not found
        return 0


    # Calculates and returns sleep interval
    # format: (int) [hour,min] array of 2 elements
    # sleep time is calculated from start and end time
    # sleep interval: time < start, time > end
    def calcSleep(self):
        try:
            # Converting from [hour]:[minute] notation
            # to [minute] parameter
            _start = self.toMin(self.start)             # start time
            _now = datetime.datetime.now()              # current time
            _now = self.toMin(str(_now.hour)+":"+str(_now.minute))

            # Two cases are possible when camera is started
            # 1. Camera is started before start time
            # sleep: sleeping untill start time 
            if(_now <= _start):
                duration = _start - _now

            # 2. Camera is past start time
            # Sleeping until the next days (next start time)
            # Adding 24-hours in minutes to start value
            elif(_now > _start): 
                _start += 1440
                duration = _start - _now
            
            # break down to [hh,mm] from [minutes]
            # returning in array format
            hr = int(duration/60)
            m = duration%60
            return [hr, m]

        except Exception as exp:
            print exp
            pass

        # default return in case of failure 15hr sleep
        return [15, 0]


    # Calculated and returns recording interval
    # format: (int) interval in minutes
    # recording time calculated from start and end time 
    # recording inverval: start < time < end
    def calcRec(self):
        try:
            # Converting from [hour]:[minute] notation to [minutes]
            # uses start,end and current time
            _start = self.toMin(self.start)             # start time
            _end = self.toMin(self.end)                 # end time
            _now = datetime.datetime.now()              # current time
            _now = self.toMin(str(_now.hour)+":"+str(_now.minute))

            # If user made a mistake in setup file
            # start time > end time
            # Swaping the two times
            if(_start > _end):
                _temp = _start      # swap
                _start = _end       # swap
                _end = _temp        # swap

            # Two cases are possible when camera is started
            # 1. Camera is started within recording interval time
            # rec inverval: difference between end time and start time
            if(_now >= _start and _now <= _end):
                interval = _end - _now

            # 2. Camera is started before designated time
            # rec interval is 0m
            elif(_now > _end or _now < _start): 
                interval = 0

            # returning recording interval in minutes
            return interval

        except Exception as exp:
            print exp

        # default return in case of failure 8hrs - 480m
        return 480


    # convert from string [hh]:[mm] to int [min]
    # return 0 if code failed to parse data
    def toMin(self, str_time):
        try:
            hr, min = str_time.split(':')
            return int(hr)*60 + int(min)

        except Exception as exp:
            print exp

        # default return
        return 0


    # Returns the full content of the param:value pair
    # used to test the class
    def dump(self):
        # loops throught the lenght of the arrays
        # prints to screen the index and values
        for i in range(len(self.param)):
            try:
                print "[{}] {} : {}".format( str(i), self.param[i], self.value[i])
            except: pass
                
# END Setup Class

# When class module is started by itself
# Following code is used for testing the parser class
# Accepts file path for setup file as input
if __name__ == '__main__':

    # Check for provided file path argument
    # Print an error if argument is not provided
    try:
        SETUP_FILE = sys.argv[1]
        print "Filepath: {}".format(SETUP_FILE)
    except:
        print "Error: filepath not provided"
        exit()

    # Create setup file object
    # opens and parses the file
    setup_file = SetupFile(SETUP_FILE)

    # prints on the sreen the contant of parsed arrays
    # used for debugging
    print "Dumpint data -----------------------"
    setup_file.dump()

    # Printing calculated intervals
    print "Intervals -----------------------"
    print "Sleep inverval: {}".format(str(setup_file.calcSleep()))
    print "Recording inverval: {}".format(str(setup_file.calcRec()))