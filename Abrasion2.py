from BeautifulSoup import *
import urllib2, datetime, re

""" """

def webSearch(search_term, engine='google', site=False, nresults=10):
	
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
			if i != 0:	
				url = '%s%s%s' % (engine_rules[engine][0], search_term, engine_rules[engine][4](i))
			else:
				url = '%s%s' % (engine_rules[engine][0], search_term)
			print url
		except:
			print 'Could not download search for %s at %s' % (search_term,url)
			
		response = opener.open(url)
		
		# Join all the response HTML together and send it to BeautifulSoup to work it's magic
		soup = BeautifulSoup(''.join(response))
		newLinkList = soup.findAll(attrs={engine_rules[engine][1]: engine_rules[engine][2]})
		
		linkList.extend( map(engine_rules[engine][3], newLinkList) )
		i += 1
	
	linkList = linkList[:nresults]
	
	return linkList

if __name__ == '__main__':
	ws = webSearch('reddit.com', engine='google', nresults=20)
	print ws