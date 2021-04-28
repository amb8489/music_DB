from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, session

from connection import get_connection

auth = Blueprint('auth', __name__)


# new user sign up page
@auth.route("/signup", methods=['POST', 'GET'])
def signup():
    """
    signup signs a new user up
    :return: the template render
    """

    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':

        # get form data from signup page
        form_data = request.form

        # check for good credentials
        user_data, allowed, error = confirm_new_account(form_data)

        # setting up new user info
        if allowed:
            user_data["num_followers"] = "0"
            user_data["num_following"] = "0"
            user_data["new_playlist"] = []
            user_data["top5genre"] = ["rap", "pop", "country", "R&B", "rock"]


            user_data["playlist_name"] = []

            user_data.update(form_data)

            # saving user data into session
            session['user_data'] = user_data

            return redirect(url_for('views.userpage', user_data=user_data))

        return render_template('signup.html', error=error)


def confirm_new_account(form_data):
    """
    confirm new account's data is valid
    :param form_data: the data entered into the signup form
    :return: the render template
    """

    user_data = {}
    error = ''
    success = False

    # if any part of user data is empty
    for key in form_data:
        if form_data[key] == "":
            error = 'please input a valid {}'.format(key)
            return user_data, success, error

    # username already exists
    if username_taken(form_data["username"]):
        error = "username already taken"
        return user_data, success, error

    # email already exists
    if email_taken(form_data["emailAddress"]):
        error = "email already taken"
        return user_data, success, error

    # setting up new user in db
    success = True
    user_data['passwordHash'] = hash(form_data['password'])
    user_data['following'] = []

    user_data.update(form_data)

    # place new user in db
    conn = get_connection()
    cur = conn.cursor()
    sql = "insert into useraccount(username, firstname, lastname, email, password, creationdate, lastaccess)" \
          " values(%s, %s, %s, %s, %s, %s, %s)"
    cur.execute(sql, (user_data["username"], user_data["firstName"], user_data["lastName"], user_data["emailAddress"],
                      user_data["password"], datetime.now(), datetime.now()))

    # getting that users data from db
    sql = "select email, creationdate, lastaccess, userid " \
          "from useraccount " \
          "where username = %s"
    cur.execute(sql, (form_data["username"],))
    result = cur.fetchone()

    # caching user data
    user_data = {"username": form_data["username"], "emailAddress": result[0], "creationDate": result[1],
                 "lastAccess": result[2], "searched_friend": "None", "num_followers": 0,
                 "num_following": 0, "id": result[3], 'following': []}
    conn.commit()
    cur.close()
    user_data["num_of_costom_playlist"] = "0"
    user_data["top10artists"] = []

    return user_data, success, error


def email_taken(email):
    """
    check if an email is already taken
    :param email: the email address string
    :return: True if taken, else False
    """

    conn = get_connection()
    cur = conn.cursor()
    sql = "select 1 from useraccount " \
          "where email = %s"
    cur.execute(sql, (email,))
    result = cur.fetchone()
    cur.close()

    # if account doesn't exist
    if result is None:
        return False

    return True


def username_taken(username):
    """
    checks if a username is already taken
    :param username: the username string
    :return: True if taken else False
    """

    conn = get_connection()
    cur = conn.cursor()
    sql = "select 1 from useraccount " \
          "where username = %s"
    cur.execute(sql, (username,))
    result = cur.fetchone()
    cur.close()

    # if account doesn't exist
    if result is None:
        return False

    return True


def confirm_login(form_data):
    """
    confirms the log in was successful
    :param form_data:
    :return:
    """

    # check db credentials exists
    username = form_data["username"]
    password = form_data["password"]

    conn = get_connection()
    cur = conn.cursor()
    sql = "select 1 from useraccount " \
          "where username = %s and password = %s"
    cur.execute(sql, (username, password))
    result = cur.fetchone()

    # if credentials don't exist
    if result is None:
        return False

    # if good login set user last log in in db
    sql = "update useraccount" \
          " set lastaccess = %s" \
          " where username = %s"
    cur.execute(sql, (datetime.now(), username))
    conn.commit()
    cur.close()

    return True


# sign in page
@auth.route("/login", methods=['POST', 'GET'])
def login():
    """
    log a user in
    :return: the render template
    """

    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':

        # getting data the user inputed
        form_data = request.form

        # confirming the user log in details
        authenticated = confirm_login(form_data)

        if authenticated:

            # getting that users data from db
            conn = get_connection()
            cur = conn.cursor()
            sql = "select email, creationdate, lastaccess, userid " \
                  "from useraccount " \
                  "where username = %s"
            cur.execute(sql, (form_data["username"],))
            result = cur.fetchone()

            sql = "select count(useridfollower) " \
                  "from userfollows " \
                  "where useridfollower = %s"
            cur.execute(sql, (result[3],))
            num_following = cur.fetchone()[0]

            sql = "select count(useridfollowing) " \
                  "from userfollows " \
                  "where useridfollowing = %s"
            cur.execute(sql, (result[3],))
            num_followers = cur.fetchone()[0]

            # caching user data
            user_data = {"username": form_data["username"], "emailAddress": result[0], "creationDate": result[1],
                         "lastAccess": result[2], "searched_friend": "None", "num_followers": num_followers,
                         "num_following": num_following, "id": result[3], 'following': []}

            user_data["new_playlist"] = []
            # getting the user that they are following
            sql = "SELECT useridfollowing" \
                  " FROM userfollows" \
                  " WHERE useridfollower = %s"

            cur.execute(sql, (user_data["id"],))
            result = cur.fetchall()

            # if users follow nobody
            if len(result) > 0:
                sql = "SELECT username " \
                      "FROM useraccount " \
                      "WHERE userid IN %s"

                cur.execute(sql, (tuple(result),))
                result = cur.fetchall()

                # formatting names
                names = []
                for name in result:
                    name = name[0]
                    names.append(name)
                user_data['following'] = names

            sql = "SELECT name FROM collection where userid = %s"
            cur.execute(sql, (user_data["id"],))
            all_playlists = cur.fetchall()

            for each in all_playlists:
                user_data[each[0]] = ''

            userID = user_data["id"]

            if len(all_playlists) > 0:
                user_data["playlist_name"] = [name[0] for name in all_playlists]

            else:
                user_data["playlist_name"] = []
            user_data["num_of_costom_playlist"] = str(len(user_data["playlist_name"]))


            sql = "SELECT playcount,artistid FROM artist_play_counts WHERE userid = %s"
            cur.execute(sql, (user_data["id"],))
            artist_play_counts = list(cur.fetchall())

            artist_play_counts = sorted(artist_play_counts)
            artist_play_counts = artist_play_counts[::-1]

            if len(artist_play_counts)>10:
                artist_play_counts = artist_play_counts[:10]
            print("_______\n",artist_play_counts)

            artist_play_counts = [artistID[1] for artistID in artist_play_counts]
            user_data["top10artists"] = []
            for artistid in artist_play_counts:
                sql = "SELECT artistname from artist where artistid = %s"
                cur.execute(sql, (artistid,))
                user_data["top10artists"].append(cur.fetchone())

            # get the genres of the top songsss of the month---

            sql = "SELECT songid from userplayssong WHERE userid = %s"
            cur.execute(sql, (user_data["id"],))
            songids = cur.fetchall()


            songs = []
            for songid in songids:
                sql = "select count(songid) from userplayssong WHERE songid = %s"
                cur.execute(sql, (songid[0],))
                songs.append((cur.fetchone()[0],songid[0]))

            songs = sorted(songs)
            songs = songs[::-1]
            songs = [song[1] for song in songs]


            top5genre = set()
            for songid in songs:
                sql = "SELECT genrename FROM genre WHERE genreid IN (SELECT genreid "\
                  "FROM songgenre WHERE songid = %s)"
                cur.execute(sql, (songid,))
                top5genre.add(cur.fetchone()[0])
                if len(top5genre) == 5:
                    break
            i = 0
            genres = {0:"rap", 1:"pop", 2:"country", 3:"R&B", 4:"rock", 5:"alternative", 6:"indie"}

            while len(top5genre) < 5:
                top5genre.add(genres[i])
                i+=1




            print("\n",top5genre,"\n")


            user_data["top5genre"] = list(top5genre)

            ## RECOMMENDATIONS ##
            # top 50 songs
            #todo

            # top 50 songs friends
            sql = "select useridfollowing from userfollows where useridfollower = %s"
            cur.execute(sql, (user_data["id"],))
            following_ids = cur.fetchall()

            percent_s = ", ".join(["%s"]*len(following_ids))
            sql = "select songid from userplayssong where userid in (" + percent_s + \
                  ") group by songid order by count(songid) desc"
            cur.execute(sql, following_ids)
            song_ids = cur.fetchall()
            if len(song_ids) > 50:
                song_ids = song_ids[:50]

            percent_s = ", ".join(["%s"] * len(song_ids))
            sql = "select title from song where songid in (" + percent_s + ")"
            print(percent_s)
            print(song_ids)
            cur.execute(sql, song_ids)
            top_songs = cur.fetchall()
            print(top_songs)
            user_data["top50byfriends"] = top_songs

            # for you
            #todo

            cur.close()

            # saving user details into the session for global use
            session['user_data'] = user_data
            return render_template('userpage.html', user_data=user_data)
        else:
            # log in was bad
            error = "username or password is incorrect"
            return render_template('login.html', error=error)
