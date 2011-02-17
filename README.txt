abrasionSearch is a very small, free, command-line interface to searching
  1. Google
  2. Bing
  3. Twitter
  4. Yahoo!
  5. Blekko
  6. Ask

Provide a search term and Abrasion willuse any or all of the above search engines to return a list of URLs. That is all
it does. This project was born out of a desire to do text analysis on past news and blog articles, and I could not find
a single, unified CLI to search even Google. As this is essentially a scraper (thus the name abrasion) of these sites,
please be mindful that many repeated calls to this script could get your IP address blocked by the search engines.

Any tips, corrections, updates, or general life lessons are greatly appreciated.

Dependencies:
1. Python 2.6-2.7 (tested on Mac OS X and Ubuntu)
2. BeautifulSoup (www.crummy.com/software/BeautifulSoup/) placed in either your
   PYTHONPATH or in the same directory as abrasionSearch

Installation:
1. python setup.py build
   [sudo] python setup.py install
2. Simply drop abrasion.py into which ever directory you need as long as Python
   can find BeautifulSoup

Usage:
1. From command-line:
  > python abrasion.py "search phrase" --[options]=[value]
2. From python scripts/interpreter
  > import abrasion
  > [return list] = abrasion.Search('search phrase', [options]=[value], )

Options:
  --engine=    Search engine to use. Defaults to 'google'. Also supports: 'bing', 'yahoo', 'twitter', 'ask', 'blekko'
               Supports combinations of the above search engines, so passing a list of ['bing', 'twitter'] will search
               those two sites. Can be overridden by '-a' option.
  
  --nresults=  Number of results to serve back. Defaults to 10. Twitter API maxes out at 100.
  
  --site=      Search within a specific domain i.e. search for all "iPhone" articles on 'engadget.com'. Not supported on
               'twitter'.
  
  -a           Search all search engines. Optional, but overrides '--engine' settings.
  
  -f           Do not follow bit.ly, goo.gl, etc. redirect links while searching 'twitter'

Written by Michael Grosner
Feb 17, 2011
Use freely; add, fork, include in your work, etc.