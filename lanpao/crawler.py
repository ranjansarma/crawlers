# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
import re
import datetime
import bs4
import json
import logging
import pickle 
import socket
import shutil # A utility for cpoying,removing and archiving file/directory tree
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
                    '2' : 'Sport',
                    '3' : 'Editorial',
                    '4' : 'LanPaoView',
                    '5' : 'Readers',
                    '6' : 'Message',
                    '7' : 'LanPaoSnippet',
                    '8' : 'Corindegum',
                    '11' : 'SpecialArticle',
                    '12' : 'ShareSmile',
                    '16' : 'Poem'
                    }


def main():
    link_file= 'new_website.bin'
    year= int(raw_input('Enter the year :'))
    month=int(raw_input('enter the month: '))
    crawler(year, month, link_file)
    
def crawler(year, month, link_file):
    base_dir=str(year)
    try:
        os.mkdir(base_dir)
    except OSError:
        print base_dir , ' directory  exists'
    
    
    try:
        f_link=open(link_file,'rb')
    except IOError:
        print 'Unable to read %s file' %(link_file)
        return
    try:
        news_link=pickle.load(f_link)
    except PickleError:
        print 'Pickle load Error in loading dictionary from %s file' %(link_file)
        return
        
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
    
    for day in news_link[year][month]:
        day_dir= "%d/%d/%d"   %(year, month, day)
        for link in news_link[year][month][day]:
            html_content = b.get_html(link)
            
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
            
            category = link.split('/')[-2]
            for item in b.get_link(html_content):
                article_link = item.get('href')
                article_html = b.get_html(article_link)
                
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
        
    
    def get_html(self,link):
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

    def get_link(self, html, patt=None):
        """ Get link of story for each day from html page of the day, takes html page and special pattern for the story link if any """
        print 'scrapping:::: \n'
        soup = bs4.BeautifulSoup(html)        
        pat = ur'http:\/\/www.hueiyenlanpao.com\/.*'
        patt = re.compile(pat)
        link_total = soup.findAll('a', href=patt)
        return link_total
        
    def get_content(self, html):
        content = ''
        soup = bs4.BeautifulSoup(html)
        content_soup = soup.find('div', attrs = {'class' : 'story-box'})
        if content_soup != None:
            content += content_soup.get_text().lstrip().replace('\r', ' ')
        return content


if __name__ == '__main__':          
    main()
