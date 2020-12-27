# WI DHS Query
I was looking at the Covid page on the Wisconsin Department of Health Services website and saw a link labeled "API Explorer".  Don't mind if I do...

This is the result.  You can query the database to get Covid numbers for the whole state of Wisconsin, a specific county, or a specific municipality.  
## Notes
This was written for Python 3, why would anyone be using Python 2 - it's been deprecated for almost a full year now.

Also, I really suggest using a virtual environment to keep your Python environment clean.  See [instructoins here](https://docs.python.org/3/library/venv.html)  
## Usage
General usage is `python3 dhsWI.py <parameters...>`  Parameters:  
+  `--outfile FileName` sends all output to the specified file
+  `--days NumberOfDays` is how many days back from today to gather data.  Default is 14
+  `--county CountyName` gives numbers for that county
+  `--muni Municipality` gives numbers of a specific municipality.  Note that this form is a bit funky; for the city of Green Bay, you need to use `--muni "Green Bay city`.  Essentially, the name of the municipality and the type.  Types can be things like city, town, village.  Some experimentation may be needed to get it right.  
#### Example for the whole state
Just use it with no parameters:
```
(venv) hackintux:dhs matty$ python dhsWI.py 
    DATE       NEW      TESTS   POS RATE   DEATHS  HOSPITAL
 ----------  -------   ------   --------   ------  --------
 12/15/2020     3501     7299      48.0%       54       184
 12/14/2020     2122     7350      28.9%       12        77
 12/13/2020     2757    12175      22.6%       15        87
 12/12/2020     4059    13642      29.8%       50       142
 12/11/2020     3858    11045      34.9%       47       145
 12/10/2020     4034    12555      32.1%       57       160
 12/09/2020     3619    11726      30.9%       81       215
 12/08/2020     4114     9591      42.9%       68       214
 12/07/2020     2155     7906      27.3%       19        70
 12/06/2020     2791    10564      26.4%       17        90
 12/05/2020     4831    13460      35.9%       77       183
 12/04/2020     4847    15197      31.9%       63       202
 12/03/2020     4618    11972      38.6%       60       172
 12/02/2020     3777     9983      37.8%       82       197
 12/01/2020     4078    10492      38.9%      107       277
 11/30/2020     2534     8740      29.0%        6        96
 11/29/2020     3831     9511      40.3%       22       117
 11/28/2020     5033     9443      53.3%       28       167
 11/27/2020     1300     9798      13.3%       17        57
 11/26/2020     5095    13748      37.1%       62       201
14-day positivity rate:  33.1% (51083 positive of 154465 tests)
```
With fewer days:
```
(venv) hackintux:dhs matty$ python dhsWI.py --days 5
Getting data from 12/23/2020 to now
Query for entire state
    DATE       NEW      TESTS   POS RATE   DEATHS  HOSPITAL
 ----------  -------   ------   --------   ------  --------
 12/26/2020      632     5893      10.7%        4        31
 12/25/2020     1506     8615      17.5%        5        56
 12/24/2020     2799    10518      26.6%       60       128
 12/23/2020     2579     8856      29.1%       69       164
```
Two notes of interest here:
+  If it is before 2:00 pm central time, you will actually have one less day of data.  New data comes out at 2
+  If you specify a number of days and get less than 14 days returned, the 14-day positivity rate won't be displayed.  Duh.
#### Exmaple for a county
```
(venv) hackintux:dhs matty$ python dhsWI.py --count Manitowoc
Query for Manitowoc county
    DATE       NEW      TESTS   POS RATE   DEATHS  HOSPITAL
 ----------  -------   ------   --------   ------  --------
 12/15/2020       35      100      35.0%        0         0
 12/14/2020       37      128      28.9%        0         4
 12/13/2020       30      137      21.9%        0         1
 12/12/2020       53      162      32.7%        9         2
 12/11/2020       43      123      35.0%        0         2
 12/10/2020       44      134      32.8%        0         1
 12/09/2020       35      123      28.5%        0         1
 12/08/2020       51      154      33.1%        0         1
 12/07/2020       34      110      30.9%        0         1
 12/06/2020       28       94      29.8%        1         0
 12/05/2020       96      212      45.3%        0         4
 12/04/2020       64      293      21.8%        0         2
 12/03/2020       42       99      42.4%        0         3
 12/02/2020       38       55      69.1%        0         3
 12/01/2020       53      123      43.1%        0         2
 11/30/2020       43      169      25.4%        0         0
 11/29/2020       56      154      36.4%        0         0
 11/28/2020       62      127      48.8%        1         0
 11/27/2020        0       46       0.0%        0         0
 11/26/2020       32       56      57.1%        1         1
14-day positivity rate:  32.7% (630 positive of 1924 tests)
```

#### Example for a munipality
```
(venv) hackintux:dhs matty$ python dhsWI.py --muni "Oak Creek city"
Query for municipality "Oak Creek city"
    DATE       NEW      TESTS   POS RATE   DEATHS  HOSPITAL
 ----------  -------   ------   --------   ------  --------
 12/15/2020       10       46      21.7%        0         1
 12/14/2020       40       75      53.3%        0         2
 12/13/2020       37      125      29.6%        0         0
 12/12/2020       50      127      39.4%        0         0
 12/11/2020       17       61      27.9%        1         2
 12/10/2020       33       88      37.5%        0         3
 12/09/2020        1       48       2.1%        1        -1
 12/08/2020       35       68      51.5%        0         1
 12/07/2020       13       57      22.8%        0         1
 12/06/2020       20       79      25.3%        0         1
 12/05/2020       33       83      39.8%        0         1
 12/04/2020       21       94      22.3%        0         0
 12/03/2020       60      120      50.0%        1         3
 12/02/2020       35       63      55.6%        1         3
 12/01/2020       42       78      53.8%        1         2
 11/30/2020       18       72      25.0%        0         1
 11/29/2020       55       85      64.7%        0         2
 11/28/2020        1       12       8.3%        0         1
 11/27/2020        0       62       0.0%        0         0
 11/26/2020       38      139      27.3%        0         2
14-day positivity rate:  35.7% (405 positive of 1134 tests)
```  
## Final words
First off, Coronovirus and Covid-19 is real.  **Wear a damn mask**.  

If you have any questions on the numbers, refer them to the Wisonsin DHS.  You can see the source code here, I'm not doing anything with the numbers, just pulling them down using their public API.

