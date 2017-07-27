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

def insert(list_path, knowledge):
    i_sql = u"insert into link_knowledge(question_id,knowledge_id)select a.id as quesiton_id , b.id as knowledge_id from knowledge as b ,question as a where b.uid ='{uid}' and a.list_path='{list_path}'  on Duplicate key update question_id=question_id;"
    i_sql =i_sql.format(list_path=list_path,uid=knowledge['id'])
    print i_sql
    db_helper.execute(i_sql)
    


def import_db(subject,knowledge_list):
    for knowledge in knowledge_list:
        if knowledge['isLeaf'] is True:
            link_knowledge = dict()
            if 'list' not in knowledge.keys():
                continue
            list_path_list = knowledge['list']
            for list_path in list_path_list:
                list_path = './%s' % list_path
                insert(list_path,knowledge)
        else:
            if 'children' in knowledge.keys():
                import_db(subject,knowledge['children'])

if __name__ == '__main__':
    subject_list= get_subject()
    for subject in subject_list:
        knowledge_list  = get_knowledge(file_path='%s%s.json' % (subject['stage'],subject['subject']))
        import_db(subject,knowledge_list)





