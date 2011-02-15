from BeautifulSoup import *
import urllib2, datetime, re, cPickle

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