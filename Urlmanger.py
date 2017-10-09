#url下载
import ssl

from bs4 import BeautifulSoup
from urllib.request import *

class Urlmanger:
    links = set()  #使用set自动去重  这里就不使用指纹去重了，而是直接使用长度不一的url 直接内存去重
    scho=[]

    def urlCrawl(self,url,sch):
        context = ssl._create_unverified_context()

        res = urlopen(url,context=context)
        bsobj = BeautifulSoup(res, 'lxml')

        lis= bsobj.find('div',{'id':'browseListContent'}).find('ul',{'class':'unstyled list-items'}).findAll('li',{'class':'mini-profile-holder'})

        domain = 'https://profiles.stanford.edu'
        for li in lis:
            try:
                url = li.find('a',href = True).attrs['href']
                url = domain+url
                self.links.add(url)
                self.scho.append(sch)      #同步设置一个和这些链接同样长度的学院标签列表  长度是相同的
            except:
                continue
        return self.links,self.scho

    def toCache(self,links):     #写入缓存
        f = open('./cache', 'a')
        for link in links:
            f.write(link)
            f.write('\n')
