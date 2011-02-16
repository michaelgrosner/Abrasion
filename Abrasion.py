import googleize, bingize
import getopt, sys

def usage():
	print """
Abrasion by Michael Grosner
Licensed under the Apache License (http://aws.amazon.com/apache2.0/)
Version 0.01
February 15, 2011

A simple, free, open-source Python script which will return the first x Google
search results' URL and page titles along with the total number of pages in the
Google database corresponding to the query. Tested and works in Python 2.6-2.7
in Mac OS and Ubunutu.

I would, however, like to point out that common sense says Google may block
your IP address/account if you're downloading too many pages or looking like a
potential attacker. Use common sense.

DEPENDENCIES:
1. BeautifulSoup.py -- http://www.crummy.com/software/BeautifulSoup/

SAMPLE USAGE:
python Abrasion.py "search phrase" [option name]=[option value]

Or within a python script:
import Abrasion
'Number of results', [link list], [title list] =
	Abrasion.googleize([search string], [option name]=[option value])

OPTIONS:
--nresults=   Number of results, an integer value. Defaults to 10.

--type=       Type of search. Defaults to `search`. Also supported:
	 `news`      Google News
	 `shopping`  Google Shopping (No Google Shopping specific options are implemented yet)
	 `blogs`     Search blogs
	 `video`     Search videos (not just youtube)


--timing=     Result ordering by Google. Currently supports:
	 `relevance` Sort by PageRank relevance (default)
	 `latest`    Sort by realtime updates to Google
	 `range`     Use when specifying a datestart and/or dateend
	 `date`      Sort by date, most recent at the top
--datestart=  Start date to search in MM/DD/YYYY format or a python datetime object.
--dateend=    End date to search in MM/DD/YYYY format or a python datetime object.

--language=   Change the language which to search in. Defaults to `en`.

--safe=       SafeSearch `on` or `off`. Defaults to `off`

--site=       Search within a domain. No default value.

-f [filename] Use cPickle to dump results in Python list form

-u            Show help dialog (this text)

-v            Verbose mode. Print Google links used to stdout.

Example Usage:
To get 100 links on "Android vs. iPhone" on www.engadget.com between
10/20/2009 and 2/4/2010 from shell and dump it into a cPickle object,
python Abrasion.py "Android vs. iPhone" --nresults=100 --timing=range --datestart=10/20/2009
	--dateend=02/04/2010 -f androidiphone.txt

In future versions, I would like to:
- Improve the general algorithm
	== Issues with flexibilty
	== Sites 10-15(?) may not be downloaded if Google decides to give video/news links
	== Related to above, Google also gives maps links which could be cut out, can't
		 figure out how short of banning all maps.google.com links
- Include scraping of other search engines
- Other search types, i.e. Books, Videos, Shopping
- Return descriptions and other data
- Improved error handling
	
	"""

if __name__ == '__main__':
	
	if len(sys.argv) == 1:
		usage()
		quit()
	
	search_term = sys.argv[1]
	opts, args = getopt.getopt(sys.argv[2:], 'hpvusf:', ['engine=', 'nresults=', 'site=', 'timing=', 'startdate=', 'enddate=', 'type=', 'language=', 'safe='])
	
	# Default parameters for lookup
	engine='google'
	type='search'
	language='en'
	startdate=''
	enddate=''
	timing='relevance'
	site=False
	safe='off'
	nresults=10
	output='p'
	verbose=False
	
	# Grab commandline arguments from getopt
	for o, a in opts:
		if   o == '--nresults':
			nresults = int(a)
		elif o == '--engine':
			engine = a
		elif o == '--site':
			site = a
		elif o == '--timing':
			timing = a
		elif o == '--startdate':
			startdate = a
		elif o == '--enddate':
			enddate = a
		elif o == '--type':
			type = a
		elif o == '--safe':
			safe = a
		elif o == '--language':
			language = a
		elif o == '-h':
			output = 'h'
		elif o == '-f':
			output = a
		elif o == '-p':
			output = 'p'
		elif o == '-u':
			usage()
			quit()
		elif o == '-s':
			output = 's'
		elif o == '-v':
			verbose = True
	
	if engine == 'google':	
		googleize.googleize(search_term, type=type, site=site, timing=timing, startdate=startdate, enddate=enddate, nresults=nresults, output=output, verbose=verbose)
	elif engine == 'bing':
		bingize.bingize(search_term, language=language, site=site, type=type, nresults=nresults)
	elif engine in ('yahoo', 'altavista', 'blekko'):
		raise Exception('Searching for %s not implemented yet' % engine)
	elif engine =='compare':
		# Create a new comparison function later
		pass
	else:
		raise Exception('Searching for %s not allowed' % engine)