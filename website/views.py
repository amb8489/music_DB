from flask import Blueprint, render_template, request, session

from connection import get_connection

views = Blueprint('views', __name__)


# the home page
@views.route("/")
def home():
    return render_template("home.html")


# the user page
@views.route("/userpage")
def userpage():
    # getting and saving new data
    user_data = request.args['user_data']
    user_data = session['user_data']
    session['user_data'] = user_data
    user_data["searched_friend"] = "None"

    return render_template("userpage.html", user_data=user_data)


@views.route('/addtoplaylist/', methods=['POST', 'GET'])
def add_song_to_playlist():
    """
    function to add song to playlist
    :return:
    """

    if request.method == 'GET':
        return render_template('userpage.html')
    if request.method == 'POST':
        # geting form data
        user_data = session['user_data']

        songid = request.form["songid"].split("<sep>")

        add_album = songid[1]
        if add_album == "True":

            playlistname = request.form['currentplaylist']

            albumInfo = request.form["songid"].split("<sep>")

            print("ALBUM INFO:",albumInfo)
            user_data = session['user_data']
            userid = user_data['id']


            conn = get_connection()
            cur = conn.cursor()

            # getting getting album id

            sql = "select collectionid " \
                  "from collection " \
                  "where name = %s and userid = %s"
            cur.execute(sql, (playlistname, userid))
            playlistid = cur.fetchone()

            sql = "select albumid " \
                  "from album " \
                  "where albumname = %s and artistname = %s"
            cur.execute(sql, (albumInfo[0],albumInfo[2]))

            albumID = cur.fetchone()


            sql = "insert into collectionalbum(collectionid,albumid)" \
                      "values(%s, %s)"
            cur.execute(sql, (playlistid,albumID))
            conn.commit()
            cur.close()

            session['user_data'] = user_data

        else:
            conn = get_connection()
            cur = conn.cursor()
            playlistname = request.form['currentplaylist']
            userid = user_data["id"]

            sql = "select collectionid " \
                  "from collection " \
                  "where name = %s and userid = %s"
            cur.execute(sql, (playlistname, userid))
            playlistid = cur.fetchone()

            sql = "insert into collectionsong(collectionid,songid)" \
                  "values(%s, %s) on conflict do nothing"
            cur.execute(sql, (playlistid, songid[0]))
            conn.commit()

            for playlist_name in user_data["playlist_name"]:
                sql = " SELECT songid,title,length FROM song WHERE songid IN " \
                      "(SELECT songid FROM collectionsong WHERE collectionid IN " \
                      "(SELECT collectionid FROM collection where name = %s AND userid = %s)) "
                cur.execute(sql, (playlist_name, userid))
                songs = cur.fetchall()
                user_data[playlist_name] = [round(sum([song[2] for song in songs]) / 60, 2), len(songs)]

            conn.commit()
            cur.close()

            user_data["explore"] = True
            user_data["myAlbums"] = False
            session['user_data'] = user_data

    return render_template('userpage.html', user_data=user_data)


@views.route('/deletefromplaylist/', methods=['POST', 'GET'])
def delete_song_from_playlist():
    """
    function to delete song from playlist
    :return:
    """

    if request.method == 'GET':
        return render_template('userpage.html')
    if request.method == 'POST':
        # geting form data
        user_data = session['user_data']
        userid = user_data["id"]
        songid = request.form["songid"]
        playlistname = user_data["current_playlist_name"]

        conn = get_connection()
        cur = conn.cursor()

        sql = "select collectionid " \
              "from collection " \
              "where name = %s and userid = %s"
        cur.execute(sql, (playlistname, userid))
        playlistid = cur.fetchone()

        sql = "delete from collectionsong " \
              "where collectionid = %s and songid = %s"
        cur.execute(sql, (playlistid, songid))
        conn.commit()

        for playlist_name in user_data["playlist_name"]:
            sql = " SELECT songid,title,length FROM song WHERE songid IN " \
                  "(SELECT songid FROM collectionsong WHERE collectionid IN " \
                  "(SELECT collectionid FROM collection where name = %s AND userid = %s)) "
            cur.execute(sql, (playlist_name, userid))
            songs = cur.fetchall()
            user_data[playlist_name] = [round(sum([song[2] for song in songs]) / 60, 2), len(songs)]

        cur.close()

        user_data["explore"] = False
        user_data["myAlbums"] = True
        session['user_data'] = user_data

    return render_template('userpage.html', user_data=user_data)


@views.route('/removeplaylist/', methods=['POST', 'GET'])
def remove_playlist():
    if request.method == 'GET':
        return render_template('userpage.html')
    if request.method == 'POST':
        rmplaylist_name = request.form["rmplaylist"]

        print("----+++++++++++++", rmplaylist_name)
        user_data = session['user_data']
        user_data["playlist_name"].remove(rmplaylist_name)
        user_data["current_playlist_length"] = 0
        user_data["current_playlist_number"] = 0

        conn = get_connection()
        cur = conn.cursor()
        sql = "SELECT collectionid FROM collection WHERE name = %s "
        cur.execute(sql, (rmplaylist_name,))
        collectionID = cur.fetchone()[0]

        sql = "DELETE FROM collectionsong WHERE collectionid = %s "
        cur.execute(sql, (collectionID,))

        sql = "DELETE FROM collection WHERE collectionid = %s "
        cur.execute(sql, (collectionID,))
        user_data["current_playlist"] = []

        conn.commit()
        cur.close()
        user_data["explore"] = False
        user_data["myAlbums"] = True
        session['user_data'] = user_data
        return render_template('userpage.html', user_data=user_data)


@views.route('/getplaylist/', methods=['POST', 'GET'])
def get_playlist():
    if request.method == 'GET':
        return render_template('userpage.html')
    if request.method == 'POST':
        # getttting form data
        playlist_name = request.form["playlist"]

        user_data = session['user_data']
        userID = user_data["id"]

        conn = get_connection()
        cur = conn.cursor()
        sql = " SELECT songid,title,length FROM song WHERE songid IN " \
              "(SELECT songid FROM collectionsong WHERE collectionid IN " \
              "(SELECT collectionid FROM collection where name = %s AND userid = %s)) "
        cur.execute(sql, (playlist_name, userID))
        songs = cur.fetchall()



        sql = "SELECT collectionid FROM collection WHERE name = %s AND userid = %s"
        cur.execute(sql, (playlist_name, userID))
        collectionid = cur.fetchone()


        #getting all albums
        sql = "SELECT albumname FROM album WHERE albumid = (SELECT albumid FROM collectionalbum WHERE collectionid = %s)"

        cur.execute(sql, (collectionid,))
        albumnames  = cur.fetchall()


        albumnames = [name[0] for name in albumnames]


        user_data["current_albums"] = albumnames
        user_data["current_playlist"] = songs


        user_data["current_playlist_name"] = playlist_name

        user_data["current_playlist_length"] = round(sum([song[2] for song in songs]) / 60, 2)
        user_data["current_playlist_number"] = len(songs)

        user_data["myAlbums"] = True
        user_data["explore"] = False
        session['user_data'] = user_data

    return render_template('userpage.html', user_data=user_data)


@views.route('/makenewplaylists/', methods=['POST', 'GET'])
def make_new_playlist():
    """
    function to make a new empty playlist
    :return:
    """

    if request.method == 'GET':
        return render_template('userpage.html')
    if request.method == 'POST':
        # getting form data
        form_data = request.form
        user_data = session['user_data']

        new_playlist_name = form_data["playlist_name"]

        userID = user_data["id"]

        conn = get_connection()
        cur = conn.cursor()
        # making new collection in db
        sql = "insert into collection(name,userid) " \
              "values(%s, %s) RETURNING collectionid"
        cur.execute(sql, (new_playlist_name, userID))
        playlistID = cur.fetchone()[0]

        conn.commit()
        cur.close()

        user_data["playlist_name"].append(new_playlist_name)
        print(user_data["playlist_name"])
        user_data["new_playlist_id"] = playlistID
        user_data["explore"] = True
        user_data["myAlbums"] = False

        session['user_data'] = user_data

        return render_template('userpage.html', user_data=user_data)


@views.route('/renamecollection/', methods=['POST', 'GET'])
def rename_collection():
    """
    route to rename a collection
    :return:
    """
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        form_data = request.form

        user_data = session['user_data']
        playlist = user_data['current_playlist_name']
        new_name = form_data['new_name']
        userid = user_data["id"]

        conn = get_connection()
        cur = conn.cursor()

        sql = "update collection " \
              "set name = %s " \
              "where name = %s and userid = %s"
        cur.execute(sql, (new_name, playlist, userid))
        user_data["current_playlist_name"] = new_name
        conn.commit()

        sql = "SELECT ALL name FROM collection where userid = %s"
        cur.execute(sql, (user_data["id"],))
        all_playlists = cur.fetchall()
        user_data["playlist_name"] = [name[0] for name in all_playlists]

        cur.close()
        session['user_data'] = user_data

        return render_template('userpage.html', user_data=user_data)


@views.route('/searchedsong/', methods=['POST', 'GET'])
def searched_song():
    """
    function to get a searched song
    :return:
    """

    if request.method == 'GET':
        return render_template('userpage.html')
    if request.method == 'POST':
        # getting form data
        form_data = request.form
        search_text = form_data["song_name"]

        # how we want to search for song by
        filter_selected = form_data['options']
        amount_of_songs = form_data['amount']

        sort_by = form_data['sort']

        user_data = session['user_data']
        user_id = user_data["id"]

        conn = get_connection()
        cur = conn.cursor()

        result = None  # get outer scope

        if sort_by == "song":
            sort_sql = " order by song.title, artist.artistname"
        elif sort_by == "genre":
            sort_sql = "  order by genre.genrename"
        elif sort_by == "artist":
            sort_sql = "  order by artist.artistname"
        else:
            sort_sql = "  order by song.releasedate"

        # FILTER_SELECTED IS USED TO GET THE SONGS (in 'result'), THEN THE SHARED 'IF' BELOW IS USED
        if filter_selected == "title":
            sql = "select song.songid, song.title, song.length, artist.artistname, " \
                  "album.albumname, genre.genrename, song.releasedate, userplayssong.playcount " \
                  "from song inner join songartist on song.songid = songartist.songid " \
                  "and song.title = %s " \
                  "inner join artist on songartist.artistid = artist.artistid " \
                  "inner join albumcontains on song.songid = albumcontains.songid " \
                  "inner join album on albumcontains.albumid = album.albumid " \
                  "inner join songgenre on song.songid = songgenre.songid " \
                  "inner join genre on songgenre.genreid = genre.genreid " \
                  "left outer join userplayssong on song.songid = userplayssong.songid " \
                  "and userplayssong.userid = %s  " + sort_sql

            cur.execute(sql, (search_text, user_id))
            result = cur.fetchall()

        elif filter_selected == "genre":
            sql = "select song.songid, song.title, song.length, artist.artistname, " \
                  "album.albumname, genre.genrename, song.releasedate, userplayssong.playcount " \
                  "from song inner join songartist on song.songid = songartist.songid " \
                  "inner join artist on songartist.artistid = artist.artistid " \
                  "inner join albumcontains on song.songid = albumcontains.songid " \
                  "inner join album on albumcontains.albumid = album.albumid " \
                  "inner join songgenre on song.songid = songgenre.songid " \
                  "inner join genre on songgenre.genreid = genre.genreid " \
                  "and genre.genrename = %s " \
                  "left outer join userplayssong on song.songid = userplayssong.songid " \
                  "and userplayssong.userid = %s" + sort_sql

            cur.execute(sql, (search_text, user_id))
            result = cur.fetchall()

        elif filter_selected == "album":
            sql = "select song.songid, song.title, song.length, artist.artistname, " \
                  "album.albumname, genre.genrename, song.releasedate, userplayssong.playcount " \
                  "from song inner join songartist on song.songid = songartist.songid " \
                  "inner join artist on songartist.artistid = artist.artistid " \
                  "inner join albumcontains on song.songid = albumcontains.songid " \
                  "inner join album on albumcontains.albumid = album.albumid " \
                  "and album.albumname = %s " \
                  "inner join songgenre on song.songid = songgenre.songid " \
                  "inner join genre on songgenre.genreid = genre.genreid " \
                  "left outer join userplayssong on song.songid = userplayssong.songid " \
                  "and userplayssong.userid = %s" + sort_sql

            cur.execute(sql, (search_text, user_id))
            result = cur.fetchall()

        else:
            sql = "select song.songid, song.title, song.length, artist.artistname, " \
                  "album.albumname, genre.genrename, song.releasedate, userplayssong.playcount " \
                  "from song inner join songartist on song.songid = songartist.songid " \
                  "inner join artist on songartist.artistid = artist.artistid " \
                  "and artist.artistname = %s " \
                  "inner join albumcontains on song.songid = albumcontains.songid " \
                  "inner join album on albumcontains.albumid = album.albumid " \
                  "inner join songgenre on song.songid = songgenre.songid " \
                  "inner join genre on songgenre.genreid = genre.genreid " \
                  "left outer join userplayssong on song.songid = userplayssong.songid " \
                  "and userplayssong.userid = %s" + sort_sql

            cur.execute(sql, (search_text, user_id))
            result = cur.fetchall()

        if (result):
            if len(result) > int(amount_of_songs):
                result = result[:int(amount_of_songs)]

            for i in range(len(result)):
                if result[i][7] is None:
                    result[i] = (result[i][0], result[i][1], result[i][2], result[i][3],
                                 result[i][4], result[i][5], result[i][6], 0)

            user_data["searched_songs"] = result
            user_data["searched_song_error"] = "None"
        else:
            user_data["searched_song_error"] = "no song found!"
            user_data["searched_songs"] = "None"

        user_data["explore"] = True
        user_data["myAlbums"] = False
        session['user_data'] = user_data
        cur.close()
        return render_template('userpage.html', user_data=user_data)


@views.route('/followuser/', methods=['POST', 'GET'])
def follow_user():
    """
    function to follow another user
    :return:
    """

    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        # getting form data

        form_data = request.form
        user_data = session['user_data']
        user_id = user_data["id"]

        # calculating follower count

        conn = get_connection()
        cur = conn.cursor()

        sql = "select userid " \
              "from useraccount " \
              "where username = %s"
        cur.execute(sql, (user_data["searched_friend"],))
        searched_user_id = cur.fetchone()[0]

        sql = "insert into userfollows(useridfollower, useridfollowing)" \
              " values(%s, %s) on conflict do nothing returning null"
        cur.execute(sql, (user_id, searched_user_id))
        result = cur.fetchone()

        # TODO: display a message if the user is already following that user instead of just skipping
        if result:
            user_data["following"].append(user_data["searched_friend"].strip())
            session.modified = True

            sql = "select count(useridfollower) " \
                  "from userfollows " \
                  "where useridfollower = %s"
            cur.execute(sql, (user_id,))
            num_following = cur.fetchone()[0]

            sql = "select count(useridfollowing) " \
                  "from userfollows " \
                  "where useridfollowing = %s"
            cur.execute(sql, (user_id,))
            num_followers = cur.fetchone()[0]

            user_data["num_followers"] = num_followers
            user_data["num_following"] = num_following
            user_data['error'] = None
        else:
            user_data['error'] = 'You already follow this user'

        user_data["searched_friend"] = "None"

        conn.commit()
        cur.close()
        user_data["explore"] = False
        session['user_data'] = user_data

        return render_template('userpage.html', user_data=user_data)


@views.route('/unfollowuser/', methods=['POST', 'GET'])
def unfollow_user():
    """
    function to unfollow another user
    :return:
    """

    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':

        # getting form data
        form_data = request.form
        user_data = session['user_data']
        user_id = user_data["id"]

        if int(user_data["num_following"]) > 0:
            # calculating follower count

            conn = get_connection()
            cur = conn.cursor()

            sql = "select userid " \
                  "from useraccount " \
                  "where username = %s"
            cur.execute(sql, (form_data["usr"],))
            searched_user_id = cur.fetchone()[0]

            sql = "DELETE FROM userfollows " \
                  "WHERE useridfollower = %s and useridfollowing = %s"
            cur.execute(sql, (user_id, searched_user_id))

            user_data["following"].remove(form_data["usr"].strip())
            session.modified = True

            sql = "select count(useridfollower) " \
                  "from userfollows " \
                  "where useridfollower = %s"
            cur.execute(sql, (user_data["id"],))
            num_following = cur.fetchone()[0]

            sql = "select count(useridfollowing) " \
                  "from userfollows " \
                  "where useridfollowing = %s"
            cur.execute(sql, (user_data["id"],))
            num_followers = cur.fetchone()[0]

            user_data["num_followers"] = num_followers
            user_data["num_following"] = num_following

            conn.commit()
            cur.close()
            session['user_data'] = user_data
            return render_template('userpage.html', user_data=user_data)

        return render_template('userpage.html', user_data=user_data)


@views.route('/searchusers/', methods=['POST', 'GET'])
def search_users():
    """
    function to find a user by email
    :return:
    """

    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        form_data = request.form

        # getting user data
        user_data = session['user_data']
        email = form_data["usr_email"]

        # searching for user in db
        conn = get_connection()
        cur = conn.cursor()
        sql = "select username " \
              "from useraccount " \
              "where email = %s"
        cur.execute(sql, (email.strip(),))
        result = cur.fetchone()

        user_data["searched_friend"] = "None"
        # if user not found
        # TODO: show a message that says user not found
        if result:
            user_data["searched_friend"] = result[0]

        user_data["explore"] = False
        user_data['error'] = None
        session['user_data'] = user_data
        cur.close()

        return render_template('userpage.html', user_data=user_data)


@views.route('/playentirealbum/', methods=['POST', 'GET'])
def play_album():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        songID = int(request.form["songid"])

        user_data = session['user_data']
        userid = user_data['id']
        print("+++++____+_+_+_+_+_+_+_+_+_+_", songID)
        conn = get_connection()
        cur = conn.cursor()

        sql = "SELECT songid from albumcontains WHERE albumid = (SELECT albumid FROM albumcontains " \
              "WHERE songid = %s)"
        cur.execute(sql, (songID,))
        result = cur.fetchall()

        for songid in result:
            print()
            print(songid[0])
            print()

            sql = "insert into userplayssong(userid, songid, playcount) " \
                  "values(%s, %s, 1)" \
                  "on conflict(userid, songid) do update " \
                  "set playcount = userplayssong.playcount + 1"
            cur.execute(sql, (userid, int(songid[0])))
        conn.commit()
        cur.close()
    i = 0
    for song in user_data['searched_songs']:
        song = song[0:7] + (song[7] + 1,)
        user_data['searched_songs'][i] = song
        i += 1
    session['user_data'] = user_data

    return render_template('userpage.html', user_data=user_data)


@views.route('/playsong/', methods=['POST', 'GET'])
def play_song():
    """
    route to play a song

    :return:
    """
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        songid = request.form["songid"]
        user_data = session['user_data']
        userid = user_data['id']

        conn = get_connection()
        cur = conn.cursor()

        sql = "insert into userplayssong(userid, songid, playcount) " \
              "values(%s, %s, 1)" \
              "on conflict(userid, songid) do update " \
              "set playcount = userplayssong.playcount + 1"
        cur.execute(sql, (userid, int(songid)))
        conn.commit()
        cur.close()

        user_data["explore"] = True
        user_data["myAlbums"] = False

        i = 0
        for song in user_data['searched_songs']:
            if int(song[0]) == int(songid):
                song = song[0:7] + (song[7] + 1,)
                user_data['searched_songs'][i] = song
            i += 1

        session['user_data'] = user_data
        return render_template('userpage.html', user_data=user_data)


@views.route('/playcollection/', methods=['POST', 'GET'])
def play_collection():
    """
    route to play a collection of songs

    :return:
    """
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':

        user_data = session['user_data']
        userid = user_data['id']
        songs = user_data["current_playlist"]
        print(songs)

        conn = get_connection()
        cur = conn.cursor()

        for song in songs:
            sql = "insert into userplayssong(userid, songid, playcount) " \
                  "values(%s, %s, 1)" \
                  "on conflict(userid, songid) do update " \
                  "set playcount = userplayssong.playcount + 1"
            cur.execute(sql, (userid, int(song[0])))

        conn.commit()
        cur.close()

        user_data["explore"] = False
        user_data["myAlbums"] = True
        session['user_data'] = user_data

        return render_template('userpage.html', user_data=user_data)
