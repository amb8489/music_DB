import psycopg2
from dbinfo import info

connection = None


def connect():
    global connection
    connection = psycopg2.connect(
        host=info["host"],
        database=info["database"],
        user=info["user"],
        password=info["password"]
    )


def get_connection():
    if not connection:
        connect()
    return connection
