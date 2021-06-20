from flask import Flask, render_template, url_for, redirect

import sqlite3
app=Flask(__name__)
app.config['SECRET_KEY'] = 'any secret string'


@app.route('/')
def homered():
  return redirect("/home", code=302)


@app.route('/home')
def home():
  return render_template("home.html")
 
@app.route('/opening')
def opening():
  conn = sqlite3.connect('chess attempt.db')
  cursor=conn.cursor()
  cursor.execute('SELECT * FROM Main_Openings')
  openings=cursor.fetchall()
  conn.close()
  print("hi")
  return render_template('pizza.html', pizza=openings)

@app.route('/about')
def about():
  return render_template("about.html")

@app.route('/search', methods=['POST'])
def search():
  if request.method =='POST':
    conn = sqlite3.connect('pizza.db')
    cursor=conn.cursor()
    c.executemany('''select * from Pizza where name = %s''', request.form['search'])
    results = 'SELECT * FROM Pizza'
    return render_template("results.html", records=c.fetchall())
  return render_template('search.html')

if __name__ == "__main__":
  app.run()
