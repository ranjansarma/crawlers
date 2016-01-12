# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
import calendar as CL
import re
import datetime
import bs4
import json
import logging
import pickle 
import socket
import shutil # A utility for copying,removing and archiving file/directory tree
import time
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


#set defalut timeout in sec
timeout=16
socket.setdefaulttimeout(timeout)

DAILY_INTERVAL = 4
ARTICLE_INTERVAL = 2

category_list = {
                    '1' : 'Headlines',
                    '2' : 'Brief_news',
                    '3' : 'Article',
                    '4' : 'Letters',
                    '5' : 'Editorials',
                    '6' : 'Sport',
                    }


def main():
    link_file= 'news_website.bin'
    year= int(raw_input('Enter the year :'))
    month=int(raw_input('enter the month: '))
    crawler(year, month, link_file)
    
def crawler(year, month, link_file):
    base_dir=str(year)
    try:
        os.mkdir(base_dir)
    except OSError:
        print base_dir , ' directory  exists'
    
    
       
    #defining all the temprorary  file name
    log_file_name = base_dir + '/' + str(month) +'_hindu.log'
    link_fail_daily_badlink  = base_dir + '/' +str(month) + '_link_failed_daily_badlink.txt'
    link_fail_daily_normal = base_dir + '/'  + str(month) + '_link_failed_daily_normal.txt'
    
    total_story_link = base_dir + '/' + str(month) + '_total_story_link.txt'
    link_fail_story_badlink  = base_dir + '/' + str(month) + '_link_failed_story_badlink.txt'
    link_fail_story_normal = base_dir + '/'  + str(month) + '_link_failed_story_normal.txt'

    logging.basicConfig(filename=log_file_name,filemode='a',format='%(levelname)s : %(message)s',level=logging.DEBUG)
    logging.info("logging starts \n ")
    t_start = time.ctime()
    logging.info('Start time: %s s\n' %(t_start) )
    
    
    b=Browser()
    
    for day in CL.Calendar().itermonthdays(year, month):
        if day != 0:
            day_dir= "%d/%d/%d"   %(year, month, day)
            date = "%d-%02d-%02d" %(year, month, day)
            for category in category_list:
                html_content = b.get_html(date,category)
                
                if type(html_content) == dict:
                    if str(html_content['e_code'])[0] == '4':
                        f=open(link_fail_daily_badlink,'a')
                        f.write(day_dir + ':' + link + '\n')
                        f.close()
                    else: 
                        f=open(link_fail_daily_normal,'a')  
                        f.write(day_dir + ':' + link + '\n' )
                        f.close()
                        if html_content['e_code'] == 48 :  # Keyboard interrupt
                            t= time.ctime()
                            logging.info('Keyboard Interrupt:: end time: %s ' %(t) )
                            return # Exit the code due to Keyboard Interrupt
                    continue # continue to next link
                
                #category = str(category)
                for item in b.get_link(html_content):
                    article_link = item.get('href')
                    article_html = b.get_html_article(article_link)
                    
                    if type(article_html) == dict:
                        if str(article_html['e_code'])[0]== '4':
                            f=open(link_fail_story_badlink,'a')
                            f.write(day_dir +':'+ category + ':' + link + '\n')
                            f.close()
                        else:
                            f=open(link_fail_story_normal,'a')  
                            f.write(day_dir + ':'+ category +':' + link + '\n')
                            f.close()
                            if article_html['e_code'] == 48 :  # Keyboard interrupt
                                t= time.ctime()
                                logging.debug('Keyboard Interrupt:: end time: %s' %(t) ) 
                                return # Exit the code due to Keyboard Interrupt
                        continue # continue to next story
                    
                    
                    
                    dir_loc = os.path.join(str(year), str(month), str(day), category_list[category])
                    try:
                        os.makedirs(dir_loc)
                    except OSError:
                        pass
                    fname = article_link.split('/')[-1]
                    f = open(os.path.join(dir_loc, fname), 'w')
                    f.write(b.get_content(article_html))
                    f.close()
                    
                    
                    
                    time.sleep(ARTICLE_INTERVAL)
                
                time.sleep(DAILY_INTERVAL)
        

class Browser:
    """
        Browser
    """
    def __init__(self, newbrowser=None):
        """
        It initializes the Cookies  and modify user agent
        """
        # Initialize Cookies
        CHandler = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        self.newbrowser = urllib2.build_opener(CHandler)
        self.newbrowser.addheaders = [
            ('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0')]
        urllib2.install_opener(self.newbrowser)
        self.error_dict={} # to be returned by get_html if any thing goes wrong
        
    
    def get_html(self,date='2016-01-10',category='2',base_url='http://ifp.co.in/page/archives'):
        """ Get html of the link  """
        
        #link = 'http://' + urllib.quote(link.lstrip('http://').encode('utf-8'))
        print 'opening index page for category %s' % category
        url = base_url
        data = urllib.urlencode({'ctid' : category,
		                     'nwsdt'  : date,
		                     'btn-submit' : 'Search+Archives'})
        try:
            req = urllib2.Request(url=url,data=data)
            data = urllib2.urlopen(req).read()
            return data
        
            
        except urllib2.HTTPError as e:
            self.error_dict['e_code'] = e.code
            self.error_dict['e_reason']=e.reason
            print 'HTTPError in link=%s' %(link)
            print 'error code:: ' , e.code
            print 'reason ::' , e.reason 
            return(self.error_dict)

        except urllib2.URLError as e: 
            
            self.error_dict['e_code'] = 12 # general  URLError code assigned by me
            self.error_dict['e_reason'] = 'URLError' # 
            print 'UrlError in link=%s' %(link)
            return(self.error_dict)

        except socket.timeout :
            time.sleep(60*1) # wait for 1 min after socket timeout  Error occured
            self.error_dict['e_code'] = 678 # assigned by me 
            self.error_dict['e_reason']= 'SocketTimeOut'
            print 'SocketTimeout Error in link=%s' %(link)
            return(self.error_dict)

        except KeyboardInterrupt: 
            self.error_dict['e_code'] = 789 # assigned by me
            self.error_dict['e_reason']='KeyboardInterrupt'
            print 'Keyboard Interrupt in link=%s' %(link)
            return(self.error_dict)
            
    def get_html_article(self,link):
        """ Get html of the link  """
        
        link = 'http://' + urllib.quote(link.lstrip('http://').encode('utf-8'))
        print 'opening  ' + link
        try :
            res = self.newbrowser.open(link)
            if res.headers.getheader('Content-Encoding') == 'gzip':
                data=zlib.decompress(res.read(), 16+zlib.MAX_WBITS) #decompress to normal html if server returns content in 'gziped' form 
            else:
                data=res.read()
            return data
            
        except urllib2.HTTPError as e:
            self.error_dict['e_code'] = e.code
            self.error_dict['e_reason']=e.reason
            print 'HTTPError in link=%s' %(link)
            print 'error code:: ' , e.code
            print 'reason ::' , e.reason 
            return(self.error_dict)

        except urllib2.URLError as e: 
            
            self.error_dict['e_code'] = 12 # general  URLError code assigned by me
            self.error_dict['e_reason'] = 'URLError' # 
            print 'UrlError in link=%s' %(link)
            return(self.error_dict)

        except socket.timeout :
            time.sleep(60*1) # wait for 1 min after socket timeout  Error occured
            self.error_dict['e_code'] = 678 # assigned by me 
            self.error_dict['e_reason']= 'SocketTimeOut'
            print 'SocketTimeout Error in link=%s' %(link)
            return(self.error_dict)

        except KeyboardInterrupt: 
            self.error_dict['e_code'] = 789 # assigned by me
            self.error_dict['e_reason']='KeyboardInterrupt'
            print 'Keyboard Interrupt in link=%s' %(link)
            return(self.error_dict)

    def get_link(self,content):
	
	

	    soup = bs4.BeautifulSoup(content, 'lxml')
	    article_link_soup = soup.find('article', attrs={'class': 'left-cont flt-left'})
	    links_soup = article_link_soup.find_all('a')
	    if links_soup is not None:
		    return links_soup
	    return []
    
    def get_content(self, html):
        content = ''
        soup = bs4.BeautifulSoup(html, 'lxml')
        content_soup = soup.find('div', attrs = {'class' : 'story-box'})
        if content_soup != None:
            content += content_soup.get_text().lstrip().replace('\r', ' ')
        return content


if __name__ == '__main__':          
    main()
