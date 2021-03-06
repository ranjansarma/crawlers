#!/usr/bin/python
import calendar as CL
import json
import pickle
import datetime

# 21-FEB-2012

category_list = [1,2,3,4,5,6,7,8,11,12,16]

def form_link(start_year,end_year):
    now = datetime.datetime.now()
    current_year = start_year
    new_website = {}
    base_link = 'http://www.hueiyenlanpao.com/page/showarchives/'
    while current_year <= end_year:
        new_website[current_year]= {}
        for month in range(1, 13):
            str_month = "%02d" % (month) # prepending 0(zero) to the month to restrict to two digits
            new_website[current_year][month]={}
            for day in CL.Calendar().itermonthdays(current_year, month):
                if day != 0:
                    date_string = '%d-%02d-%02d' % (current_year, month, day) 
                    list_link = []
                    for category in category_list:
                        final_link = '%s%d/%s' % (base_link, category, date_string)
                        list_link.append(final_link)
                    
                    
                    new_website[current_year][month][day]= list_link
                    if current_year == now.year and  month == now.month and day == now.day:
                         break
            if current_year == now.year and  month == now.month and day == now.day:
                 break
        if current_year == now.year and  month == now.month and day == now.day:
             break

        current_year += 1
        
    #f.close()
    f=open('news_website.txt','w')
    json.dump(new_website,f,indent=4)
    f.close()
    f=open('news_website.bin','wb')
    pickle.dump(new_website,f)
    f.close()



def main():
    start_year=2012
    end_year=2015
    form_link(start_year,end_year)


if __name__ == '__main__':
    main()
