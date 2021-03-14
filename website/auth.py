from flask import Blueprint,Flask, render_template,request

auth = Blueprint('auth',__name__)




#new user sign up page
@auth.route("/signup", methods = ['POST', 'GET'])
def signup():

    if request.method == 'GET':
            return render_template('signup.html')
    if request.method == 'POST':
        form_data = request.form


        #ERROR CHECKING NAME (not null) IF ALL IS GOOD PUT NEW USERIN DB

        if form_data['firstName']=="":
            error = 'please input a vaild name'
        elif form_data['lastName']=="":
            error = 'please input a vaild last name'
        elif form_data['emailAdress']=="":
            error = 'please input a vaild email'
        else:
            user_data = {}
            user_data['passwordHash'] = hash(form_data['Password'])
            user_data.update(form_data)

            return render_template('userpage.html',user_data = user_data)

        return render_template('signup.html',error = error)


#sign in page
@auth.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
            return render_template('login.html')
    if request.method == 'POST':
        form_data = request.form

        #authenticate FROM DB

        #right now always false
        authenticated = False

        if authenticated:
            return render_template('userpage.html',user_data = form_data)
        else:
            error = "username or passoword is incorrcet"
            return render_template('login.html',error = error)
