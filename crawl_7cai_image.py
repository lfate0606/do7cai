#coding:utf-8
"""
    获取图片
"""
import json
import db_helper
from  requests import Session
from urlparse import urljoin
from  redis import StrictRedis
from hashlib import md5
import re
import MySQLdb
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

redis = StrictRedis('localhost',db=1)


def crawl(session, url_list,subject):
    base_path = "%s%s/" % (subject['stage'],subject['subject'])
    base_url = subject['list_url']
    image_dir = 'images'
    url_file_name_dict = dict()
    url_list = set(url_list)
    for url in url_list:
        retry = 15
        image_url = urljoin(base_url,url)
        while retry>0:
            retry -= 1
            if redis.get(image_url) is None:
                redis.set(image_url,'0')
                resp = session.get(image_url)
                print resp.status_code 
                if resp.status_code != 200:
                    redis.delete(image_url)
                    print resp.status_code 
                    continue
                md5_value = md5(resp.content).hexdigest()
                if md5_value == '70eba11b6c6201e5e50934ff8d14c2ba':
                    print md5_value
                    redis.delete(image_url)
                    continue
                file_name = "%s/%s.png" % (image_dir,md5_value)
                with open(file_name,'wb') as f:
                    f.write(resp.content)
                redis.set(image_url,file_name)
                url_file_name_dict[url] = file_name
                retry = 0
            else:
                file_name = str(redis.get(image_url))
                if file_name.startswith('images'):
                    url_file_name_dict[url] = file_name
                    retry = 0
                else:
                    redis.delete(image_url)
                    print 'error:', image_url
    return url_file_name_dict

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
    sql = "select  body,answer,analysis from question where id={id}".format(id=id)
    quesiton = db_helper.query_one(sql)
    return quesiton

def replace(value,image_dict):
    _value = value
    for key, v in image_dict.iteritems():
        print key, v 
        _value = _value.replace(key,v)
    return _value

def get_url_list(content):
    if content is None:
        return []
    pattern = re.compile(r'<img[\s\S]+?src="([\s\S]+?)"')
    url_list = pattern.findall(content)
    return [url for url in url_list if not url.startswith('images/') and len(url) != 43]


def update_question(question):
    sql = "update question set body='{body}', answer='{answer}' ,analysis='{analysis}' where id={id}"
    db_helper.execute(sql.format(**question))



def run(stage,subject,type):
    session = Session()
    with open('subject_list.json','rb') as f:
        subject_list = json.load(f)
    _subject = None
    for sub in subject_list:
        if sub['stage'] == stage and sub['subject'] == subject:
            _subject = sub
    if _subject is None:
        return 
    session.headers.update({'Accept-Language': 'zh-CN,zh;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36', 'Connection': 'keep-alive', 'Referer': _subject['list_url']})
    id_list = get_question_id_list(stage,subject,type)
    for id in id_list:
        if redis.get(id) is None:
            try:
                redis.set(id,0)
                question = get_question(id)
                _question = dict()
                change = False
                for key,value in question.iteritems():
                    url_list = get_url_list(value)
                    image_dict = crawl(session,url_list,_subject)
                    if len(image_dict) != 0:
                        change = True
                    _question[key] = replace(value,image_dict)
                    if _question[key] is not None:
                        _question[key] = MySQLdb.escape_string(_question[key])
                _question['id'] = id
                if change:
                    update_question(_question)
                redis.set(id,1)
                del id
            except Exception as e:
                redis.delete(id)
                del id
                session = Session()
                session.headers.update({'Accept-Language': 'zh-CN,zh;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36', 'Connection': 'keep-alive', 'Referer': _subject['list_url']})

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






