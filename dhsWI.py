'''
dhsWI - a python module to query the Wisconsin Department of Health
Services Covid ARCGIS database using public API

usage: dhsWI.py [-h] [-v VERBOSITY] [--outfile OUTFILE] [--county COUNTY] [--muni MUNI]

optional arguments:
  -h, --help            show this help message and exit
  -v VERBOSITY, --verbose VERBOSITY
                        verbosity level (0 to 5)
  --outfile OUTFILE     name of output file
  --county COUNTY       specific county
  --muni MUNI           specific municipality
'''

import datetime     # conversion to/from database timestamp type
import time         # for time, duh.
import requests     # web rest requests
import argparse     # command line arguments
import json         # json handling

import utils        # logging, debug, etc.

# Class dhs - 
# class that handles queries against the DHS database
class dhs(object):
    # __init__() method called when an instance of the class is created
    def __init__(self, history):
        utils.dbgPrint(utils.LOG_INFO, 'instantiating')
        self._response = None

        self._month = history.tm_mon
        self._day = history.tm_mday
        self._year = history.tm_year

        # The DHS API has 2 urls we are interested in: 11 & 12.  11 gives us the whole state, 12 by county
        self._urlState = 'https://dhsgis.wi.gov/server/rest/services/DHS_COVID19/COVID19_WI/MapServer/11/query?where=DATE%3E%27YEAR-MONTH-DAY%2014%3A00%3A00.000000%27&outFields=DATE,POS_NEW,TEST_NEW,NAME,DTH_NEW,HOSP_YES&outSR=4326&f=json'
        self._urlCounty = 'https://dhsgis.wi.gov/server/rest/services/DHS_COVID19/COVID19_WI/MapServer/12/query?where=NAME%3D%27COUNTY%27%20and%20DATE%3E%27YEAR-MONTH-DAY%2014%3A00%3A00.000000%27&outFields=NAME,DATE,POS_NEW,HOSP_YES,DTH_NEW,TEST_NEW&outSR=4326&f=json'
        self._urlMuni = 'https://dhsgis.wi.gov/server/rest/services/DHS_COVID19/COVID19_WI/MapServer/16/query?where=NAME%3D%27MUNI%27%20and%20DATE%3E%27YEAR-MONTH-DAY%2014%3A00%3A00.000000%27&outFields=NAME,DATE,POS_NEW,HOSP_YES,DTH_NEW,TEST_NEW&outSR=4326&f=json'
    
    # Do the actual query, the result is a blob of JSON
    def doQuery(self, county, city):
        query = None
        if county == None and city == None:
            # basic query for the whole state
            query = self._urlState.replace('YEAR', str(self._year))
            query = query.replace('MONTH', str(self._month))
            query = query.replace('DAY', str(self._day))

            # display county name for results
            utils.outline('Query for entire state')
            
        elif city == None:
            # specific county; replace the text COUNTY with desired county name
            query = self._urlCounty.replace('COUNTY', county)
            query = query.replace('YEAR', str(self._year))
            query = query.replace('MONTH', str(self._month))
            query = query.replace('DAY', str(self._day))

            # display county name for results
            utils.outline('Query for {} county'.format(county))
        else:
            # specify municipality; replace text MUNI with desired municipality name
            query = self._urlMuni.replace('MUNI', city)
            query = query.replace('YEAR', str(self._year))
            query = query.replace('MONTH', str(self._month))
            query = query.replace('DAY', str(self._day))

            # display municipality name for results
            utils.outline('Query for municipality "{}"'.format(city))

        try:
            utils.dbgPrint(utils.LOG_INFO, 'query string: {}'.format(query))
            self._response = requests.get(query)
            utils.dbgPrint(utils.LOG_INFO, 'raw output: {}'.format(self._response.text))
        
        except ConnectionError:
            utils.dbgPrint(utils.LOG_ERR, 'Could not connect to DHS')
        
        except Exception as err:
            utils.dbgPrint(utils.LOG_ERR, 'Could not connect to DHS - {}'.format(err))

        # check for bad response; server busy, bad county name, etc
        if self._response == None:
            utils.outline('Empty response')
        elif not self._response.status_code == 200:
            utils.outline('Bad response code of {}'.format(resp.status_code))
        else:
            utils.dbgPrint(utils.LOG_DBG, 'Response length: {} bytes'.format(len(self._response.content)))

    # in case you wanna know if there's data to display
    def isValidResponse(self):
        if self._response == None:
            return (False)
        else:
            j = self.getResponseJSON()
            if len(self.getResponseJSON()['features']) > 0:
                return (True)
            else:
                return (False)

    # response as JSON data
    def getResponseJSON(self):
        if self._response == None:
            return (None)

        ret = json.loads(self._response.text)
        return (ret)
    
    # response as plain text
    def getResponseText(self):
        if self._response == None:
            return (None)
            
        return (self._response.text)

    # pretty-print output
    def prettyPrintResults(self):
        if self._response == None:
            utils.outline('No data to display')
        else:
            j = self.getResponseJSON()
            utils.outline('    DATE       NEW      TESTS   POS RATE   DEATHS  HOSPITAL')
            utils.outline(' ----------  -------   ------   --------   ------  --------')

            # get the results
            data = j['features']

            # sort by date, newest first
            data = sorted(data, key=lambda k: k['attributes'].get('DATE', 0), reverse=True)

            count14 = 0
            positive = 0
            total = 0

            # hackity-hack ugliness: the hospitalization rate is cumulative, so in order to 
            # get daily change
            dailyHospChange = []
            lastHosp = 0
            firstPass = True
            for item in data:
                thisHosp = item['attributes']['HOSP_YES']

                if not firstPass == True:
                    dailyHospChange.append(lastHosp - thisHosp)
                else:
                    firstPass = False
                
                lastHosp = thisHosp

            inx = 0

            # wrap this all in a try because the last read of newHosp will
            # throw an exception.  This is expected behavior
            try:
                # each 'item' is database row of returned result
                for item in data:
                    thisDate = utils.timeStampToDate(item['attributes']['DATE'])
                    newTests = item['attributes']['TEST_NEW']
                    newPositive = item['attributes']['POS_NEW']
                    newDeaths = item['attributes']['DTH_NEW']

                    newHosp = dailyHospChange[inx]
                    inx += 1

                    # avoid divide by zero errors
                    if not newTests == 0 and not newPositive == 0:
                        percentage = '{:> 6.1f}'.format((newPositive / newTests) * 100.0)
                    else:
                        percentage = '   0.0'

                    # accumulate the most recent 14 days worth of postives and total tests
                    # to cipher out the 14-day positivity rate
                    if count14 < 14:
                        positive += newPositive
                        total += newTests
                        count14 += 1

                    # formatted print output for nice columns
                    utils.outline(' {}   {:> 6}   {:> 6}    {}%    {:> 5}    {:> 6}'.format(
                        thisDate, newPositive, newTests, percentage, newDeaths, newHosp))
            
            # this exception is expected on the last row
            except IndexError:
                pass

            # don't show 14 day rate if less than 14 days of data.  duh.
            if count14 == 14:
                utils.outline('14-day positivity rate: {:> .1f}% ({} positive of {} tests)'.format(
                    ((positive / total) * 100), positive, total))

########################################################################
###                              MAIN                                ###
########################################################################
if __name__ == "__main__":
    # commandline argument handler
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', dest='verbosity', default=1, required=False, type=int, help='verbosity level (0 to 5)')
    parser.add_argument('--outfile', dest='outfile', default=None, required=False, help='name of output file')
    parser.add_argument('--county', dest='county', default=None, required=False, help='specific county')
    parser.add_argument('--muni', dest='muni', default=None, required=False, help='specific municipality')
    parser.add_argument('--days', dest='days', default=15, type=int, required=False, help='how many previous days')
    args = parser.parse_args()
    
    utils.setLogLevel(args.verbosity)

    # output to file if desired
    if not args.outfile == None:
        utils.setLogfile(args.outfile)

    # noisy
    if utils.LOG_LEVEL > utils.LOG_ERR:
        utils.outline('Output level: {}'.format(utils.logLevelToText()))

    # how far back to go in history?
    previous = time.localtime(
        time.time() - datetime.timedelta.total_seconds(datetime.timedelta(days = args.days + 1)))

    # we lose a couple of days accumulating data between days, so lie to the user
    display = time.localtime(
        time.time() - datetime.timedelta.total_seconds(datetime.timedelta(days = args.days - 1)))

    utils.outline('Getting data from {} to now'.format(time.strftime('%m/%d/%Y', display)))

    # new query object
    DHS = dhs(previous)

    # do the query
    DHS.doQuery(args.county, args.muni)

    # if we got results, output to console or file
    if DHS.isValidResponse() == True:
        DHS.prettyPrintResults()
    else:
        utils.outline('No results returned!')

    # if outputing to file, close that file
    utils.closeLogfile()