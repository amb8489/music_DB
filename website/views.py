from flask import Blueprint, render_template, request, session, jsonify

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
def add_to_my_playlist():
    """
    function to get a users albums (collections
    :return:
    """

    if request.method == 'GET':
        return render_template('userpage.html')
    if request.method == 'POST':
        # geting form data
        form_data = request.form['song_']

        user_data = session['user_data']
        print(form_data)
        user_data["new_playlist"].append(form_data[7:-2].replace('\'', '').split(","))
        user_data["explore"] = True
        user_data["myAlbums"] = False
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
        sql = " SELECT ALL title FROM song WHERE songid IN "\
              "(SELECT ALL songid FROM collectionsong WHERE collectionid IN "\
              "(SELECT ALL collectionid FROM collection where name = %s AND userid = %s)) "
        cur.execute(sql, (playlist_name,userID))
        songs = cur.fetchall()

        print(songs)

        user_data["current_playlist"] = songs
        user_data["current_playlist_name"]=playlist_name

        user_data["myAlbum"] = True
        session['user_data'] = user_data
    return render_template('userpage.html', user_data=user_data)




@views.route('/makenewplaylists/', methods=['POST', 'GET'])
def make_new_playlist():
    """
    function to get the user's followers
    :return:
    """


    if request.method == 'GET':
        return render_template('userpage.html')
    if request.method == 'POST':
        # getttting form data
        form_data = request.form
        user_data = session['user_data']

        new_playlist_name = form_data["playlist_name"]

        user_data["playlist_name"].append(new_playlist_name)
        user_data["playlist_name"] = sorted(user_data["playlist_name"])
        session['user_data'] = user_data

        usrID = user_data["id"]

        conn = get_connection()
        cur = conn.cursor()
# making new collection in db
        sql = "insert into collection(name,userid) " \
              "values(%s, %s) RETURNING collectionid"
        cur.execute(sql, (new_playlist_name,usrID))
        playlistID = cur.fetchone()[0]

# adding songs to collection --better way to do this ?

        songs_in_playlist = user_data["new_playlist"]
        songIDs = [song[0] for song in songs_in_playlist]
        for songid in songIDs:
            sql = "insert into collectionsong(collectionid,songid)" \
                  "values(%s, %s)"
            cur.execute(sql, (playlistID,songid))

        conn.commit()
        cur.close()



        user_data["new_playlist"] = []
        user_data["explore"] = True
        user_data["myAlbums"] = False

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

        user_data = session['user_data']
        user_id = user_data["id"]

        conn = get_connection()
        cur = conn.cursor()


        result = None  # get outer scope

        # FILTER_SELECTED IS USED TO GET THE SONGS (in 'result'), THEN THE SHARED 'IF' BELOW IS USED
        if filter_selected == "title":
            sql = "select song.songid, song.title, song.length, artist.artistname, " \
                  "album.albumname, genre.genrename, song.releasedate, userplayssong.playcount" \
                  "from song inner join songartist on song.songid = songartist.songid " \
                  "and song.title = %s " \
                  "inner join artist on songartist.artistid = artist.artistid " \
                  "inner join albumcontains on song.songid = albumcontains.songid " \
                  "inner join album on albumcontains.albumid = album.albumid " \
                  "inner join songgenre on song.songid = songgenre.songid " \
                  "inner join genre on songgenre.genreid = genre.genreid " \
                  "left outer join userplayssong on song.songid = userplayssong.songid " \
                  "and userplayssong.userid = %s"

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
                  "and userplayssong.userid = %s"

            cur.execute(sql, (search_text, user_id))
            result = cur.fetchall()

            # TODO
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
                  "and userplayssong.userid = %s"

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
                  "and userplayssong.userid = %s"

            cur.execute(sql, (search_text, user_id))
            result = cur.fetchall()

        if (result):
            if len(result) > int(amount_of_songs):
                result = result[:int(amount_of_songs)]

            for i in range(len(result)):
                if result[i][6] is None:
                    result[i] = (result[i][0], result[i][1], result[i][2], result[i][3], result[i][4], result[i][5], 0)

            user_data["searched_songs"] = sorted(result)
            # user_data["searched_song_id"] = result[1]
        else:
            user_data["searched_song_errors"] = "no song found!"
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
        session['user_data'] = user_data
        cur.close()

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
        print(songid)
        user_data = session['user_data']
        userid = user_data['id']

        conn = get_connection()
        cur = conn.cursor()

        sql = "insert into userplayssong(userid, songid, playcount) " \
              "values(%s, %s, 1)" \
              "on conflict(userid, songid) do update " \
              "set playcount = userplayssong.playcount + 1"
        cur.execute(sql, (userid, int(songid)))
        cur.fetchone()
        conn.commit()
        cur.close()

        return jsonify("playcount: %s", ())
