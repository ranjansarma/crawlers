# ctid=2&nwsdt=2016-01-10&btn-submit=Search+Archives
import urllib
import urllib2
from bs4 import BeautifulSoup

def get_link(date='2016-01-10',category='2',base_url='http://ifp.co.in/page/archives'):
	url = base_url
	data = urllib.urlencode({'ctid' : category,
		                     'nwsdt'  : date,
		                     'btn-submit' : 'Search+Archives'})
	req = urllib2.Request(url=url,data=data)
	content = urllib2.urlopen(req).read()

	soup = BeautifulSoup(content, 'lxml')
	article_link_soup = soup.find('article', attrs={'class': 'left-cont flt-left'})
	links_soup = article_link_soup.find_all('a')
	if link_soup is not None:
		return link_soup
	return []

#print content
