import os
import flask
import sqlite3

app = flask.Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
APP_PASSWORD = os.environ.get("GIFT_TRACKER_PASSWORD", "letmein")


@app.before_request
def require_login_for_index_file():
    if flask.request.path == "/static/index.html" and not flask.session.get("authed"):
        return flask.redirect("/login")

conn = sqlite3.connect('gifts.db') 
cursor = conn.cursor()  
cursor.execute('''
    CREATE TABLE IF NOT EXISTS gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gift TEXT NOT NULL
    )
''')
conn.commit()  
conn.close()

@app.get("/")
def index():
    if not flask.session.get("authed"):
        return flask.redirect("/login")
    return flask.send_from_directory("static", "index.html")


@app.get("/login")
def login_page():
    return flask.send_from_directory("static", "login.html")


@app.post("/login")
def login():
    password = flask.request.form.get("password", "")
    if password != APP_PASSWORD:
        return "Invalid password", 401
    flask.session["authed"] = True
    return flask.redirect("/")

@app.post("/gifts")
def create_gift():
    if not flask.session.get("authed"):
        return "Unauthorized", 401
    data = flask.request.get_json()
    name = data.get('name')
    gift = data.get('gift')
    
    conn = sqlite3.connect('gifts.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO gifts (name, gift) VALUES (?, ?)', (name, gift))
    conn.commit()
    conn.close()

    return '', 201
    
@app.get("/gifts")
def get_gifts():
    if not flask.session.get("authed"):
        return "Unauthorized", 401
    conn = sqlite3.connect('gifts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, gift FROM gifts')
    rows = cursor.fetchall()
    conn.close()
    
    gifts = [{'id': row[0], 'name': row[1], 'gift': row[2]} for row in rows]
    return flask.jsonify(gifts)

if __name__ == "__main__":
    app.run()