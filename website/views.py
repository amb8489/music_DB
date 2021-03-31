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

    return render_template("userpage.html",user_data = user_data)


'''
function to get user albums
'''
@views.route('/myalbums/')
def my_albums():

    pass

'''
function to get user followers
'''
@views.route('/myfollowers/')
def my_followers():

    pass


'''
function to get user a searched song
'''
@views.route('/searchedsong/',methods = ['POST', 'GET'])
def searched_song():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        # getttting form data
        form_data = request.form


        # how we want to search for song by
        filter_selected = form_data['options']
        amount_of_songs = form_data['amount']

        # TO DO
        user_data = session['user_data']

        conn = get_connection()
        cur = conn.cursor()

        print("filter type, by:",filter_selected)
        print("only show the first:",amount_of_songs,"songs")

        print("find songs relating to:",form_data["song_name"])


            # DONE
        if filter_selected == "title":
            sql = "select title, songid " \
                  "from song " \
                  "where title = %s"

            cur.execute(sql, (form_data["song_name"],))
            result = cur.fetchone()

            # TODO
        elif filter_selected == "genre":
            sql = "select ALL title from song where songid = (select ALL songid from songartist where artistid = (select artistid " \
                      " from artist " \
                      " where artistname = %s))"

            cur.execute(sql, (form_data["song_name"],))
            result = cur.fetchall()
            # TODO
        elif filter_selected == "album":
            sql = "select ALL title from song where songid = (select ALL songid from songartist where artistid = (select artistid " \
                      " from artist " \
                      " where artistname = %s))"

            cur.execute(sql, (form_data["song_name"],))
            result = cur.fetchall()
            # DONE
        else:
            sql = "select ALL title from song where songid = (select ALL songid from songartist where artistid = (select artistid " \
                      " from artist " \
                      " where artistname = %s))"

            cur.execute(sql, (form_data["song_name"],))
            result = cur.fetchall()
            # print(result)


        if(result):
            if result > amount:
                result = [result[i] for i in range(amount)]

            user_data["searched_song"] = result
            # user_data["searched_song_id"] = result[1]
        else:
            user_data["searched_song_error"] = "no song found!"
        user_data["explore"] = True
        cur.close()
        return render_template('userpage.html', user_data=user_data)


'''
function to unfollow user
'''
@views.route('/unfollowuser/',methods = ['POST', 'GET'])
def unfollow_user():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':

            # getttting form data
            form_data = request.form
            user_data = session['user_data']
            if int(user_data["num_following"]) > 0:

                # calculating follower count

                conn = get_connection()
                cur = conn.cursor()


                user_data["num_following"] -= 1

                user_id = user_data["id"]

                sql = "select userid " \
                      "from useraccount " \
                      "where username = %s"
                cur.execute(sql, (form_data["usr"],))
                result = cur.fetchone()

                seached_user_id = result[0]

                # add to user following count for user

                sql = "update useraccount "\
                      "set numberfollowing = numberfollowing - 1 "\
                      "where username = %s"
                cur.execute(sql, (user_data["username"],))

                #updating followers count for other user
                sql = "update useraccount"\
                      " set numberoffollowers = numberoffollowers - 1"\
                      " where username = %s"
                cur.execute(sql, (form_data["usr"],))
                # follow this person conection in db

                sql = "DELETE FROM userfollows WHERE useridfollower = %s and useridfollowing = %s"

                cur.execute(sql, (user_id,seached_user_id))

                user_data["following"].remove(form_data["usr"].strip())

                conn.commit()


                cur.close()
                return render_template('userpage.html', user_data=user_data)

            return render_template('userpage.html', user_data=user_data)




'''

function to follow

'''
@views.route('/followuser/',methods = ['POST', 'GET'])
def follow_user():

    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':


        # getttting form data

        form_data = request.form
        user_data = session['user_data']

        # calculating follower count

        conn = get_connection()
        cur = conn.cursor()

        sql = "select numberoffollowers, numberfollowing, userid " \
              "from useraccount " \
              "where userid = %s"
        cur.execute(sql, (user_data["id"],))
        result = cur.fetchone()

        user_data["num_followers"] = result[0]
        user_data["num_following"] = result[1]+1
        user_id = result[2]

        sql = "select userid " \
              "from useraccount " \
              "where username = %s"
        cur.execute(sql, (user_data["searched_friend"],))
        result = cur.fetchone()

        seached_user_id = result[0]

        # add to user following count for user

        sql = "update useraccount "\
              "set numberfollowing = numberfollowing + 1 "\
              "where userid = %s"
        cur.execute(sql, (user_data["id"],))

        #updating followers count for other user
        sql = "update useraccount"\
              " set numberoffollowers = numberoffollowers + 1"\
              " where username = %s"
        cur.execute(sql, (user_data["searched_friend"],))
        # follow this person conection in db

        sql = "insert into userfollows(useridfollower, useridfollowing)" \
              " values(%s, %s)"
        cur.execute(sql, (user_id,seached_user_id))
        user_data["following"].append(user_data["searched_friend"])

        user_data["searched_friend"] = "None"
        conn.commit()
        # user_data["following"].append(user_data["searched_friend"])


        cur.close()

        return render_template('userpage.html', user_data=user_data)

'''
route to "play" a song
'''

@views.route('/playsong', methods = ['POST', 'GET'])
def play_song():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        songid = request.args.get('songid')
        user_data = session['user_data']
        userid = user_data['id']
        #TODO check for userplayssong(songid, userid)
        #TODO increment the playcount



'''
function to find a user by email
'''

@views.route('/searchusers/',methods = ['POST', 'GET'])
def search_users():

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

        # if user not found
        if result is None:
            user_data["searched_friend"] ="None"
            return render_template('userpage.html', user_data=user_data)

        #saving some data
        user_data["searched_friend"] = result[0]
        session['user_data'] = user_data
        cur.close()

        return render_template('userpage.html', user_data=user_data)
