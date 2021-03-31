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

        # get form data from signup page
        form_data = request.form

        # check for good credentials
        user_data, allowed, error = confirm_new_account(form_data)

        # setting up new user info
        if allowed:
            user_data["num_followers"] = "0"
            user_data["num_following"] = "0"
            user_data["my_albums"] = "None"

            user_data.update(form_data)

            #saving user data into session
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
    sql = "select email, creationdate, lastaccess,numberoffollowers,numberfollowing,userid " \
          "from useraccount " \
          "where username = %s"
    cur.execute(sql, (form_data["username"],))
    result = cur.fetchone()

    # caching user data
    user_data = {"username": form_data["username"], "emailAddress": result[0], "creationDate": result[1],
                 "lastAccess": result[2], "searched_friend": "None", "num_followers": result[3],
                 "num_following": result[4], "id": result[5], 'following': []}
    conn.commit()
    cur.close()

    return user_data, success, error


def email_taken(email):

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
    cur.close()

    return True


# sign in page
@auth.route("/login", methods=['POST', 'GET'])
def login():
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
            sql = "select email, creationdate, lastaccess,numberoffollowers,numberfollowing,userid " \
                  "from useraccount " \
                  "where username = %s"
            cur.execute(sql, (form_data["username"],))
            result = cur.fetchone()

            # caching user data
            user_data = {"username": form_data["username"], "emailAddress": result[0], "creationDate": result[1],
                         "lastAccess": result[2], "searched_friend": "None", "num_followers": result[3],
                         "num_following": result[4], "id": result[5], 'following': []}


            # TODO LOAD USER ALBUMS
            user_data["my_albums"] = "None"

            # getting the user that they are following
            sql = "SELECT ALL useridfollowing"\
                  " FROM userfollows"\
                  " WHERE useridfollower = %s"

            cur.execute(sql, (user_data["id"],))
            result = cur.fetchall()

            # if users follow nobody
            if len(result)>0:
                sql = "SELECT All username "\
                      "FROM useraccount "\
                      "WHERE userid IN %s"

                cur.execute(sql, (tuple(result),))
                result = cur.fetchall()

                # formating names
                names = []
                for name in result:
                    name = name[0]
                    names.append(name)
                user_data['following'] = names


            # saving user details into the session for global use
            session['user_data'] = user_data
            return render_template('userpage.html', user_data=user_data)
        else:
            # log in was bad
            error = "username or password is incorrect"
            return render_template('login.html', error=error)
