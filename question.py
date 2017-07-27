#coding:utf-8
"""
    导出到知识点
"""
import json
import db_helper
import os
from lxml import etree
import codecs
import MySQLdb
import sys
from  redis import StrictRedis
reload(sys)
sys.setdefaultencoding('utf-8')

def get_list_list(dir_path="./list"):
    files = os.listdir(dir_path)
    return ['%s/%s' % (dir_path,file) for file in files if file.endswith('html')]

def _parse_list(content):
    html = etree.HTML(content)
    uid_list = html.xpath('/html/body/input[@name="STID"]/@value')
    type_list = html.xpath('/html/body/table/tr[1]/td[1]/b[1]/text()')
    difficulty_list = html.xpath('/html/body/table/tr[1]/td[1]/b[2]/text()')
    knowledges_list = html.xpath('/html/body/table/tr[2]/td/b/text()')
    body_list = [etree.tostring(body,encoding='UTF-8') for body in html.xpath('/html/body/table/tr[3]')]
    answer_list = [etree.tostring(body,encoding='UTF-8') for body in html.xpath('/html/body/table/tr[4]')]
    return zip(uid_list,type_list,difficulty_list,knowledges_list,body_list,answer_list)


def parse_list(file_path):
    """
        解析list 中的题目
    """
    with codecs.open(file_path,'rb',encoding='utf-8') as f:
        content = f.read()
    return _parse_list(content)

def insert(question):
    i_sql = u"insert into question(uid,type,diffculty,body,answer,knowledges,list_path) values('{uid}','{type}','{diffculty}','{body}','{answer}','{knowledges}','{list_path}') on Duplicate key update uid='{uid}';"
    print i_sql.format(**question)
    db_helper.execute(i_sql.format(**question))



def import_db(file,question_list):
    for _question in question_list:
        question = {
            'uid':_question[0],
            'type':_question[1],
            'diffculty':_question[2],
            'knowledges':_question[3],
            'body': MySQLdb.escape_string(_question[4]),
            'answer':MySQLdb.escape_string(_question[5]),
            'list_path':file
        }
        insert(question)

        
if __name__ == '__main__':
    files = get_list_list()
    redis = StrictRedis('localhost',db=0)
    for file in files:
        try:
            if redis.get(file) is None:
                redis.set(file,0)
                question_list = parse_list(file)
                redis.set(file,1)
            else:
                continue
            import_db(file,question_list)    
        except Exception as e:
            print e
        del file
        






