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
    user_data = request.args['user_data']  # counterpart for url_for()
    session['user_data'] = user_data
    user_data = session['user_data']  # counterpart for session
    user_data["searched_friend"] = "None"

    return render_template("userpage.html",user_data =user_data)


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
@views.route('/searchedsong/')
def searched_song():

    pass




'''
function to follow  TODO
'''
@views.route('/followuser/',methods = ['POST', 'GET'])
def follow_user():

    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':



        form_data = request.form
        user_data = session['user_data']  # counterpart for session



        conn = get_connection()
        cur = conn.cursor()
        #
        sql = "select numberoffollowers, numberfollowing " \
              "from useraccount " \
              "where username = %s"
        cur.execute(sql, (user_data["username"],))
        result = cur.fetchone()



        user_data["num_followers"] = result[0]
        user_data["num_following"] = result[1]+1

        #add to user follers count

        sql = "update useraccount "\
              "set numberfollowing =  1 "\
              "where username = %s"
        cur.execute(sql, (user_data["username"],))


        sql = "update useraccount"\
              " set numberoffollowers = numberoffollowers + 1"\
              " where username = %s"
        cur.execute(sql, (user_data["searched_friend"],))
        # make connection thaty i follow this person

        user_data["searched_friend"] ="None"
        conn.commit()

        cur.close()

        # TODO
        return render_template('userpage.html', user_data=user_data)




'''
function to get user a searched song
'''
@views.route('/searchusers/',methods = ['POST', 'GET'])
def search_users():


    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        form_data = request.form


        user_data = session['user_data']  # counterpart for session

        email = form_data["usr_email"]


        conn = get_connection()
        cur = conn.cursor()

        sql = "select username " \
              "from useraccount " \
              "where email = %s"
        cur.execute(sql, (email.strip(),))
        result = cur.fetchone()


        if result is None:
            user_data["searched_friend"] ="None"
            return render_template('userpage.html', user_data=user_data)

        user_data["searched_friend"] = result[0]
        session['user_data'] = user_data
        cur.close()

        return render_template('userpage.html', user_data=user_data)
