from website import create_app
# from werkzeug.serving import run_simple

app = create_app()

if __name__ == '__main__':
    # run_simple('localhost', 8080, app, use_reloader=True)
    app.run(debug=True)