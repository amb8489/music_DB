from flask import Flask, render_template,request

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '123456789abc'

    from .views import views
    from .auth import auth
    from .database import init

    app.register_blueprint(views ,url_prefix = '/')
    app.register_blueprint(auth ,url_prefix = '/')


    return app
