from flask import Flask, render_template, redirect, url_for, request, session, g
import sys
import base64
import hashlib
import sqlite3
import os
import os.path

# defining the flask application

app = Flask(__name__)

# Generating secret key; this just base64 encodes 32 random bytes
app.secret_key = base64.b64encode(os.urandom(32)).decode()[:-1]


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User:{self.username}>'


# Getting all users and passwords on program start
conn = sqlite3.connect("wack.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM LOGIN")
pwun = cursor.fetchall()
conn.close()
users = []
# Creating a User object with the details obtianed priorly
for i in range(len(pwun)):
    users.append(User(id=i+1, username=pwun[i][0], password=pwun[i][1]))


@app.before_request
def before_request():
    g.user = None

    # Check if the user is logged in (has a valid session)
    if 'user_id' in session:
        try:j
            # Get the user with the session id given
            user = [x for x in users if x.id == session['user_id']][0]
            g.user = user
            # This variable is so that the Logout text will be displayed.
            # <a href = "/logout"  > {{user.logout}}</a></li>
            # If user.logout is not set, this text won't appear
            g.user.logout = "Logout"
        except Exception as e:
            return "User not found" + e


@app.route("/")
def home():
    return render_template("home.html", user=g.user)


@app.route("/logout")
def logout():
    # Removes current session
    session.pop('user_id', None)
    # Redirects to home.html WITHOUT user=g.user
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template("about.html", user=g.user)


@app.route("/login", methods=["POST", "GET"])
def login():
    # Massive try except in case of a plethora of errors.
    try:
        # This will be displayed under the login page ('incorrect password')
        error = None
        # There is no need to reconnect to the database here.
        # This is because the /register page also appends the new user to the
        # list of users, and so it is not needed to reconnect and check the
        # database.

        if request.method == "POST":
            # Removes current session
            session.pop('user_id', None)

            username = request.form["username"]
            # Converts password to bytes, then gets the hex digest of the
            # Sha 256 hash of the password.
            password = hashlib.sha256(request.form["password"].encode()).hexdigest()
            try:
                # Gets uer object with the same username as the one provided
                # Will error if not present
                user = [x for x in users if x.username == username][0]
            except IndexError:
                user = False
                error = "The username entered does not exist on the server"
            # Checks if the user existed from before and if password is correct
            if (user and user.password == password):
                # Creates session
                session['user_id'] = user.id
                # Redirects to home
                return redirect(url_for("home"))
            # User exists; password is incorrect
            elif user:
                error = "Incorrect password"
                # print(pwun, file=sys.stderr)
                # print(request.form["username"], request.form["password"], file=sys.stderr)
        # Renders the page with the 'error' message
        return render_template("login.html", error=error, user=g.user)
    except Exception as e:
        # hope this is never called :D
        return str(e)


@app.route("/register", methods=["POST", "GET"])
def register():
    try:
        error = None
        # Connect to database
        conn = sqlite3.connect("wack.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM LOGIN")
        pwun = cursor.fetchall()
        # SQL insert statement
        state = "INSERT INTO LOGIN (Username, Password) VALUES (?, ?);"

        if request.method == "POST":
            # Remove current session
            session.pop('user_id', None)
            # Checks if the username entered is in the database
            if (request.form["username"]) in [i[0] for i in pwun]:
                error = "This username is already taken!"
                # print(pwun, file=sys.stderr)
                # print(request.form["username"], request.form["password"], file=sys.stderr)
            else:
                # Tuple of username and hashed password (sql format)
                val = (request.form["username"], hashlib.sha256(request.form["password"].encode()).hexdigest())
                # print(val, file=sys.stderr)
                # Execute query
                conn.execute(state, val)
                conn.commit()
                conn.close()
                # Adds new user to the current list
                users.append(User(id=len(users)+1, username=request.form["username"], password=hashlib.sha256(request.form["password"].encode()).hexdigest()))
                # Gets the session of the most recently created user
                session['user_id'] = users[-1].id
                return redirect(url_for("home"))

        conn.close()
        return render_template("register.html", error=error, user=g.user)
    except Exception as e:
        # as before, if this runs someting went very wrong
        return str(e)


@app.route("/opening")
def Explorer():

    # Connect to database and retrieve opening information
    conn = sqlite3.connect("wack.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Main_Openings")
    cursoroutput = cursor.fetchall()
    conn.close()
    # render and pass database response into openingss
    return render_template("opening.html", openingss=cursoroutput, user=g.user)


@app.route("/opening/<string:openingname>")
# Dynamic page; will load depending on what opening is given
def openingsspecific(openingname):
    # Connect to database and retrieve information about the specific opening
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
    # Close database and return information
    conn.close()
    # print(cursoroutput2, file=sys.stderr)
    return render_template("openingprofile.html", thingy=cursoroutput2, user=g.user)


if __name__ == "__main__":
    # Run app
    app.run(debug=True)
