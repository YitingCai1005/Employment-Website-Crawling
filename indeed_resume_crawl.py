import pandas as pd
from bs4 import BeautifulSoup
import urllib2
from urllib2 import urlopen
import re
import json
import unicodedata
import time

URL2 = 'https://www.indeed.com/r/b3196e01febabc48'
#crawl([URL2],'tt','oopeopo')
def crawl (urllist,major,position):

    for url in urllist:
        time.sleep(3)
        try:
            data = urllib2.urlopen(url)
            soup = BeautifulSoup(data, "html.parser")
        except urllib2.HTTPError:
            time.sleep(300)
            print 'dead.............'
            continue

        OneR={'major':major,'position':position}
        t=soup.find('div',{'id':'basic_info_cell'})
        summary=''
        for i in t.children:
            if i.get('id')=='resume-contact':
                OneR['Jobtitle']=i.string
                print OneR['Jobtitle']
            elif i.get('id')=='contact_info_container':
                try:
                    OneR['adr']=i.find('p',{'class':'locality'}).text
                except AttributeError:
                    continue
            else:
                for string in i.stripped_strings:
                    #print repr(string)
                    ss=string
                    ss=ss.encode("latin-1", "ignore").decode('utf-8','ignore')
                    #print ss
                    summary=summary+' '+ss

                #summary = unicodedata.normalize("NFKD", summary)
                #summary=summary.encode("latin-1", "ignore").decode('utf-8','ignore')
                #summary=summary.translate({0x2022:u' '})
                OneR['summary'] = summary

        p=re.compile(r'section-item (?P<title>\S+)-content')
        for i in soup.find_all('div',{'class':p}):
            title=p.search(str(i)).group('title')
            #print title
            tag='section-item '+title+'-content'
            #print tag
            content=soup.find('div',{'class':tag}).text
            content = unicodedata.normalize("NFKD", content)
            OneR[title] = content.encode("latin-1", "ignore").decode('utf-8','ignore')

        #print json.dumps(OneR,indent=2)
        with open("Resume4.json", "a") as json_file:
            json.dump(OneR, json_file,sort_keys=True, indent=4)

def fab(page,Major, Position):
    i=0
    while page:
        time.sleep(5)
        try:
            PageData = urlopen(page)
            PageSoup = BeautifulSoup(PageData, 'html.parser')
        except urllib2.HTTPError:
            time.sleep(300)
            print 'DEAD.............'
            continue

        URLlist = ['https://www.indeed.com' + tag.get('href') for tag in
                   PageSoup.find_all('a', {'data-tn-element': 'resume-result-link[]'})]

        crawl(URLlist,Major,Position)
        print "Crawled %s :: %s Page %d"%(Major,Position,i)
        #time.sleep(1)
        i+=1
        try:
            nextp=PageSoup.find_all('a',{'class':'confirm-nav next'})[-1]
            if 'Next' in nextp.text:
                page='https://www.indeed.com/resumes'+nextp.get('href')

            #print page
            else:
                return 'FINISH page=%d'% i
        except:
            continue

def create_parent_page(position):
    position=position.replace('&','%26')
    position=position.replace(' ','+')
    URL = 'https://www.indeed.com/resumes?q=' + position # seed URL
    return URL

LL=pd.read_csv('majorandpositionnR2.csv',header=None,names=['major','position'])
for row in LL.itertuples():
    print row[1]
    print row[2]
    #print create_parent_page(row[2])
    fab(create_parent_page(row[2]),row[1],row[2])

#crawl(URLlist)
