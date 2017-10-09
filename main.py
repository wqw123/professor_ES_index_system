import pymysql

from Urlmanger import Urlmanger
from Downloader import Downloader

if __name__=='__main__':


    urlmanger = Urlmanger()

    urls = []  #获得所有表的链接
    # for i in range(1,38): # 1-38
    #     urls.append({'href':'https://profiles.stanford.edu/browse/school-of-medicine?affiliations=capFaculty&p='+str(i)+'&ps=100','sch':'school-of-medicine'})
    # for i in range(1, 15):
    #     urls.append({'href':'https://profiles.stanford.edu/browse/school-of-humanities-and-sciences?affiliations=capFaculty&p=' + str(i) + '&ps=100','sch':'school-of-humanities-and-sciences'})
    # for i in range(1, 8):
    #     urls.append({'href':'https://profiles.stanford.edu/browse/school-of-engineering?affiliations=capFaculty&p=' + str(i) + '&ps=100','sch':'school-of-engineering'})
    # for i in range(1, 3):
    #     urls.append({'href':'https://profiles.stanford.edu/browse/school-of-earth-energy-environmental-sciences?affiliations=capFaculty&p=' + str(i) + '&ps=100','sch':'school-of-earth-energy-environmental-sciences'})
    for i in range(1, 2):
        urls.append({'href':'https://profiles.stanford.edu/browse/graduate-school-of-business?affiliations=capFaculty&p=' + str(i) + '&ps=100','sch':'graduate-school-of-business'})
    print(len(urls))
    while(urls):
        url = urls.pop()
        urlmanger.urlCrawl(url['href'],url['sch'])

    downloader = Downloader()
    insert_sql1 = 'INSERT INTO profile (link_md5,source,university,sch,name,picture,bio,contacts,program,current_research,teaching,external_links,create_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '
    #
    insert_sql2 = 'INSERT INTO academicAppointments (link_md5,source,name,pro_title,department) VALUES (%s,%s,%s,%s,%s) '
    #
    insert_sql3 = 'INSERT INTO administrativeAppointments (link_md5,source,name,position,department,at_time) VALUES (%s,%s,%s,%s,%s,%s) '
    #
    insert_sql4 = 'INSERT INTO boards (link_md5,source,name,duty,department,at_time) VALUES (%s,%s,%s,%s,%s,%s) '
    #
    insert_sql5 = 'INSERT INTO honors (link_md5,source,name,honor_name,honor_department,honor_time) VALUES (%s,%s,%s,%s,%s,%s) '
    #
    insert_sql6 = 'INSERT INTO professionalEducation (link_md5,source,name,edu,school,edu_time) VALUES (%s,%s,%s,%s,%s,%s) '
    #
    insert_sql7 = 'INSERT INTO publications (link_md5,source,name,title,journal,authors,publish_time,abstract,doi_urls,pubmed_urls,wos) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '

    insert_sql8 = 'INSERT INTO patent (link_md5,source,name,inventor,patent_num,time) VALUES (%s,%s,%s,%s,%s,%s) '


    urlmanger.toCache(urlmanger.links)   #是否开启缓存

    while(urlmanger.links):
            url = urlmanger.links.pop()
            xueyuan=urlmanger.scho.pop()
            print("正在抓取：")
            print(url)     #每个教授具体信息的url

            try:
                downloader.download(url)
                data = downloader.data #拿到所有数据

                #基本信息的入库
                links = ','.join(data['external_links'])

                downloader.cursor.execute(insert_sql1,(data['md5'],data['source'],data['univer'],xueyuan,data['name'],data['picture'],data['bio'],data['contacts'],data['program'],data['current_research'],data['teaching'],links,data['create_time']))

                #
                for i in range(len(data['pro_title'])):
                    downloader.cursor.execute(insert_sql2,(data['md5'],data['source'],data['name'],data['pro_title'][i],data['bumen'][i]))
                #
                for i in range(len(data['position'])):
                    downloader.cursor.execute(insert_sql3,(data['md5'],data['source'],data['name'],data['position'][i],data['dept'][i],data['at_time'][i]))
                #
                for i in range(len(data['duty'])):
                    downloader.cursor.execute(insert_sql4, (data['md5'],data['source'],data['name'],data['duty'][i],data['boards_dept'][i],data['boards_time'][i]))
                #
                for i in range(len(data['honors_name'])):
                    downloader.cursor.execute(insert_sql5,(data['md5'],data['source'],data['name'],data['honors_name'][i],data['honors_dept'][i],data['honors_time'][i]))
                #
                for i in range(len(data['edu'])):
                    downloader.cursor.execute(insert_sql6,(data['md5'],data['source'],data['name'],data['edu'][i],data['school'][i],data['edu_time'][i]))
                #
                for i in range(len(data['title'])):
                    downloader.cursor.execute(insert_sql7,(data['md5'],data['source'],data['name'],data['title'][i],data['journal'][i],data['authors'][i],data['publish_time'][i],data['abstract'][i],data['doi_urls'][i],data['pubmed_urls'][i],data['wos'][i]))

                for i in range(len(data['inventor'])):
                    downloader.cursor.execute(insert_sql8,(data['md5'],data['source'],data['name'], data['inventor'][i], data['patent_num'][i], data['time'][i]))

                downloader.conn.commit()  # 进行统一的提交



            except Exception as e:
                print(str(e))
                continue






