from flask import Blueprint,Flask, render_template,request, session


views = Blueprint('views',__name__)

# the home page
@views.route("/")
def home():
    return render_template("home.html")



# the user page
@views.route("/userpage")
def userpage():
    user_data = request.args['user_data']  # counterpart for url_for()
    user_data = session['user_data']       # counterpart for session
    return render_template("userpage.html",user_data = user_data)
