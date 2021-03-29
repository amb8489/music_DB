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
