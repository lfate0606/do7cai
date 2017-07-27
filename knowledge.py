#coding:utf-8
"""
    导出到知识点
"""
import json
import db_helper

def get_subject(file_path="subject_list.json"):
    with open(file_path,'r') as f:
        subject_list = json.load(f)
    return subject_list

def get_knowledge(file_path='初中历史.json'):
    with open(file_path,'r') as f:
        knowledge_list = json.load(f)
    return knowledge_list

def insert(knowledge):
    i_sql = u"insert into knowledge(uid,pid,puid,knowledge,ischild,stage,subject) values('{uid}',{pid},'{puid}','{knowledge}',{ischild},'{stage}','{subject}') on Duplicate key update uid='{uid}';"
    print i_sql.format(**knowledge)
    db_helper.execute(i_sql.format(**knowledge))
    s_sql = u"select id from knowledge where uid = '{uid}'".format(**knowledge)
    _id = db_helper.query_one(s_sql)
    return _id['id']

def import_db(subject,knowledge_list,pid,puid):
    for knowledge in knowledge_list:
        knowledge['pid'] = pid
        knowledge['puid'] = puid
        knowledge['uid'] = knowledge['id']
        knowledge['ischild'] = knowledge['isLeaf']
        knowledge['knowledge'] = knowledge['text']
        knowledge['subject'] = subject['subject']
        knowledge['stage'] = subject['stage']
        _pid = insert(knowledge)
        if 'children' in knowledge.keys():
            import_db(subject,knowledge['children'],_pid,knowledge['uid'])

if __name__ == '__main__':
    subject_list= get_subject()
    for subject in subject_list:
        print '\n'
        print subject['stage'],subject['subject']
        knowledge_list  = get_knowledge(file_path='%s%s.json' % (subject['stage'],subject['subject']))
        import_db(subject,knowledge_list,0,0)





