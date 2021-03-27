from flask import Blueprint,Flask, render_template,request, redirect, url_for,session

auth = Blueprint('auth',__name__)




#new user sign up page
@auth.route("/signup", methods = ['POST', 'GET'])
def signup():

    if request.method == 'GET':
            return render_template('signup.html')
    if request.method == 'POST':

        # get form data
        form_data = request.form

        # check for good cridentials
        user_data,allowed,error = confirm_new_account(form_data)


        if allowed:
            session['user_data'] =  user_data


            return redirect(url_for('views.userpage',user_data = user_data))

            #return render_template('userpage.html',user_data = user_data)

        return render_template('signup.html',error = error)



'''
place to confirm new sign up data is allowed
'''
def confirm_new_account(form_data):
    #ERROR CHECKING NAME (not null) IF ALL IS GOOD PUT NEW USERIN DB

    user_data = {}
    error = ''
    success = False


    # What ever needs to be check in db bfore signing up
    if form_data['firstName']=="":
        error = 'please input a vaild name'
    elif form_data['lastName']=="":
        error = 'please input a vaild last name'
    elif form_data['emailAdress']=="":
        error = 'please input a vaild email'
    else:
        success = True
        user_data['passwordHash'] = hash(form_data['Password'])
        user_data.update(form_data)


        # add time of creation and last log in = time of creation

        # place user in db

    return user_data,success,error



'''
place to confirm log in
'''
def confirm_login(form_data):
    # check db for right cridetials

    return False



#sign in page
@auth.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
            return render_template('login.html')
    if request.method == 'POST':
        form_data = request.form

        #authenticate FROM DB

        #right now always false
        authenticated = confirm_login(form_data)

        if authenticated:
            # load user data from db

            #shiould prob be a redirect with a new log in route taht will load user data
            return render_template('userpage.html',user_data = form_data)
        else:
            error = "username or passoword is incorrcet"
            return render_template('login.html',error = error)
