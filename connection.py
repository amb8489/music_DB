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


def close_connection():
    if connection is not None:
        connection.close()
        connection = None


def add_songs():
    import os
    directory = 'songs'
    sep = "<sep>"

    #    id:   0       1         2         3       4            5            6
    genres = {"rap": 0, "pop": 1, "country": 2, "R&B": 3, "rock": 4, "alternative": 5, "indie": 6}
    album_hist_seen = {}

    conn = get_connection()
    cur = conn.cursor()

    number_of_song_files_to_add = 2
    d = 0
    b = 0
    songid = 1
    for filename in os.listdir(directory):
        if d == number_of_song_files_to_add:
            return
        d += 1

        if filename.endswith(".txt"):
            path = directory + "/" + filename

            with open(path, "r") as f:
                for line in f:
                    song_data = f.readline().strip().split(sep)
                    # title , artist, length,album,year, genre
                    if len(song_data) >= 5:
                        title = song_data[0]
                        artist = song_data[1]
                        duration = song_data[2]
                        album = song_data[3]
                        year = song_data[4]
                        gen = song_data[5]
                        Uid = song_data[6]

                        if len(artist) > 100:
                            artist = artist[:100]

                        if len(album) > 100:
                            album = album[:100]

                        # --- sql to add dat NOTE: year is just the year this might
                        # be wrong in the db table ---

                        if len(title) < 50:

                            # adding songs
                            # place new user in db
                            # sql = "insert into song(songid,title, releasedate, length)"\
                            #       "values(%s,%s, %s, %s)"
                            #
                            # cur.execute(sql, (Uid,title,year,float(duration)))
                            #

                            # adding songs

                            # sql = "insert into songgenre(songid, genreid)"\
                            # "values((select songid from song where songid = %s),"\
                            # "(select genreid from genre where genre.genreid = %s))"
                            # cur.execute(sql, (Uid,genres[gen.strip()]))

                            # sql = "insert into artist(artistname)"\
                            #       " values(%s) on conflict do nothing"
                            # cur.execute(sql, (artist.strip(),))
                            #
                            #
                            # sql = "insert into songartist(songid,artistid)"\
                            #       "values((select songid from song where songid = %s),"\
                            #       "(select artistid from artist where artist.artistname = %s)) on conflict do nothing"
                            # cur.execute(sql, (Uid, artist.strip()))
                            #
                            #
                            #

                            # sql = "insert into album(albumname,releasedate,artistname)"\
                            #       " values(%s,%s,%s) on conflict do nothing"
                            # cur.execute(sql, (album.strip(),year,artist.strip()))

                            # name = album + artist.strip()
                            # if name in album_hist_seen:
                            #     album_hist_seen[name] += 1
                            # else:
                            #     album_hist_seen[name] = 1
                            #
                            #
                            #
                            # sql = "insert into albumcontains(albumid,songid,tracknumber)"\
                            #       " values((select albumid from album where albumname = %s and artistname = %s),"\
                            #       " (select songid from song where song.songid = %s),"\
                            #       " (%s))"
                            # cur.execute(sql, (album.strip(),artist.strip(),Uid, album_hist_seen[name]))

                            b += 1
                            if b > 9388:
                                return

                            conn.commit()
                            # songid +=1
                            # time.Sleep(10)

    cur.close()
