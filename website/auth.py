from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, session

from connection import get_connection

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

            user_data["num_followers"] = "0"
            user_data["num_following"] = "0"
            session['user_data'] = user_data
            user_data.update(form_data)

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
        if form_data[key] == "":
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
    cur.execute(sql, (user_data["username"], user_data["firstName"], user_data["lastName"], user_data["emailAddress"],
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

    # check db for right credentials
    username = form_data["username"]
    password = form_data["password"]

    conn = get_connection()
    cur = conn.cursor()
    sql = "select 1 from useraccount " \
          "where username = %s and password = %s"
    cur.execute(sql, (username, password))
    result = cur.fetchone()
    if result is None:
        return False

    # if good login set user last log in in db
    sql = "update useraccount" \
          " set lastaccess = %s" \
          " where username = %s"
    cur.execute(sql, (datetime.now(), username))
    cur.close()

    return True


# sign in page
@auth.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        form_data = request.form

        authenticated = confirm_login(form_data)

        if authenticated:
            conn = get_connection()
            cur = conn.cursor()
            sql = "select email, creationdate, lastaccess,numberoffollowers,numberfollowing " \
                  "from useraccount " \
                  "where username = %s"
            cur.execute(sql, (form_data["username"],))
            result = cur.fetchone()
            user_data = {"username": form_data["username"], "emailAddress": result[0], "creationDate": result[1],
                         "lastAccess": result[2]}
            user_data["searched_friend"] = "None"
            user_data["num_followers"] = result[3]
            user_data["num_following"] = result[4]
            session['user_data'] = user_data

            return render_template('userpage.html', user_data=user_data)
        else:
            error = "username or password is incorrect"
            return render_template('login.html', error=error)
