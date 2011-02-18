#!/usr/bin/env python

from BeautifulSoup import *
import urllib2, datetime, re, json, sys, getopt

def socialSearch(search_term, extra_params=False, api='facebook', nresults=10, followLinks=True, output='p'):
	if nresults > 100 and api == 'twitter':
		raise Exception('Please specify less than 100 results')
		
	urlregex = r"https?://([-\w\.]+)+(:\d+)?(/([\w/_\.]*(\?\S+)?)?)?"
	social_rules = {'twitter':  ['http://search.twitter.com/search.json?q=',      # Base link to api
															 'results', 'text',                               # json dict handlers
															 'rpp',                                           # key for nresults
															 lambda url: re.compile(urlregex).findall(url)],  # URL extractor
									'facebook': ['https://graph.facebook.com/search?q=',
															 'data', 'source',
															 'limit',
															 lambda url: url],
									#'reddit':   ['http://www.reddit.com/search?sort=new&q=',
									#						 'data', 'url',
									#						 False,
									#						 lambda url: url]
															 }
	
	if not extra_params: extra_params = {}
	
	# Add nresults to extra_params
	if social_rules[api][-2]: extra_params[social_rules[api][3]] = nresults
	
	# As before, change our user agent to prevent blocking, although with Twitter
	# I suspect they are much more liberal than the web searchers
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]

	# Construct a URL based on documentation found at...
	# http://apiwiki.twitter.com/w/page/22554756/Twitter-Search-API-Method:-search
	url = '%s%s' % (social_rules[api][0], search_term)
	
	if extra_params:
		for k, v in extra_params.iteritems():
			url += '&%s=%s' % (k,v)

	# Try and grab the JSON formatted data
	try:	
		socialData = json.load(opener.open(url))
	except:
		print 'Cannot load %s data on "%s"' % (api, search_term)
		print url

	if api == 'reddit':
		socialData = socialData['data']['children']

	linkList = []
	for post in socialData[ social_rules[api][1] ]:
		# For every tweet, use a regex to grab the link component
		try:
			text = post[ social_rules[api][2] ]
		except:
			# No link available
			continue
			
		link = social_rules[api][-1](text)

		# Not every tweet will yield a link, so don't cause an error if no link is found.
		# If there is a link, the regex is screwy and so the 0th and 2nd parts need to be
		# rejoined
		if isinstance(link,list) and api=='twitter':
			for l in link:
				try:
					url = ''.join(l)
					
					# If the user has indicated to follow all links, and not just get the bit.ly
					# etc links, use the .geturl() method to find the followed URL
					if followLinks:
						if url.startswith('http://') == False:
							url = 'http://'+url
						r = opener.open(url)
						linkList.append( r.geturl() )
					else:	
						linkList.append( url )
						
				except:
					pass
		else:
			linkList.append(link)	

	# Depending on whether this is used through the command-line interface or plugged
	# directly into python code, change the output. I would rather print out the linkList
	# in this manner so it'd be easier to run on a pipe for further processing.
	if output == 'p':
		print '=> Results for: %s' % api 
		for l in linkList:
			print l
	elif output == 'r':
		return linkList

def webSearch(search_term, extra_params=False, engine='google', site=False, nresults=10, output='p'):
	
	# Data structure containing the procedure to determining links
	engine_rules = {'google': ['http://www.google.com/search?q=',          # Base URL for search engine
														 'class', 'l',															 # Identifying tags for BeautifulSoup
														 lambda url: str(url)[9:].split('"')[0],		 # Function which gets link URL cleaned
														 lambda i: '&start=%s' % (10*i)],						 # Function calculating next page increment
		
									'bing':   ['http://www.bing.com/search?q=',
														 'class', 'sb_meta',
														 lambda url: re.compile(r'<.*?>').sub('', str(url)).split('&nbsp;&#0183;')[0],
														 lambda i: '&first=%i' % (10*i+1)],
										
									'yahoo':  ['http://search.yahoo.com/search?p=',
														 'class', 'yschttl spt',
														 lambda url: str(url).replace('%3a',':').partition('**')[2].split('"')[0],
														 lambda i: '&b=%i' % (10*i+1)],
										
									'blekko': ['http://blekko.com/ws/',
														 'class', 'UrlTitleLine',
														 lambda url: str(url).split('"')[3],
														 lambda i: '&p=%i' % i],
										
									# Can't get around duckduckgo's javascript
									#'duckduckgo': ['http://duckduckgo.com/?q=',
									#							 'class', 'l le',
									#								lambda url: url,
									#								lambda i: i],
										
									'ask':    ['http://www.ask.com/web?q=',
														 'id', re.compile('r[0-9]_t'),
														 lambda url: str(url).split('"')[3],
														 lambda i: '&page=%i' % (i+1)]}
	
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
	
	linkList = []
	i = 0
	while len(linkList) < nresults:
		try:
			# If the first page, don't include the page numbering, yet.
			if i != 0:
				# engine[0] rule is the base URL
				# engine[4](i) is the lambda function which maps the page number to
				#   the incrementor used in the URL
				url = '%s%s%s' % (engine_rules[engine][0], search_term, engine_rules[engine][4](i))
			else:
				url = '%s%s' % (engine_rules[engine][0], search_term)
			response = opener.open(url)
		except:
			print 'Could not download search for %s at %s' % (search_term,url)
		
		# Join all the response HTML together and send it to BeautifulSoup to work it's magic
		soup = BeautifulSoup(''.join(response))
		
		# Using the 1st and 2nd rules, use BeautifulSoup to parse the HTML and pick out
		# the links we are so desirous of.
		newLinkList = soup.findAll(attrs={engine_rules[engine][1]: engine_rules[engine][2]})
		
		# Using the 3rd rule, a lambda function which contains all the directions to
		# taking the BeautifulSoup HTML parsed <a href=...>mfcsdce</a> and cut it down to
		# just the URL
		linkList.extend( map(engine_rules[engine][3], newLinkList) )
		i += 1
	
	# Trim down the linkList to the desired number of results
	linkList = linkList[:nresults]
	
	# As in the Twitter search, output in different ways.
	if output == 'p':
		print '=> Results for: %s' % engine
		for l in linkList:
			print l
	elif output == 'r':
		return linkList

# This function is the entry point for all searches, and will either send the search
# to Twitter or web-based searches
def Search(search_term, extra_params=False, engine='google', site=False, followLinks=True, nresults=10, output='r'):
	
	# Convert indicated search engine to a list to loop over if passed as a string 
	if isinstance(engine, str): engine = [engine]
	
	# And make sure no other cruft gets through, just lists
	assert isinstance(engine,list)
	
	# Return links in a dictionary format
	links = {}
	for e in engine:
		if   e in ['twitter', 'facebook', 'reddit']:
			links[e] = socialSearch(search_term, extra_params, e, nresults, followLinks, output)
		elif e in ['google', 'yahoo', 'bing', 'blekko', 'ask']:
			links[e] = webSearch(search_term, extra_params, e, site, nresults, output)
		
	return links
	
# This function handles the command-line arguments, passing them to Search()
def searchFromBash():
	search_term = sys.argv[1]
	opts, args = getopt.getopt(sys.argv[2:], 'fa', ['engine=', 'nresults=', 'site='])
	
	engine = 'google'
	site = False
	nresults = 10
	followLinks = True
	searchAll = False
	extra_params = False
	
	for o, a in opts:
		if   o == '--engine':
			engine = a
		elif o == '-a':
			searchAll = True
		elif o == '-f':
			followLinks=False
		elif o == '--nresults':
			nresults = a
		elif o == '--site':
			site=site
			
	if searchAll: engine = ['google', 'yahoo', 'bing', 'blekko', 'ask', 'twitter', 'facebook']#, 'reddit']
		
	Search(search_term, extra_params=extra_params, engine=engine, site=site, followLinks=followLinks, nresults=nresults, output='p')

if __name__ == '__main__':
	#Search('Radiohead', engine=['twitter', 'facebook'], output='p')
	searchFromBash()