#coding:utf-8
"""
    导出到知识点
"""
import json
import db_helper
from  requests import Session
from urlparse import urljoin
from  redis import StrictRedis
from hashlib import md5
import re
import MySQLdb
import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')

redis = StrictRedis('localhost',db=3)

re_pattern = re.compile(r'''<div style="display:block;[\s]{2,13}display:none;">[\s\S]*?</div>|alt="[^<>"]*?"|&#13;|style="font-family:宋体; font-size:10.5pt"''')

def get_question_id_list(stage='语文',subject='数学',type='选择题'):
    sql = "select a.id as id from question as a join link_knowledge as b on a.type='{type}' and a.id=b.question_id  join knowledge as c on b.knowledge_id=c.id where c.stage='{stage}' and c.subject='{subject}' order by a.id"
    
    if type is None:
        sql = "select b.question_id as id from knowledge as c  join link_knowledge as b on b.knowledge_id=c.id where c.stage='{stage}' and c.subject='{subject}' order by b.question_id "
    f_sql = sql.format(stage=stage,subject=subject,type=type)
    ids= db_helper.query_all(f_sql)
    id_list = [id['id'] for id in ids]
    return id_list

def get_question(id):
    sql = "select  answer from question where id={id}".format(id=id)
    quesiton = db_helper.query_one(sql)
    return quesiton



def update_question(question):
    sql = "update question set answer='{answer}' ,analysis='{analysis}' where id={id}"
    db_helper.execute(sql.format(**question))

def split(answer):
    if answer is None:
        return None
    if '【答案】' in answer:
        answer = answer.split('【答案】')[1]
    analysis = None
    if '【解析】' in answer:
        _anwser = answer.split('【解析】')[0]
        analysis = answer.replace(_anwser,'')
        answer = _anwser
    elif '【解析】' in answer:
        _anwser = answer.split('【解析】')[0]
        analysis = answer.replace(_anwser,'')
        answer = _anwser
    elif '【</span><span >解析</span><span >】' in answer:
        _anwser = answer.split('【</span><span >解析</span><span >】')[0]
        analysis = answer.replace(_anwser,'')
        answer = _anwser
    elif '【解析</span><span >】' in answer:
        _anwser = answer.split('【解析</span><span >】')[0]
        analysis = answer.replace(_anwser,'')
        answer = _anwser
    if analysis is None:
        if '考点:' in answer:
            answer = answer.split('考点:')[0]
        if '</font>' in answer:
            answer = answer.split('</font>')[0]
        if '解析' in answer:
            raise Exception('解析error')
        #print '答案==== ', answer
        return 
    #print '答案==== ', answer
    if '考点:' in analysis:
        analysis = analysis.split('考点:')[0]
    if '</font>' in analysis:
        analysis = analysis.split('</font>')[0]
    #print '解析==== ', analysis





def run(stage,subject,type):
    with open('subject_list.json','rb') as f:
        subject_list = json.load(f)
    _subject = None
    for sub in subject_list:
        if sub['stage'] == stage and sub['subject'] == subject:
            _subject = sub
    if _subject is None:
        return 
    id_list = get_question_id_list(stage,subject,type)
    for id in id_list:
        if redis.get(id) is None:
            try:
                redis.set(id,0)
                question = get_question(id)
                if question is None:
                    continue
                _question = split(question['answer'])
                if _question is None:
                    continue
                else:
                    _question['id'] = question['id']
                    update_question(_question)
                    redis.set(id,1)
                    del id
            except Exception as e:
                print e
                redis.delete(id)
                del id
                print question['answer']
                _continue = raw_input("continue")
                if _continue != 'exit':
                    pass
                else:
                    sys.exit(0)

def init_id():
    for i in range(10):
        key = '%s*' % i
        ids = redis.keys(key)
        for id in ids:
            redis.delete(id)




if __name__ == '__main__':
    args = sys.argv 
    if args[1] == 'init_id':
        init_id()
        sys.exit(0)
    if len(args) < 3:
        print """
            python crawl_7cai_image.py 高中 数学 选择题
            python crawl_7cai_image.py 高中 数学
        """
        sys.exit(0)
    if len(args) >= 3:
        stage = args[1]
        subject = args[2]
    if len(args) > 3:
        type = args[3]
    else:
        type = None
    run(stage,subject,type)






