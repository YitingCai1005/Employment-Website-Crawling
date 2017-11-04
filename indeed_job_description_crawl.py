import pandas as pd
import csv
from bs4 import BeautifulSoup
import requests
import urllib
import re


def cleanhtml(raw_html):  # clean html tags
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext

################crawl one page#######################
def crawl (URLlist,Major,Position):

    for UUU in URLlist:
        try:
            response = requests.get(UUU)
        except:
            continue

        if response.history:
            FinalURL=response.url
            print  response.url
        else:
            print "Request was not redirected"
            FinalURL=UUU


        if FinalURL[:22]!='https://www.indeed.com':
            print 'skip!'
            continue
        else:
            print 'yes!'

        tt=urllib.urlopen(FinalURL)
        ss=BeautifulSoup(tt,'html.parser')

        try:
            for t in ss.find_all('font',{'size':'+1'}):  # find job title
                print t.string
                JobTitle = t.string.encode('ascii', 'ignore')

            for c in ss.find('span',{'class':'company'}):  # find company name
                print c.string
                CompanyName=c.string.encode('ascii', 'ignore')

            for l in ss.find('span',{'class':'location'}):
                print l.string
                Location=l.string.encode('ascii', 'ignore')

            if ss.find('span',{'style':'white-space: nowrap'}):
                Salary=ss.find('span',{'style':'white-space: nowrap'}).string
            else:
                Salary='NA'

            for su in ss.find_all('span',{'id':'job_summary'}):
        #print su
                summary=str(su)
                summary=summary[39:-7]
                summary=summary.decode("ascii", "ignore").encode('ascii', 'ignore')
                summary=cleanhtml(summary)
                print summary

            for d in ss.find('span',{'class':'date'}):
                print d.string
                Date=d.string.encode('ascii', 'ignore')

        except TypeError:
            continue

    #line=str(FinalURL)+str(JobTitle)+str(CompanyName)+str(Location)+str(Salary)+str(summary)+str(Date)

        with open('FYA1.csv', 'a') as f:
        #headers=['URL','JobTitle','CompanyName','Location','Salary','Summary','Date']
            f_csv=csv.writer(f,dialect='excel')
            f_csv.writerow([Major]+[Position]+[FinalURL]+[JobTitle]+[CompanyName]+[Location]+[Salary]+[summary]+[Date])

####################################################
def fab(page,Major,PPosition):  # next page self loop
    i=0
    while page:
        dataf = urllib.urlopen(page)
        soupf = BeautifulSoup(dataf, 'html.parser')
        URLlist = ['https://www.indeed.com' + tag.get('href') for tag in soupf.find_all('a', {'data-tn-element': 'jobTitle'})]

        crawl(URLlist,Major,PPosition)

        i+=1
        try:
            nextp=soupf.find_all('span',{'class':'np'})[-1]
        except IndexError:
            break

        if 'Next' in nextp.text:
            #and i<5 :
            page='https://www.indeed.com'+nextp.parent.parent.get('href')
            print page
        else:
            return 'FINISH page=%d'% i


def CreatURL(cell):
    cell=cell.replace('&','%26')
    cell=cell.replace(' ','+')
    return 'https://www.indeed.com/jobs?q='+cell+'&l'

#####################################################################################
LL=pd.read_csv('majorandpositionn.csv',header=None,names=['major','position'])
for row in LL.itertuples():
    print row[1]
    print row[2]
    fab(CreatURL(row[2]),row[1],row[2])

