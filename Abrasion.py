from BeautifulSoup import *
import urllib2, getopt, sys, datetime, re, cPickle

def googleize(search_term, type='search',
													 language='en',
													 startdate='',
													 enddate='',
													 timing='relevance',
													 site=False,
													 safe='off',
													 nresults=10,
													 output='h',
													 verbose=False):
	
	# Google doesn't like Python accessing it's pages, so change the user agent
	# and it should work fine
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	
	# Add + signs between words in search_term
	search_term = search_term.replace(' ', '+')
	
	# Begin by constructing the url to the search result. Google uses two seperate
	# ways of declaring options, one is &[option]=[value] and the other way is
	# &tbs=...[option]:[value].
	# If searching only a specific subdomain, build the `site` addition
	if site: search_term = ''.join(['site:', site, '+', search_term])
	
	# Prefix for the tbs options. I don't think 'en' at the end makes a difference,
	# even when specifying a seperate language
	tbs_opts = ''
	
	# Which type of search desired
	if type == 'search':
		pass
	# IMPLEMENT: Other search forms
	#elif type == 'books':
	#	tbs_opts += 'bks:1,'
	elif type == 'news':
		tbs_opts += 'nws:1,'
	elif type == 'shopping':
		tbs_opts += 'shop:1,'
	elif type == 'blogs':
		tbs_opts += 'blg:1,'
	elif type == 'video':
		tbs_opts += 'vid:1,'
	else:
		raise Exception("Invalid search type %s. See documentation for acceptable commands" % type)
	
	# `timing` controls the order of search result
	# 'latest' is the realtime Google update, i.e. sort by latest results
	if   timing == 'latest':
		tbs_opts += 'rltm:1,'
	# 'range' will allow the user to specify a range of results starting at
	# `startdate` and ending at `enddate`
	elif timing == 'range':
		
		# startdate and enddate can accept str and datetime objects. As of now, there
		# are no checks on the format of the string version. Implement later
		if startdate == '':
			startdate = datetime.date(1900, 1, 1).strftime('%m/%d/%Y')
		elif isinstance(startdate, datetime.date):
			startdate = startdate.strftime('%m/%d/%Y')
			
		if enddate == '':
			enddate = datetime.date.today().strftime('%m/%d/%Y')
		elif isinstance(enddate, datetime.date):
			enddate = startdate.strftime('%m/%d/%Y')
			
		tbs_opts += 'cd_min:%s,cd_max:%s,' % (startdate, enddate)
	# 'date' will sort by date, with newest results at the top. Not sure what is
	# different vs. 'latest'
	elif timing == 'date':
		tbs_opts += 'sbd:1,'
	# Standard Google search using their PageRank algorithm
	elif timing == 'relevance':
		pass
	else:
		raise Exception("Invalid timing command %s. See documentation for acceptable commands" % timing)
	
	linkList = []
	titleList = []
	
	#IMPLEMENT: Return descriptions?
	#descList = []

	# If more than 10 results are desired, loop so they're grabbed. This is a point of
	# weakness, see documentation for why
	for start in range(0,nresults,10):
		try:
			# The messy google url
			google_url = 'http://www.google.com/search?q=%s&hl=%s&safe=%s&start=%s&tbs=%s' % (search_term, language, safe, start, tbs_opts)
			if verbose: print start, google_url
			# And download the HTML
			response = opener.open(google_url)
		except:
			print 'Failed Google Response for %s (Add some better reporting here)' % search_term
		
		# Join all the response HTML together and send it to BeautifulSoup to work it's magic
		soup = BeautifulSoup(''.join(response))
		
		# Use extract links and titles
		if type in ('search', 'news', 'blogs', 'video'): dataList = soup.findAll(attrs={"class" : "l"})
		elif type in ('shopping'): dataList = soup.findAll(attrs={"class" : "r"})
			
			# In Google news, Google prefixes links with '/url?q=' so we need to chop that off
			# whereas that doesnt happen in regular search, either way, still need to cut off
			# <a href=... business
		if   type in ('search', 'blogs', 'video'):
			prefixLen = 9
			splitPart = 0
		elif type == 'news':
			prefixLen = 16
			splitPart = 0
		elif type == 'shopping':
			prefixLen = 0
			splitPart = 3
			
		linkList.extend( [str(url)[prefixLen:].split('"')[splitPart] for url in dataList] )
		titleList.extend( [re.compile(r'<.*?>').sub('', str(title)) for title in dataList] )
		
		#elif type == 'books':
		#	return soup.findAll(attrs={"class" : "r"})
		
		# If available, also extract the maximum results found
		if timing in ['range', 'relevance', 'date'] and start == 0:
			foundResults = soup.find(attrs={"id": "resultStats"})
			foundResults = re.search('(\d|,)*\d', str(foundResults)).group(0)
		else:
			foundResults = str(nresults)
		
	# Cut down linkList and titleList to fit nresults
	linkList  = linkList[:nresults]
	titleList = titleList[:nresults]
		
	if verbose:
		print 'Search: %s' % search_term
		print 'Type of search: %s' % type.title()
		print 'Number of Results: %s\n\n' % foundResults	
	
	if output == 'h':
		return (foundResults, linkList, titleList)
	elif output == 'p':
		for t, l in zip(titleList, linkList):
			print '%s\n%s\n' % (t, l)
	else:
		cPickle.dump([foundResults, linkList, titleList], open(output, 'w'))
		
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
	opts, args = getopt.getopt(sys.argv[2:], 'hpvuf:', ['nresults=', 'site=', 'timing=', 'startdate=', 'enddate=', 'type=', 'language=', 'safe='])
	
	# Default parameters for lookup
	type='search'
	language='en'
	startdate=''
	enddate=''
	timing='relevance'
	site=False
	safe='off'
	nresults=10
	output='p'
	verbose = False
	
	# Grab commandline arguments from getopt
	for o, a in opts:
		if   o == '--nresults':
			nresults = int(a)
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
			language = o
		elif o == '-h':
			output = 'h'
		elif o == '-f':
			output = a
		elif o == '-p':
			output = 'p'
		elif o == '-u':
			usage()
			quit()
		elif o == '-v':
			verbose = True
	
	googleize(search_term, type=type, site=site, timing=timing, startdate=startdate, enddate=enddate, nresults=nresults, output=output, verbose=verbose)
