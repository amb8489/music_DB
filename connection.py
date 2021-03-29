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




def add_songs():
    import os
    import sys
    import random
    import time
    directory = 'songs'
    sep = "<sep>"

    conn = get_connection()
    cur = conn.cursor()

    number_of_song_files_to_add = 2
    d = 0
    for filename in os.listdir(directory):
        if d == number_of_song_files_to_add:
            return
        d+=1

        if filename.endswith(".txt"):
            path =directory+"/"+filename

            with open(path,"r") as f:
                for line in f:
                    song_data = f.readline().strip().split(sep)
                    # title , artist, length,album,year, genre

                    title =    song_data[0]
                    artist =   song_data[1]
                    duration = song_data[2]
                    album =    song_data[3]
                    year =     song_data[4]
                    genre =    song_data[5]
                    month = random.randint(1,12)

                    if month < 10:
                        year+="-0"+str(month)
                    else:
                        year+="-"+str(month)


                    day = random.randint(10,30)
                    if month == 2:
                        day%=27
                        day+=1

                    day = str(day)
                    year+="-"
                    year+=day
                    # --- sql to add dat NOTE: year is just the year this might
                    # be wrong in the db table ---


                    if len(title)<50:
                        # place new user in db
                        sql = "insert into song(title, releasedate, length)"\
                              "values(%s, %s, %s)"

                        cur.execute(sql, (title,year,float(duration)))
                        conn.commit()
    cur.close()
