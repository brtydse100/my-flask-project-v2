from website import create_app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    
    from .website.views import views

    app.register_blueprint(views, url_prefix='/')

    
        
    return app
# from werkzeug.serving import run_simple

app = create_app()

if __name__ == '__main__':
    # run_simple('localhost', 8080, app, use_reloader=True)
    app.run(host="0.0.0.0", port=5000)
    # app.run(debug=True)