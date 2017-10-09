from bs4 import BeautifulSoup
from urllib.request import *
import ssl
import time
import pymysql
import re
import hashlib
class Downloader:

    data={}

    # def __init__(self):
    #     self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', db='people',charset='utf8mb4')
    #     self.cursor = self.conn.cursor()


#负责数据清洗
    def process(self,str):
        list = str.split(',')

        for i in range(len(str) - 1, 0, -1):
            if (str[i] == '('):
                flag = 0
                index = i
                break
        if (flag == 0):
            time = str[index + 1:len(str) - 1]
        else:
            time = ' '

        if (time in list[len(list) - 1]):
            list[len(list) - 1] = list[len(list) - 1].replace(time, '').replace('(', '').replace(')', '')  #最后一段的内容要去掉时间内容和括号

        #将多个部门拼接
        dept =[]
        for i in range(1,len(list)):
            dept.append(list[i])
        c = ','.join(dept)

        return [list[0], c, time]

#链接指纹函数

    def get_md5(self,url):
        if isinstance(url, str):  # 只要是str 那么在p3里面，它的编码就是unicode的
            url = url.encode('utf8')
        m = hashlib.md5()
        m.update(url)
        return m.hexdigest()

#采集函数
    def download(self,url):
        context = ssl._create_unverified_context()
        res = urlopen(url, context=context)  # 对于https的网站处理
        bsobj= BeautifulSoup(res,'lxml')

#获得基本信息
        link_md5 = self.get_md5(url)  #拿到个人链接指纹
        source = url
        univer = 'stanford'

        try:
            picture = bsobj.find('div',{'class':'image-holder'}).find('img').attrs['src']
        except:
            picture = 'null'
        try:
            name = bsobj.find('div',{'class':'nameAndTitle'}).find('h1').get_text()
        except:
            name='null'
        try:
            contacts = bsobj.find('div',{'id':'contactInfoContent'}).get_text()
            contacts = contacts.strip('\n').replace('Contact', '') #要把多余字段去掉
        except:
            contacts='null'
        try:
            bio = bsobj.find('div',{'id':'bioContent'}).find('p').get_text()
        except:
            bio ='null'
        try:
            current_research = bsobj.find('div', {'id': 'currentResearchAndScholarlyInterestsContent'}).find(
                'p').get_text()

        except:
            current_research = 'null'

        try:
            teaching = bsobj.find('div', {'id': 'coursesContent'}).get_text().strip('\n')

        except:
            teaching = 'null'

        try:
            links=[]
            lis = bsobj.find('div', {'id': 'linksContent'}).find('ul').findAll('li')
            for li in lis:
                links.append(li.find('a').attrs['href'])
        except:
            links = []

        try:
            program = bsobj.find('div', {'id': 'programAffiliationsContent'}).find('ul').get_text().strip('\n')

        except:
            program = 'null'

        # try:
        #     pub_topics=[]
        #     lis= bsobj.find('div', {'id': 'tagCloudContent'}).find('ul').findAll('li')    #标签云抓不了
        #     for li in lis:
        #         pub_topics.append(li.get_text())
        #
        # except:
        #     pub_topics = []

        create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))




#获取职称和部门
        try:
            pro_title = []
            bumen = []

            uls  = bsobj.find('div',{'id':'academicAppointmentsContent'}).findAll('ul',{'class':'section-listing'})
            if(len(uls)==1):
                lis = uls[0].findAll('li')

                for li in lis:
                    all = li.get_text()
                    all = all.strip('\n')
                    list = all.split(',')
                    pro_title.append(list[0])
                    bumen.append(list[1])
            else:
                lis = uls[0].findAll('li')
                lis2 =uls[1].findAll('li')
                lis.extend(lis2)    #将lis2的所有元素添加到lis的尾部，完成两个list的合并
                for li in lis:
                    all = li.get_text()
                    all = all.strip('\n')
                    list = all.split(',')
                    pro_title.append(list[0])
                    bumen.append(list[1])

        except: #没有职称
            pro_title = []
            bumen = []


#获得admin
        try:
            position = []
            dept = []
            at_time = []

            uls = bsobj.find('div', {'id': 'administrativeAppointmentsContent'}).findAll('ul',
                                                                                         {'class': 'section-listing'})

            if (len(uls) == 1):
                lis = uls[0].findAll('li')
                for li in lis:
                    all = li.get_text()
                    all = all.strip('\n')  # 首先要对数据进行清洗

                    list = self.process(all)
                    position.append(list[0])
                    dept.append(list[1])
                    at_time.append(list[2])
            else:
                lis = uls[0].findAll('li')
                lis2 = uls[1].findAll('li')
                lis.extend(lis2)  # 将lis2的所有元素添加到lis的尾部，完成两个list的合并
                for li in lis:
                    all = li.get_text()
                    all = all.strip('\n')

                    list = self.process(all)
                    position.append(list[0])
                    dept.append(list[1])
                    at_time.append(list[2])

        except Exception  as e:
            #print(str(e))
            position = []
            dept = []
            at_time = []




#获得boards
        try:
            boards = []
            jigou = []
            boards_time = []

            uls = bsobj.find('div', {'id': 'professionalOrganizationsContent'}).findAll('ul',
                                                                                        {'class': 'section-listing'})
            if (len(uls) == 1):
                lis = uls[0].findAll('li')
                for li in lis:
                    all = li.get_text()
                    all = all.strip('\n')  # 首先要对数据进行清洗

                    list = self.process(all)
                    boards.append(list[0])
                    jigou.append(list[1])
                    boards_time.append(list[2])
            else:
                lis = uls[0].findAll('li')
                lis2 = uls[1].findAll('li')
                lis.extend(lis2)  # 将lis2的所有元素添加到lis的尾部，完成两个list的合并
                for li in lis:
                    all = li.get_text()
                    all = all.strip('\n')

                    list = self.process(all)
                    boards.append(list[0])
                    jigou.append(list[1])
                    boards_time.append(list[2])

        except Exception  as e:
            boards = []
            jigou = []
            boards_time = []


#获得honors
        try:
            honors_name = []
            honors_dept = []
            honors_time = []

            uls = bsobj.find('div', {'id': 'honorsAndAwardsContent'}).findAll('ul',
                                                                              {'class': 'section-listing'})
            if (len(uls) == 1):
                lis = uls[0].findAll('li')
                for li in lis:
                    all = li.get_text()
                    all = all.strip('\n')  # 首先要对数据进行清洗

                    list = self.process(all)
                    honors_name.append(list[0])
                    honors_dept.append(list[1])
                    honors_time.append(list[2])
            else:
                lis = uls[0].findAll('li')
                lis2 = uls[1].findAll('li')
                lis.extend(lis2)  # 将lis2的所有元素添加到lis的尾部，完成两个list的合并
                for li in lis:
                    all = li.get_text()
                    all = all.strip('\n')

                    list = self.process(all)
                    honors_name.append(list[0])
                    honors_dept.append(list[1])
                    honors_time.append(list[2])

        except Exception  as e:
            honors_name = []
            honors_dept = []
            honors_time = []




#获得教育背景
        try:
            edu = []
            school = []
            edu_time = []

            uls = bsobj.find('div', {'id': 'professionalEducationContent'}).findAll('ul',
                                                                              {'class': 'section-listing'})
            if (len(uls) == 1):
                lis = uls[0].findAll('li')
                for li in lis:
                    all = li.get_text()
                    all = all.strip('\n')  # 首先要对数据进行清洗

                    list = self.process(all)
                    edu.append(list[0])
                    school.append(list[1])
                    edu_time.append(list[2])
            else:
                lis = uls[0].findAll('li')
                lis2 = uls[1].findAll('li')
                lis.extend(lis2)  # 将lis2的所有元素添加到lis的尾部，完成两个list的合并
                for li in lis:
                    all = li.get_text()
                    all = all.strip('\n')

                    list = self.process(all)
                    edu.append(list[0])
                    school.append(list[1])
                    edu_time.append(list[2])

        except Exception  as e:
            edu = []
            school = []
            edu_time = []


#获取专利
        try:
            inventor = []
            patent_num = []
            pa_time = []
            lis = bsobj.find('div', {'id': 'patentsContent'}).find('ul').findAll('li')
            for li in lis:
                content = li.get_text()
                content = content.strip('\n')
                list = content.split('"')

                if (len(list) == 3):
                    inventor.append(list[0])
                    patent_num.append(list[1])
                    pa_time.append(list[2].strip(',').replace(' ', ''))

        except Exception as e:
            #print(str(e))
            inventor = []
            patent_num = []
            pa_time = []






#获得论文的具体信息
        title =[]
        authors =[]
        details=[]
        journal=[]
        abstract =[]
        doi_urls =[]
        pubmed_urls=[]
        wos=[]
        try:
            lis = bsobj.find('div', {'id': 'allPublicationsContent'}).find('ul', {'class':'section-listing articles'}).findAll('li') #所有文章的li
            for li in lis:
                title.append(li.find('cite').find('span', {'class': 'title'}).find('span').get_text())
                try:
                    journal.append(li.find('cite').find('span', {'class': 'title'}).find('i').get_text())
                except:
                    journal.append('null')

                authors.append(li.find('cite').find('span', {'class': 'authors'}).get_text())

                details.append(li.find('cite').find('span', {'class': 'details'}).get_text())  #这个是发表的时间

                try:
                    abstract.append(li.find('div',{'class':'detail'}).find('p',{'class':'abstract'}).get_text())
                except:
                    abstract.append('null')
                try:
                    doi_urls.append(li.find('div', {'class': 'detail'}).find('p', {'class': 'doi'}).find('a').attrs['href'])
                except:
                    doi_urls.append('null')
                try:
                    pubmed_urls.append(li.find('div', {'class': 'detail'}).find('p', {'class': 'pub-med'}).find('a').attrs['href'])
                except:
                    pubmed_urls.append('null')
                try:
                    wos.append(
                        li.find('div', {'class': 'detail'}).find('p', {'class': 'wos'}).find('a').attrs['href'])
                except:
                    wos.append('null')



        except Exception as e:
            #print(str(e))
            #print(name+'未发表论文')
            pass


        self.data={
            #基本表字段
            'md5':link_md5,
            'source':source,
            'univer':univer,
            'name':name,
            'picture':picture,
            'contacts':contacts,
            'bio':bio,
            'current_research':current_research,
            'teaching':teaching,
            'external_links':links, #数组
            'program':program,
            'create_time':create_time,

            'pro_title':pro_title,#数组
            'bumen':bumen,#数组

            'position':position,
            'dept':dept,
            'at_time':at_time,

            'duty':boards,
            'boards_dept':jigou,
            'boards_time':boards_time,

            'honors_name':honors_name,
            'honors_dept':honors_dept,
            'honors_time':honors_time,

            'edu':edu,
            'school':school,
            'edu_time':edu_time,

            'inventor':inventor,
            'patent_num':patent_num,
            'time':pa_time,



            'title':title,   #值是数组类型的值
            'journal':journal,
            'authors':authors,
            'publish_time':details,
            'abstract':abstract,
            'doi_urls':doi_urls,
            'pubmed_urls':pubmed_urls,
            'wos':wos,




        }















