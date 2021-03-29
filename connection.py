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
    directory = 'songs'
    sep = "<sep>"

    number_of_song_files_to_add = 3
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

                    # --- sql to add dat NOTE: year is just the year this might
                    # be wrong in the db table ---
