import mysql.connector


def connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="chungcudb"
    )


def get_all_apartments():
    db = connect()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name, area, price FROM apartment")
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data


def get_all_apartment_types():
    db = connect()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, type_name, description FROM apartment_type")
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data
