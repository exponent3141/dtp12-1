from flask import Flask, render_template, url_for

from forms import SearchForm
import os.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "chess_attempt.db")



import sqlite3

app=Flask(__name__)

app.config['SECRET_KEY'] = 'any secret string'



@app.route('/')

def home():

  return render_template("home.html")


@app.route('/about')

def about():
    return render_template("about.html")
@app.route('/opening')

def Explorer():

  conn = sqlite3.connect('wack.db')

  cursor=conn.cursor()

  cursor.execute('SELECT * FROM Main_Openings')

  cursoroutput=cursor.fetchall()

  conn.close()

  return render_template('opening.html', openingss=cursoroutput)



@app.context_processor

def inject_search():

  searchform = SearchForm()

  return dict(searchform=searchform)



@app.route('/opening/<string:openingname>')
def openingsspecific(openingname):
  conn = sqlite3.connect('wack.db')

  cursor=conn.cursor()

  cursor.execute('''
SELECT
  p.id,
  p.name,
  p.description,
  mo.name,
  mo.description,
  mo.moves,
  mo.fen,
  OI.info_text
FROM
  Opening_Info OI
  INNER JOIN Main_Openings mo ON mo.id = OI.oid
  INNER JOIN Person p ON p.id = OI.pid
WHERE
  OI.id =
  '''+openingname+';')

  cursoroutput2=cursor.fetchall()

  conn.close()
  return render_template('openingprofile.html', thingy=cursoroutput2)
  

if __name__ == "__main__":

  app.run(debug=True)
