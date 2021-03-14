from flask import Blueprint,Flask, render_template,request


views = Blueprint('views',__name__)


# the home page
@views.route("/")
def home():
    return render_template("home.html")
