from BeautifulSoup import *
import urllib2, datetime, re, cPickle

def bingize(search_term, language='en', 
                          site=False, 
                          type='search',
													nresults=10,
                          news_timeinterval=8):
  
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	
	postfix = ''
	
	if type == 'search':
		soupClass = 'sb_meta'
	elif type == 'news':
		soupClass = 'sn_hd'
		postfix += '&p1=[NewsVertical+Interval%3d"%i"]' % news_timeinterval
	else:
		raise Exception('Not a valid search type: %s' % type)
	
	if language != 'en':
		search_term += ' language:%s' % language
	
	if site:
		search_term += ' site:%s' % site
	
	search_term = search_term.replace(' ', '+')
	
	linkList = []
	for result_i in xrange(0,nresults+1,10):
		
		try:
			bing_url = 'http://www.bing.com/%s?q=%s&first=%s%s' % (type, search_term, result_i, postfix)
			print bing_url
			response = opener.open(bing_url)
		except:
			print 'Could not download Bing search for %s' % search_term
		
		soup = BeautifulSoup(''.join(response))
		
		dataList = soup.findAll(attrs={"class" : soupClass})
		
		if type == 'search':
			for link in dataList:
				l = re.compile(r'<.*?>').sub('', str(link))
				dotfind = l.find('&nbsp;&#0183;')
				if dotfind > 0:
					l = l[:dotfind]
				linkList.append(''.join(['http://',l]))
				
		elif type == 'news':
			linkList.extend( [str(url)[9:].split('"')[3] for url in dataList] )
		
	print linkList
	
if __name__ == '__main__':
	bingize('Macbook Pro', type='search')