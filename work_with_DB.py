# -*- coding: utf-8 -*-
import pymysql
import config

# Функция для изменения каких-либо данных, если понадобится
def edit(*commands):
    try:
        db = pymysql.connect(host=config.host, user=config.user, passwd=config.passwd, db=config.db, charset='utf8mb4')
        cur = db.cursor()
        for command in commands:
            cur.execute(command)
        db.commit()
        cur.close()
        db.close()
    except:
        print("Some errors while i try edit DB")


#Функция регистрации. Вносит в Базу уникальный логин и hash пароля
def register(login, password, tg_id):
    try:
        db = pymysql.connect(host=config.host, user=config.user, passwd=config.passwd, db=config.db, charset='utf8mb4')
        cur = db.cursor()
        sql = "INSERT INTO users (`Login`, `Password`, `TelegramID`) VALUES (%s, %s, %s)"
        cur.execute(sql, (login, password, tg_id))
        db.commit()
        cur.close()
        db.close()
    except:
        print("Some Errors in register func DB")


def new_quiz(question, answer):
    try:
        db = pymysql.connect(host=config.host, user=config.user, passwd=config.passwd, db=config.db, charset='utf8mb4')
        cur = db.cursor()
        sql = "INSERT INTO quiz (`Question`, `Answer`) VALUES (%s, %s)"
        cur.execute(sql, (question, answer))
        db.commit()
        cur.close()
        db.close()
    except:
        print("Some Errors in new_quiz func DB")


# Обычная функция для выборки из БД
def select(command):
    conn = pymysql.connect(host=config.host, user=config.user, passwd=config.passwd, db=config.db, charset='utf8mb4')
    cur = conn.cursor()
    cur.execute(command)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data