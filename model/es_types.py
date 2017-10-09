#定义es 模型

# -*- coding: utf-8 -*-

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

class ArticleType(DocType):
    #定义教授字段类型
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")     #选用ik_max_word 中文分词器
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    #front_image_url = Keyword()
    #front_image_path = Keyword()
    #praise_nums = Integer()
    #comment_nums = Integer()
    #fav_nums = Integer()
    tags = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")

    class Meta:
        index = "stanford"      #在这个类型里面声明index和type
        doc_type = "professor"

if __name__ == "__main__":
    ArticleType.init()      #该类初始化后，会自动创建我们定义好的mappings
