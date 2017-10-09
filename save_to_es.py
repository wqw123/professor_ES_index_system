from model.es_types import ArticleType
from Urlmanger import Urlmanger
from Downloader import Downloader
from elasticsearch_dsl.connections import connections
import redis
es = connections.create_connection(ArticleType._doc_type.using)

redis_cli = redis.StrictRedis()   #开启redis数据库，用来记录抓取数据量

if __name__=='__main__':


    def gen_suggests(index, info_tuple):  # 通过分析器来生成建议字段内容
        # 根据字符串生成搜索建议数组
        used_words = set()
        suggests = []
        for text, weight in info_tuple:
            if text:
                # 调用es的analyze接口分析字符串
                words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]},
                                           body=text)
                anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
                new_words = anylyzed_words - used_words
            else:
                new_words = set()

            if new_words:
                suggests.append({"input": list(new_words), "weight": weight})  # es建议字段的格式

        return suggests


    urlmanger = Urlmanger()

    urls = []  #获得所有表的链接
    for i in range(1, 2):
        urls.append({'href':'https://profiles.stanford.edu/browse/graduate-school-of-business?affiliations=capFaculty&p=' + str(i) + '&ps=100','sch':'graduate-school-of-business'})
    print(len(urls))
    while(urls):
        url = urls.pop()
        urlmanger.urlCrawl(url['href'],url['sch'])

    downloader = Downloader()
    while (urlmanger.links):
        url = urlmanger.links.pop()
        print("正在抓取：")
        print(url)  # 每个教授具体信息的url
        try:
            downloader.download(url)
            data = downloader.data          # 拿到一个教授的信息数据
            redis_cli.incr("people_count")  # 内存数据库里面，该变量全局可用


            article = ArticleType()  # 导入es的模型类
            article.title = data['name']
            article.create_date = data["create_time"]
            article.content = ';'.join(data["title"])     #向用户展示的该教授的所有论文
            article.url = data["source"]
            article.tags = ';'.join(data["pro_title"])
            article.meta.id = data["md5"]   #es数据的主键  我们使用自己的id
            article.suggest = gen_suggests(ArticleType._doc_type.index,
                                           ((article.title, 10), (article.tags, 7)))  # 教授的建议字段应该以名字来建议
            article.save()    #执行这个方法就可以将教授信息存入ES了，就和数据库的commit一样





        except Exception as e:
            print(str(e))
            continue
