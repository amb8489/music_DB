import psycopg2

connection = None


def connect():
    global connection
    connection = psycopg2.connect(
        host="reddwarf.cs.rit.edu",
        database="p320_03a",
        user="p320_03a",
        password="gslAMAqn0xcx"
    )


def get_connection():
    if not connection:
        connect()
    return connection
