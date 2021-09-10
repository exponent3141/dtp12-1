from flask import Flask, render_template, redirect, url_for, request, session, g
import sys
import base64
import hashlib
import sqlite3
import os

from forms import SearchForm
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "chess_attempt.db")


app = Flask(__name__)
app.secret_key = base64.b64encode(os.urandom(32)).decode()[:-1]


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User:{self.username}>'


conn = sqlite3.connect("wack.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM LOGIN")
pwun = cursor.fetchall()
conn.close()
users = []
for i in range(len(pwun)):
    users.append(User(id=i+1, username=pwun[i][0], password=pwun[i][1]))


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        try:
            user = [x for x in users if x.id == session['user_id']][0]
            g.user = user
            g.user.logout = "Logout"
        except:
            return "User not found"


@app.route("/")
def home():
    print(g.user, file=sys.stderr)

    return render_template("home.html", user=g.user)


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template("about.html", user=g.user)


@app.route("/login", methods=["POST", "GET"])
def login():
    try:
        error = None

        conn = sqlite3.connect("wack.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM LOGIN")
        pwun = cursor.fetchall()
        conn.close()


        if request.method == "POST":
            session.pop('user_id', None)

            username = request.form["username"]
            password = hashlib.sha256(request.form["password"].encode()).hexdigest()
            try:
                user = [x for x in users if x.username == username][0]
            except:
                user = False
                error = "The username entered does not exist on the server"
            if (user and user.password == password):
                session['user_id'] = user.id

                return redirect(url_for("home"))

            elif user:
                error = "Incorrect password"
                print(pwun, file=sys.stderr)
                print(request.form["username"], request.form["password"], file=sys.stderr)


        return render_template("login.html", error=error, user=g.user)
    except Exception as e:

        return str(e)


@app.route("/register", methods=["POST", "GET"])
def register():
    try:
        error = None

        conn = sqlite3.connect("wack.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM LOGIN")
        pwun = cursor.fetchall()
        state = "INSERT INTO LOGIN (Username, Password) VALUES (?, ?);"



        if request.method == "POST":
            session.pop('user_id', None)
            if (request.form["username"]) in [i[0] for i in pwun]:
                error = "This username is already taken!"
                print(pwun, file=sys.stderr)
                print(request.form["username"], request.form["password"], file=sys.stderr)
            else:


                val = (request.form["username"], hashlib.sha256(request.form["password"].encode()).hexdigest())
                print(val, file=sys.stderr)
                conn.execute(state, val)
                conn.commit()
                conn.close()
                users.append(User(id=len(users)+1, username=request.form["username"], password=hashlib.sha256(request.form["password"].encode()).hexdigest()))
                session['user_id'] = users[-1].id
                return redirect(url_for("home"))
        conn.close()
        return render_template("register.html", error=error, user=g.user)
    except Exception as e:

        return str(e)


@app.route("/opening")
def Explorer():

    conn = sqlite3.connect("wack.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Main_Openings")

    cursoroutput = cursor.fetchall()

    conn.close()

    return render_template("opening.html", openingss=cursoroutput, user=g.user)





@app.route("/opening/<string:openingname>")
def openingsspecific(openingname):
    conn = sqlite3.connect("wack.db")
    cursors = conn.cursor()
    cursors.execute(''' SELECT p.name,
  p.description,
  mo.name,
  mo.description,
  mo.moves,
  mo.IFRAMELINK,
  OI.info_text
FROM
  Opening_Info OI
  INNER JOIN Main_Openings mo ON mo.id = OI.oid
  INNER JOIN Person p ON p.id = OI.pid
WHERE
  OI.id =
  '''+openingname+';')
    cursoroutput2 = cursors.fetchall()

    conn.close()
    print(cursoroutput2, file=sys.stderr)
    return render_template("openingprofile.html", thingy=cursoroutput2, user=g.user)


if __name__ == "__main__":

    app.run(debug=True)
