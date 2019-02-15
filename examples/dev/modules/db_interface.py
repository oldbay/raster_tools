#! /usr/bin/python2
# -*- coding: utf-8 -*-

import psycopg2


class psql(object):
    """
    Простой класс подключения и работы с
    базой данных в PostgreSQL:
    dbhost = СУБД хост
    dbname = имя БД
    dbuser = пользователь
    dbpass = пароль
    """

    def __init__(self, **kwargs):
        connString = "host={0} dbname={1} user={2} password={3}".format(
            kwargs["dbhost"],
            kwargs["dbname"],
            kwargs["dbuser"],
            kwargs["dbpass"]
        )
        self.conn = psycopg2.connect(connString)
        self.cur = self.conn.cursor()

    def sql(self, _sql):
        self.cur.execute(_sql)

    def commit(self):
        self.conn.commit()

    def autocommit(self, _aut=False):
        self.conn.autocommit = _aut

    def fetchone(self):
        return self.cur.fetchone()

    def fetchall(self):
        return self.cur.fetchall()

    def close(self):
        self.commit()
        self.cur.close()
        self.conn.close()

    def __call__(self):
        return self.cur
