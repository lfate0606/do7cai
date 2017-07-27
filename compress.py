#coding:utf-8
"""
    压缩数据,去除多余的html代码
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

redis = StrictRedis('localhost',db=2)
one=False
re_pattern = re.compile(r'''([\S\s]*)<font|</font>([\s\S]*)''')
#re_pattern = re.compile(r"style=\"font-family:[^\"]{2,20}?font-size:[\d\.]{1,5}pt[^\"]{0,30}?\"|&#13;|满分5|满分网|manfen5.com|border-[\S\s]{0,5}?-width: [\d\.]{1,4}px;|font-family:[\s\S]{2,10}?;|font-size:[\d\.]{1,4}?pt|<div[\s]{0,20}?style=\"display:block;[\s]{1,13}?display:none;\">[\s\S]*?</div>|alt=\"[\S\s]{1,40}?\"|colspan=\"[\d]{0,10}?\"|id=\"[^\"]*?\"|onclick=\"showSTDA\(\'[\S\s]*?\'\)\"|ondragstart=\"[\s\S]*?\"|<span> </span>")

def get_question_id_list(stage='语文',subject='数学',type='选择题'):
    sql = "select a.id as id from question as a join link_knowledge as b on a.id=b.question_id join knowledge as c on b.knowledge_id=c.id where c.stage='{stage}' and c.subject='{subject}' "
    if type is None:
        sql = "select b.question_id as id from knowledge as c  join link_knowledge as b on b.knowledge_id=c.id where c.stage='{stage}' and c.subject='{subject}' order by b.question_id "
    else:
        sql += " and a.type='{type}' order by a.question_id"
    f_sql = sql.format(stage=stage,subject=subject,type=type)
    ids= db_helper.query_all(f_sql)
    id_list = [id['id'] for id in ids]
    return id_list

def get_question(id):
    sql = "select  body,answer from question where id={id}".format(id=id)
    quesiton = db_helper.query_one(sql)
    return quesiton

def replace(value,str_list):
    _value = value
    for str_str in str_list:
        _value = _value.replace(str_str,'')
    return _value

def get_replace_str(content):
    if content is None:
        return []
    replace_list = re_pattern.findall(content)
    _replace_list = list()
    for re in replace_list:
        if isinstance(re,tuple):
            _replace_list.extend(list(re))
        else:
            _replace_list.append(re)
    print '='*10 ,"len:", len(_replace_list) 
    _replace_list = list(set(_replace_list))
    return sorted(_replace_list, key=len,reverse=True)


def update_question(question):
    sql = "update question set body='{body}', answer='{answer}' where id={id}"
    db_helper.execute(sql.format(**question))



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
                _question = dict()
                change = False
                for key,value in question.iteritems():
                    url_list = get_replace_str(value)
                    for url in url_list:
                        print url
                    if url_list is not None and len(url_list) > 0:
                        change = True
                    print '=='*30 ,'qlen ', len(value)
                    _question[key] = replace(value,url_list)
                    print '=='*30 ,'_qlen ', len(_question[key])
                    print _question.keys()
                    if _question[key] is not None:
                        _question[key] = MySQLdb.escape_string(_question[key])
                _question['id'] = id
                if change:
                    update_question(_question)
                redis.set(id,1)
                del id
            except Exception as e:
                print 'hi', e
                redis.delete(id)
                del id
#            time.sleep(2)
            if one:
                break

def init_id():
    for i in range(10):
        key = '%s*' % i
        ids = redis.keys(key)
        for id in ids:
            redis.delete(id)

def init_image():
    keys = redis.keys('http*')
    for key in keys:
        value = redis.get(key)
        if value == '0' or  value==0 or value==-1 or value=='-1':
            redis.delete(key)



if __name__ == '__main__':
    args = sys.argv 
    if args[1] == 'init_id':
        init_id()
        sys.exit(0)
    if args[1] == 'init_image':
        init_image()
        sys.exit(0)
    if len(args) < 3:
        print """
            python compress.py 高中 数学 选择题
            python compress.py 高中 数学
        """
        sys.exit(0)
    if len(args) >= 3:
        stage = args[1]
        subject = args[2]
    if len(args) > 3 and args[3] != 'one':
        type = args[3]
    else:
        type = None
    if 'one' in args:
        global one
        one =True
    run(stage,subject,type)






