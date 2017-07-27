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

pattern_a = re.compile(r'<span>A</span><span>([^B]*?)</span></p><p><span>B[、|．|\.]|<span>A([^B]*?)</span></p><p><span>B[、|．|\.]|<p>A([^B]*?)</p><p>B[、|．|\.]|<span>A([^B]*?)B[、|．|\.]|<p>A([^B]*?)B[、|．|\.]|A([^B]*?)B[、|．|\.]')
pattern_b = re.compile(r'<span>B</span><span>([^C]*?)</span></p><p><span>C[、|．|\.]|<span>B([^C]*?)</span></p><p><span>C[、|．|\.]|<p>B([^C]*?)</p><p>C[、|．|\.]|<span>B([^C]*?)C[、|．|\.]|<p>B([^C]*?)C[、|．|\.]|B([^C]*?)C[、|．|\.]')
pattern_c = re.compile(r'<span>C</span><span>([^D]*?)</span></p><p><span>D[、|．|\.]|<span>C([^D]*?)</span></p><p><span>D[、|．|\.]|<p>C([^D]*?)</p><p>D[、|．|\.]|<span>C([^D]*?)D[、|．|\.]|<p>C([^D]*?)D[、|．|\.]|C([^D]*?)D[、|．|\.]')
pattern_d = re.compile(r'D</span>(.*?)</p>|D(.*?)</p>')
pattern_answer = re.compile(ur'【解析】[\s\S]*?故选([ABCD]{1,4})|【解析】[\s\S]*?故选：([ABCD]{1,4})|【解析】[\s\S]*?故选择：([ABCD]{1,4})|【答案】[\s\S]*?[span <>/]{1,10}([ABCD]{1,4})[\s\S]*?【解析】|【答案】[\s\S]*?故选([ABCD]{1,4})|【答案】[\s\S]*?故答案为：([ABCD]{1,4})')
pattern_analysis = re.compile(ur'<font[\s\S]{0,10}color=\"red\">([\S\s]*?)</font>[\s]{0,}</div>[\s]{0,}</td>')
pattern_body = re.compile(r'<div style="display:block;[\s\S]*?display;none">([\s\S]*?)<p><span>A[、|．|\.]|<div style="display:block;[\s\S]*?display;none">([\s\S]*?)<p>A[、|．|\.]')

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
    if 0 < len(answer_):
        choices = [i for i in answer_[0] if len(i) > 0][0]
        return choices,analysis[0]
    else:
        print answer
        raise Exception('err')



def parse_analysis(analysis):
    """
        解析:解析
    """
    pass

def parse_body(body):
    """
        解析body
    """
    html = etree.HTML(body)
    table_list = html.xpath('//tr/td/table[@class="ques quesborder"]')
    if len(table_list) > 0:
        choices_table = table_list[0]
        choices_text = etree.tostring(choices_table,encoding='utf-8')
        choices = choices_table.xpath('tbody/tr/td/label')
        if len(choices) < 4:
            return
        for choice in choices:
            text = etree.tostring(choice,encoding='utf-8')
            if 'A．' in text:
                choices_a = text.split('A．')[1].split('</label>')[0]
                # print 'A',choice_a
            if 'B．' in text:
                choices_b = text.split('B．')[1].split('</label>')[0]
                # print 'B',choice_b
            if 'C．' in text:
                choices_c = text.split('C．')[1].split('</label>')[0]
                # print 'C',choice_c
            if 'D．' in text:
                choices_d = text.split('D．')[1].split('</label>')[0]
                # print 'D',choice_d
        td_list = html.xpath('//tr/td')
        text = etree.tostring(td_list[0],encoding='utf-8')
        body = text.split(choices_text)[0]
        body =  body.replace('<td height="38" width="619" style="">','').replace('<td height="38" width="619"   style=""  >','').strip('\n\r\t').rstrip('</td>','')
        return body.strip('\n\r\t '),choices_a,choices_b,choices_c,choices_d
    div_list = html.xpath('//tr/td/div')
    if len(div_list) == 0:
        td_list = html.xpath('//tr/td')
        if len(td_list) > 0:
            # print '===='* 20 , 2 ,'===='* 20
            text = etree.tostring(td_list[0],encoding='utf-8').replace('<td height="38" width="619" style="">','').replace('</td>','').strip('\n\r\t')
            if '<br />A．' in text:
                br = '<br />'
            else:
                br = '<br/>'
            body,choices = text.split('{br}A．'.format(br=br))[0:2]
            choices_a,choices = choices.split('{br}B．'.format(br=br))[0:2]
            choices_b,choices = choices.split('{br}C．'.format(br=br))[0:2]
            choices_c,choices = choices.split('{br}D．'.format(br=br))[0:2]
            choices_d = choices.split(br)[0]
            return body.strip('\n\r\t '),choices_a,choices_b,choices_c,choices_d
        else:
            raise Exception('error')
    else:
        text = etree.tostring(div_list[0],encoding='utf-8')
        body = [i for i in pattern_body.findall(text)[0] if len(i) > 0][0].replace('</span>','').replace('<span>','')
        choices_a = [i for i in pattern_a.findall(text)[0] if len(i) > 0][0].replace('</span>','').replace('<span>','').replace('<p>','\n').replace('</p>','\n')
        choices_b = [i for i in pattern_b.findall(text)[0] if len(i) > 0][0].replace('</span>','').replace('<span>','').replace('<p>','\n').replace('</p>','\n')
        choices_c = [i for i in pattern_c.findall(text)[0] if len(i) > 0][0].replace('</span>','').replace('<span>','').replace('<p>','\n').replace('</p>','\n')
        choices_d = [i for i in pattern_d.findall(text)[0] if len(i) > 0][0].replace('</span>','').replace('<span>','').replace('<p>','\n').replace('</p>','\n')
        return body,choices_a,choices_b,choices_c,choices_d

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
            body = question['body'].replace('<span >','<span>')
            body,choices_a,choices_b,choices_c,choices_d = parse_body(body)
            options = u''
            options += (u'''<tr id='a'><td>''' + choices_a.lstrip('.、．') + u'</td></tr>')
            options += (u'''<tr id='b'><td>''' + choices_b.lstrip('.、．') + u'</td></tr>')
            options += (u'''<tr id='c'><td>''' + choices_c.lstrip('.、．') + u'</td></tr>')
            options += (u'''<tr id='d'><td>''' + choices_d.lstrip('.、．') + u'</td></tr>')
            if len(options) > 0:
                options = u'''<table id='options'>''' + options + u'</table>'
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
        question['json'] = MySQLdb.escape_string(options)
        question['analysis'] = MySQLdb.escape_string(analysis)
        insert(question)

    print count , len(id_list),count * 1.0 / len(id_list)

        # break

if __name__ == '__main__':
    run('单选题')



