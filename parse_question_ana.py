# coding:utf-8
"""
    试题解析:
        1. 获取需要解析的试题内容
        2. 简单去除试题内容中的多余的标签
        3. 选择题提取出 具体的答案
        4. 从答案内容中提取出解析内容

"""
import db_helper
from  redis import StrictRedis
from hashlib import md5
import re
import MySQLdb
import sys
import time
from lxml import etree
reload(sys)
sys.setdefaultencoding('utf-8')

redis = StrictRedis('localhost',db=4)


pattern_answer = re.compile(ur'<font[\s\S]{0,10}color=\"red\">[\s\S]*?【答案】([\s\S]*?)【解析】')
pattern_analysis = re.compile(ur'【解析】([\s\S]*?)</font>[\s]{0,}</div>[\s]{0,}</td>')
pattern_body = re.compile(r'<tr>[\s]*?<td height="38" width="619"   style=""  >([\s\S]*)</td>[\s]*?</tr>')

def get_question_id_list(type='选择题'):
    """
        获取 试题
    """
    sql = "select id from docai.question where type='{type}'"
    ids = db_helper.query_all(sql.format(type=type))
    return [id['id'] for id in ids]

def get_question(id):
    """
        获取试题
    """
    sql = "select * from docai.question where id={id}"
    return db_helper.query_one(sql.format(id=id))

def parse_answer(answer):
    """
        解析:答案
    """
    # print answer
    answer_ = pattern_answer.findall(answer)
    analysis = pattern_analysis.findall(answer)
    if answer_ is None or len(answer_) == 0:
        answer_ = ''
    else:
        answer_ = answer_[0]
    if analysis is None or len(analysis) == 0:
        analysis = ''
    else:
        analysis = analysis[0]
    return answer_.strip(' \n\t\r'),analysis.strip(' \n\t\r')
    





def parse_body(body):
    """
        解析body
    """
    body_ = pattern_body.findall(body)
    if body_ is None or len(body_) == 0:
        raise Exception('error: %s ' % body)
    else:
        body_ = body_[0]
    return body_.strip(' \n\t\r')

    
    

def insert(question):
    i_sql = u"insert into question_tmp(id,uid,type,diffculty,body,answer,knowledges,list_path,analysis,json) values({id},'{uid}','{type}','{diffculty}','{body}','{answer}','{knowledges}','{list_path}','{analysis}','{json}') on Duplicate key update uid='{uid}';"
    print i_sql.format(**question)
    db_helper.execute(i_sql.format(**question))


def run(type):
    id_list = get_question_id_list(type)
    count = 0
    for id in id_list:
        if redis.get(id) is not None:
            continue
        redis.set(id,'0')
        question = get_question(id)
        try:
            body = parse_body(question['body'])
            answer,analysis = parse_answer(question['answer'])
        except Exception as e:
            # print count, e , question['body']
            print e
            redis.delete(id)
            continue
        count += 1
        # print body,choices_a,choices_b,choices_c,choices_d,answer,analysis
        question['body'] = MySQLdb.escape_string(body)
        question['answer'] = MySQLdb.escape_string(answer)
        question['analysis'] = MySQLdb.escape_string(analysis)
        insert(question)

    print count , len(id_list),count * 1.0 / len(id_list)

        # break

if __name__ == '__main__':
    run('解答题')



