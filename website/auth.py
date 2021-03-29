from flask import Blueprint, render_template, request, redirect, url_for, session
from connection import get_connection
from datetime import datetime

auth = Blueprint('auth', __name__)


# new user sign up page
@auth.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':

        # get form data
        form_data = request.form

        # check for good credentials
        user_data, allowed, error = confirm_new_account(form_data)

        if allowed:
            session['user_data'] = user_data

            return redirect(url_for('views.userpage', user_data=user_data))

        return render_template('signup.html', error=error)


def confirm_new_account(form_data):
    """
    confirm new account's data is valid
    :param form_data:
    :return:
    """

    user_data = {}
    error = ''
    success = False


    # if any part of user data is empty
    for key in form_data:
        if form_data[key]=="":
            error = 'please input a valid {}'.format(key)
            return user_data, success, error



    # --- TODO --- do a check to make sure that new credentials are NOT
    # already beig used like (username and email)


    success = True
    user_data['passwordHash'] = hash(form_data['password'])
    user_data.update(form_data)

    # place new user in db
    conn = get_connection()
    cur = conn.cursor()
    sql = "insert into useraccount(username, firstname, lastname, email, password, creationdate, lastaccess)" \
             " values(%s, %s, %s, %s, %s, %s, %s)"
    cur.execute(sql,(user_data["username"], user_data["firstName"], user_data["lastName"], user_data["emailAddress"],
                     user_data["password"], datetime.now(), datetime.now()))
    conn.commit()
    cur.close()

    return user_data, success, error


def confirm_login(form_data):
    """
    confirms the log in was successful
    :param form_data:
    :return:
    """

    # ----------- check db for right credentials---------------

    # -------------- if good login  set user last log in in db --------------

    return False


# sign in page
@auth.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        form_data = request.form

        # right now always false
        authenticated = confirm_login(form_data)

        if authenticated:
            # ------------load user data from db--------------------

            return render_template('userpage.html', user_data=form_data)
        else:
            error = "username or password is incorrect"
            return render_template('login.html', error=error)
