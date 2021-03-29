from flask import Blueprint, render_template, request, session

views = Blueprint('views', __name__)


# the home page
@views.route("/")
def home():
    return render_template("home.html")


# the user page
@views.route("/userpage")
def userpage():
    user_data = request.args['user_data']  # counterpart for url_for()
    user_data = session['user_data']  # counterpart for session
    return render_template("userpage.html", user_data=user_data)


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




##### IN-PROGRESS
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


        conn = get_connection()  # import 
        cur = conn.cursor()
        sql = "select username ,email" \
              "from useraccount " \
              "where email = %s"
        cur.execute(sql, (email,))
        result = cur.fetchone()

        user_data["searched_friend"] = result

        return render_template('userpage.html', user_data=user_data)
