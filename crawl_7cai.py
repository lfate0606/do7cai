# coding:utf-8
"""
	爬取7cai
"""
import requests
import json
from bs4 import BeautifulSoup
import codecs
import os
from urlparse import urljoin
from lxml import etree
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def _crawl_knowledge(url, data=None):
    resp = requests.post(url, data)
    print resp.text
    knowledge_list = json.loads(resp.text.replace("'",'"'))
    for knowledge in knowledge_list:
        if knowledge['isLeaf'] is False:
            data["pid"] = knowledge['id']
            data["id"] = knowledge['id']
            knowledge['children'] = _crawl_knowledge(url, data=data)
        else:
            knowledge['url'] = url
            knowledge['data'] = data
    return knowledge_list



def crawl_knowledge():
    if os.path.exists('subject_list.json'):
        with open('subject_list.json', 'r') as f:
            subject_list = json.load(f)
    for subject in subject_list:
        print subject
        data = {
				"pageIndex": 0,
				"pageSize": 0,
				"pageSize": 0,
				"sortField": 0,
				"sortOrder": 0,
				"pid": 0,
				"id": 0,
		}
        url = subject['knowledge_url']
        subject["knowledge_tree"] = _crawl_knowledge(url,data=data)
        knowledge_tree = subject['knowledge_tree']
        with codecs.open('%s%s.json' % (subject['stage'],subject['subject']), 'w', encoding='utf-8') as f:
            json.dump(knowledge_tree, f, encoding="utf-8", indent=2,ensure_ascii=False) 
    with codecs.open('subject_list.json', 'w', encoding='utf-8') as f:
        json.dump(subject_list, f, encoding="utf-8", indent=2,ensure_ascii=False)
    return subject_list



def crawl_grade():
	pass

def check_list(content):
    if  len(content) > 4500:
        return True
    else:
        return False


def _craw_list(url,knowledge,grade_list):
    if knowledge['isLeaf'] is False:
        for child in knowledge['children']:
            _craw_list(url, child, grade_list)
    else:
        for grade in grade_list:
            for page in xrange(1,101):
                file_path = "list/%s_%s_%s.html" % (knowledge['id'],grade,page)
                if os.path.exists(file_path):
                    if 'list' in knowledge.keys() and file_path not in knowledge['list']:
                        knowledge['list'].append(file_path)
                    else:
                        knowledge['list'] = [file_path]
                    continue
                r_url = url + "?page={page}&STCCSF=&GradeID={grade}&STTypeID=&School=&STCCName=&KP={kp}&ZJID=&STTX=&STLeavel=&x=?randnum=0.42159312474573407"
                resp = requests.get(r_url.format(kp=knowledge['id'],page=page,grade=grade))
                print r_url.format(kp=knowledge['id'],page=page,grade=grade)
                if check_list(resp.text) is False:
                    break
                with codecs.open( file_path , 'wb', encoding="utf-8") as f:
                    f.write(resp.text)
                if 'list' in knowledge.keys() and file_path not in knowledge['list']:
                    knowledge['list'].append(file_path)
                else:
                    knowledge['list'] = [file_path]

def save(subject_list):
    with codecs.open('subject_list.json', 'w', encoding='utf-8') as f:
        json.dump(subject_list, f, encoding="utf-8", indent=2,ensure_ascii=False)                



def crawl_list(subject):
    if os.path.exists('%s%s.json' % (subject['stage'],subject['subject'])):
        with open('%s%s.json' % (subject['stage'],subject['subject']), 'r') as f:
             knowledge_tree = json.load(f)
    if subject['stage'] ==u'高中':
        grade_list = ['G003',"G002","G001"]
    elif subject["stage"] == u'初中':
        grade_list = ['G010',"G020","G030"]
    else:
        grade_list = ['G002',"G002","G001"]
    for knowledge in knowledge_tree:
        print subject['subject']
        _craw_list(subject['list_url'],knowledge,grade_list)
        with codecs.open('%s%s.json' % (subject['stage'],subject['subject']), 'w', encoding='utf-8') as f:
            json.dump(knowledge_tree, f, encoding="utf-8", indent=2,ensure_ascii=False) 
    with codecs.open('%s%s.json' % (subject['stage'],subject['subject']), 'w', encoding='utf-8') as f:
            json.dump(knowledge_tree, f, encoding="utf-8", indent=2,ensure_ascii=False) 


def run(subject_list=['高中语文']):
	pass



if __name__ == '__main__':
    # crawl_knowledge()
    # crawl_list()
    args = sys.argv
    if os.path.exists('subject_list.json'):
        with open('subject_list.json', 'r') as f:
            subject_list = json.load(f)
    if args[1] == 'knowledge':
        crawl_knowledge()
        sys.exit(0)
    if len(args) < 2:
        print """
        python crawl_7cai.py 高中 数学
        """
        sys.exit(0)
    subject_name = args[2]
    subject_stage = args[1]
    subject_name =  subject_name.decode('utf-8')
    subject_stage =  subject_stage.decode('utf-8')
    for subject in subject_list:
        if subject['subject'] == unicode(subject_name) and subject['stage']==unicode(subject_stage):
            crawl_list(subject)


