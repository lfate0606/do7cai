# encoding: utf-8

import MySQLdb
from DBUtils.PooledDB import PooledDB
from MySQLdb.cursors import DictCursor

mysql_config = {
        "host": "localhost",
        "passwd": "root",
        "user": "",
        "port": 3306,
        "db": "docai",
        "charset": "utf8",
}


# mysql  数据库连接池
pool = PooledDB(MySQLdb, **mysql_config)


def transaction(func):
    """
        数据库处理事务
    """

    def _transaction(sql, _type='dict'):
        print sql
        db = pool.connection()
        if _type == 'dict':
            cursor = db.cursor(DictCursor)
        else:
            cursor = db.cursor()
        try:
            data = func(cursor, sql)
            db.commit()
            cursor.close
            return data
        except Exception as e:
            db.rollback()
            raise e

    return _transaction


@transaction
def query_one(cursor, sql, _type='dict'):
    cursor.execute(sql)
    return cursor.fetchone()


@transaction
def query_all(cursor, sql, _type='dict'):
    cursor.execute(sql)
    return cursor.fetchall()


@transaction
def execute(cursor, sql):
    return cursor.execute(sql)


def test_query_one():
    sql = "select id from  basic_question WHERE id = 100000000000000"
    data = query_one(sql)
    if isinstance(data, dict):
        pass
    else:
        assert False


def test_query_all():
    sql = "select id from basic_question limit 1"
    data = query_all(sql)
    if isinstance(data, tuple):
        pass
    else:
        assert False


if __name__ == '__main__':
    test_query_one()
