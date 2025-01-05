# from utils.views import views
from utils.views import views
from flask import  Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'


    app.register_blueprint(views, url_prefix='/')
    return app

app = create_app()

if __name__ == '__main__':
    # run_simple('localhost', 8080, app, use_reloader=True)
    #app.run(host='192.168.0.11', port=5020)
    app.run(debug=True,host='0.0.0.0', port=5000)
    # app.run(debug=True, host='192.168.0.11',port=5020)

