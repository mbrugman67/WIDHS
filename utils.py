'''
utils.py

Generic utility methods to be used all over the place.
This includes logging and the such

By default, logging is to stdout.  It can be redirected
to a file using the setLogfile() method
'''

import datetime     # conversion to/from database timestamp type
import sys          # getframe(), et.al.; used to find call chain for debug printing
import time         # for timestamps

# Current log level, see definition below
LOG_LEVEL = 1

# Log Levels:
#
LOG_ALL = 5     # Log everything
LOG_INFO = 4    # Log informational, debug, warning, errors
LOG_DBG = 3     # Log debug, warnings, errors
LOG_WARN = 2    # Log warnings and errors
LOG_ERR = 1     # Log errors
LOG_NONE = 0    # Log nuthin'

# file object is logging to file is selected
logfile = None


'''
setLogfile()
Enables writing all output to a file instead of stdout.  If specified
file is unwritable for whatever reason, output will fallback to stdout

Parameters:
    filespec for output

Returns:
    None
'''
def setLogfile(f):
    global logfile
    try:
        # open the output file in write mode (truncate existing file)
        logfile = open(f, 'w', encoding='utf-8')
    except err:
        logfile = None
        dbgPrint(LOG_ERR, 'unable to open err log {}:{}'.format(f, err))
        return


'''
closeLogfile()
Will turn off logging to file (if enabled).  Once called, all output goes back
to stdout.  Logging to file can be reenabled by calling setLogfile() again

Parameters:
    None

Returns:
    None
'''
def closeLogfile():
    global logfile
    if not logfile == None:
        try:
            logfile.close()
        except:
            pass

        logfile = None

'''
outline()
Generic output method; call from everywhere to "print".  It will go to the 
outfile if logging is enabled, otherwise to stdout
Parameter:
    s - string to output
Returns:
    None
'''
def outline(s):
    global logfile  # need to declare 'global' because writing to the file is a change
    if not logfile == None:
        logfile.write('{}\n'.format(s))
    else:
        print (s)


'''
dbgPrint()
General logging output method; a wrapper around Print() or file Write().  Each call
to dbgPrint() specifies a level; if the specified level is less than or equal to the 
current LOG_LEVEL, then the text will be output.  Otherwise, it is skipped.

Some crazy stuff here. Along the way, try to determine the name of the process that 
called this.  If it happens to be a class member, get that too.  Format it out and print it

Formatted output is in the form of:
YYYYMMDD HH:MM:SS DBG>method - text
where:
    + YYYYMMDD HH:MM:SS is a date/timestamp of when line was generated
    + DBG> is the literal text "INF", "DBG", "WRN", or "ERR"
    + method is the name of the method from which dbgPrint() was called
    + text is the text

For example
    dbgPrint(LVL_DBG, 'Added {} fuzzers.format(count))
in class config, method _parseConfigFile() would output:

20200602 15:04:34 DBG>config._parseConfigFile() - Added 2 fuzzers

assuming debug logging is enabled and it's 3:04 pm on the second of June, 2020
'''
def dbgPrint(lvl = LOG_ALL, stuff = None):
    # global logfile file object is written to here, so must be declared
    global logfile

    # make sure we actually have something to log and this level is logging
    if lvl <= LOG_LEVEL and not stuff == None: 
        className = None

        # start ciphering out method name (and class, if appropriate)
        # sys._getframe() returns the current frame.  .f_back is the next outer frame;
        # the caller's frame
        frame = sys._getframe().f_back

        # the name of the method that called this one
        methName = frame.f_code.co_name

        # special case - called from module level (as if in main()), the we'll just
        # say we were called by 'main
        if methName == '<module>':
            caller = 'main'
        else:
            # Try to pull the class name from the local stack frame.  If this fails,
            # then just rock on
            try:
                className = frame.f_locals['self'].__class__.__name__
            except KeyError:
                pass
            
            # formatted text string with class name (if any) and method name
            caller = ('{}.{}'.format(className, methName))

        # free it up!
        del frame

        # for the date/timestamp
        now = time.localtime()

        # log level
        if lvl == LOG_INFO:
            lvlText = 'INF'
        elif lvl == LOG_DBG:
            lvlText = 'DBG'
        elif lvl == LOG_WARN:
            lvlText = 'WRN'
        elif lvl == LOG_ERR:
            lvlText = 'ERR'
        else:
            lvlText = 'ALL'

        # write it all out, either to stdout or file
        if logfile == None:
            print ('{} {}>{}() - {}'.format(time.strftime('%Y%m%d %X'), lvlText, caller, stuff))
        else:
            logfile.write ('{} {}>{}() - {}\n'.format(time.strftime('%Y%m%d %X'), lvlText, caller, stuff))

'''
timeStampToDate()
'''
def timeStampToDate(ts):
    return(datetime.datetime.fromtimestamp(ts / 1000.0).strftime('%m/%d/%Y'))

def dateToTimeStamp(d):
    date = datetime.datetime.strptime(d, "%m/%d/%Y")
    return (int(datetime.datetime.timestamp(date) * 1000))


'''
setLogLevel()
set global output log level

Parameters:
    log level (see constant values above LOG_XXX)

Returns:
    None
'''
def setLogLevel(lvl):
    global LOG_LEVEL
    if lvl >= LOG_NONE and lvl <= LOG_ALL:
        LOG_LEVEL = lvl
    else:
        LOG_LEVEL = LOG_ERR


'''
logLevelToText()
Generic helper to return a string representing the current log level
Parameters & Returns:
    None
'''
def logLevelToText():
    if LOG_LEVEL == LOG_ALL:
        return ('all diagnostic messages')
    elif LOG_LEVEL == LOG_INFO:
        return ('errors, warnings, debug, and informational')
    elif LOG_LEVEL == LOG_DBG:
        return ('errors, warnings, and debug')
    elif LOG_LEVEL == LOG_WARN:
        return ('errors and warnings')
    elif LOG_LEVEL == LOG_ERR:
        return ('errors only')
    else:
        return ('error in output configuration')
