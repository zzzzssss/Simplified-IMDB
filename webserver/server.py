#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from datetime import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the postgresql test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/postgres
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# Swap out the URI below with the URI for the database created in part 2
DATABASEURI = "postgresql://hx2208:dmy9k@104.196.175.120/postgres"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  #cursor = g.conn.execute("SELECT name FROM test")
  #names = []
  #for result in cursor:
  #  names.append(result['name'])  # can also be accessed using result[0]
  #cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
#@app.route('/another')
#def another():
#  return render_template("anotherfile.html")


# Example of adding new data to the database
#@app.route('/add', methods=['POST'])
#def add():
#  name = request.form['name']
#  print name
#  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
#  g.conn.execute(text(cmd), name1 = name, name2 = name);
#  return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['username']
    if len(email) == 0:
      return render_template("index.html", error_message="Email cannot be empty")
    if '@' not in email:
      return render_template("index.html", error_message="Invalid email address")
    password = request.form['password']
    if len(password) == 0:
      return render_template("index.html", error_message="Password cannot be empty")
    res = g.conn.execute('SELECT nickname, pid FROM users WHERE email = (%s) and password = (%s)', email, password).fetchall();
    if len(res) == 0:
      return render_template("index.html", error_message="Incorrect login info")
    else:
      username = res[0]['nickname']
      people_id = res[0]['pid']
      return render_template("main.html", username=res[0]['nickname'], pid = res[0]['pid'])

@app.route('/new', methods=['POST'])
def new_acc():
  return render_template("anotherfile.html")

@app.route('/register', methods=['POST'])
def register():
  email = request.form['username']
  if len(email) == 0:
    return render_template("anotherfile.html", error_message="Email cannot be empty")
  if '@' not in email:
    return render_template("anotherfile.html", error_message="Invalid email address")
  res = g.conn.execute('SELECT * FROM users WHERE email = (%s)', email).fetchall();
  if len(res) != 0:
    return render_template("anotherfile.html", error_message="Email address has been registered")
  password = request.form['password']
  if len(password) < 6:
    return render_template("anotherfile.html", error_message="Password is too short")
  nickname = request.form['nickname']
  res = g.conn.execute('SELECT count(*) from people').fetchall();
  count = res[0]['count']
  pid = count + 1
  g.conn.execute('INSERT INTO users VALUES ((%s), (%s), (%s), (%s))',pid, nickname, password, email)
  g.conn.execute('INSERT INTO people VALUES ((%s), (%s), (%s), (%s))', pid, '', '1900-1-1', '')
  return render_template("index.html", error_message="Register successfully!")

@app.route('/searchMovies', methods=['POST'])
def searchMovies():
  title = request.form['movie_title']
  username = request.form['username']
  people_id = request.form['pid']
  if len(title) == 0:
    return render_template("main.html", username=username, pid=people_id, error_message="Movie Title cannot be empty")
  
  title = '%' + title.lower() + '%'

  # basic info of the movie
  cmd= 'SELECT * FROM movie where Lower(title) like :name1';
  movie_info= g.conn.execute(text(cmd), name1=title).fetchall();
  #movie_info = g.conn.execute('SELECT * FROM movie where title = (%s)', title).fetchall();
  if len(movie_info) == 0:
    return render_template("main.html", username=username, pid=people_id, error_message="404 NOT FOUND!")
  m_title=movie_info[0]['title']
  date = movie_info[0]['release_date']
  m_type = movie_info[0]['type']
  lang = movie_info[0]['language']
  desc = movie_info[0]['description']
  mid = movie_info[0]['mid']
    
  # avg rate of the movie
  avg = g.conn.execute('SELECT round(avg(rate), 1) FROM rate where mid = (%s) group by mid', mid).fetchall()
  avg = avg[0]['round']
  print avg

  # actor of the movie and their corresponding charactor
  act = g.conn.execute('SELECT name, character_name FROM actor_of, people WHERE actor_of.mid = (%s) and actor_of.pid = people.pid', mid).fetchall()
  actor = {}
  for row in act:
    actor[row['name']] = row['character_name']

  # director of the movie
  director = g.conn.execute('SELECT name FROM directed_by, people WHERE directed_by.mid=(%s) and directed_by.pid = people.pid', mid).fetchall()
  direct = []
  for row in director:
    direct.append(row['name'])

  # movie company of the movie
  company = g.conn.execute('SELECT name from company, made_by where made_by.mid=(%s) and made_by.cid = company.cid', mid).fetchall()
  com = []
  for row in company:
    com.append(row['name'])

  # Trailer of the movie
  trailer = g.conn.execute('SELECT link, view_count, date_released, version from trailer, trailer_of where trailer_of.mid = (%s) and trailer_of.tid = trailer.tid order by version', mid).fetchall()
  t = []
  for row in trailer:
    r = []
    r.append(row['link'])
    r.append(row['view_count'])
    r.append(row['date_released'])
    r.append(row['version'])
    t.append(r)

  return render_template('output.html', mtitle=m_title, type=m_type, date=date, desc = desc, avg=avg, act=actor, director=direct, company=com, trailer = t)



@app.route('/searchActor', methods=['POST'])
def searchActor():
  actor = request.form['actor_name']
  username = request.form['username']
  people_id = request.form['pid']
  if len(actor) == 0:
    return render_template("main.html", username=username, pid=people_id, error_message="Actor Name cannot be empty")
  
  actor = '%' + actor.lower() + '%'  
  # basic info of actor
  cmd = 'SELECT * FROM actor,people where actor.pid=people.pid and Lower(people.name) like :name1';
  actor_info = g.conn.execute(text(cmd), name1=actor).fetchall();
  #actor_info = g.conn.execute('SELECT * FROM actor, people where actor.pid=people.pid and people.name = (%s)', actor).fetchall();
  if len(actor_info) == 0:
    return render_template("main.html",username=username, pid=people_id, error_message="404 NOT FOUND!")
  actor_name = actor_info[0]['name']
  dateofBirth = actor_info[0]['date_of_birth']
  country = actor_info[0]['country']
  tradeMark = actor_info[0]['trade_mark']
  pid = actor_info[0]['pid']
  
  #known for
  knownfor_info = g.conn.execute('SELECT * FROM movie_maker where movie_maker.pid=(%s)', pid).fetchall();
  knownfor=knownfor_info[0]['known_for']
  
  # basic info of the movie
  movie_info = g.conn.execute('SELECT * FROM actor_of, movie WHERE actor_of.pid = (%s) and actor_of.mid = movie.mid', pid).fetchall()
  m=[]
  for row in movie_info:
      r=[]
      r.append(row['title'])
      r.append(row['release_date'])
      r.append(row['type'])
      r.append(row['description'])
      m.append(r)

  
  return render_template('outputactor.html', aname=actor_name, dob=dateofBirth, country=country, tmark = tradeMark, knfor=knownfor, movie=m)


@app.route('/searchDirector', methods=['POST'])
def searchDirector():
  director = request.form['director_name']
  username = request.form['username']
  people_id = request.form['pid']
  if len(director) == 0:
    return render_template("main.html",username=username, pid=people_id, error_message="Director Name cannot be empty")
    
  director = '%' + director.lower() + '%'  
  # basic info of director
  #director_info = g.conn.execute('SELECT * FROM director, people where director.pid=people.pid and people.name = (%s)', director).fetchall();
  cmd= 'SELECT * FROM director,people where director.pid=people.pid and Lower(people.name) like :name1';
  director_info= g.conn.execute(text(cmd), name1=director).fetchall();
  if len(director_info ) == 0:
    return render_template("main.html",username=username, pid=people_id, error_message="404 NOT FOUND!")
  director_name = director_info[0]['name']
  dateofBirth = director_info[0]['date_of_birth']
  country = director_info[0]['country']
  bio = director_info[0]['bio']
  pid = director_info[0]['pid']
  
  #known for
  knownfor_info = g.conn.execute('SELECT * FROM movie_maker where movie_maker.pid=(%s)', pid).fetchall();
  knownfor=knownfor_info[0]['known_for']
  
  # basic info of the movie
  movie_info = g.conn.execute('SELECT * FROM Directed_by, movie WHERE Directed_by.pid = (%s) and Directed_by.mid = movie.mid', pid).fetchall()
  m=[]
  for row in movie_info:
    r=[]
    r.append(row['title'])
    r.append(row['release_date'])
    r.append(row['type'])
    r.append(row['description'])
    m.append(r)

  return render_template('outputdirector.html', dname=director_name, dob=dateofBirth, country=country, bio = bio, knfor=knownfor, movie=m)

@app.route('/searchCompany', methods=['POST'])
def searchCompany():
  company = request.form['company_name']
  username = request.form['username']
  people_id = request.form['pid']
  if len(company) == 0:
    return render_template("main.html",username=username, pid=people_id, error_message="Company Name cannot be empty")

  company = '%' + company.lower() + '%'
  cmd= 'SELECT * FROM Company where Lower(company.name) like :name1';
  company_info= g.conn.execute(text(cmd), name1=company).fetchall();
  # basic info of company
  #company_info = g.conn.execute('SELECT * FROM Company where company.name = (%s)', company).fetchall();
  if len(company_info) == 0:
    return render_template("main.html",username=username, pid=people_id, error_message="404 NOT FOUND!")
  company_name = company_info[0]['name']
  country = company_info[0]['country']
  webpage = company_info[0]['webpage']
  webpage='http://'+webpage
  cid = company_info[0]['cid']
  
  # basic info of the movie
  movie_info= g.conn.execute('SELECT * FROM Made_by, movie WHERE Made_by.cid = (%s) and Made_by.mid = movie.mid', cid).fetchall()
  mov=[]  
  for row in movie_info:
    mov.append(row['title'])
    print mov
  

  return render_template('outputcompany.html', cname=company_name, country=country, website=webpage, movie=mov)

@app.route('/rater', methods=['POST'])
def rate():
  mtitle = request.form['movie_title']
  rate = request.form['rate']
  username = request.form['username']
  pid = request.form['pid']
  print mtitle
  print rate
  print pid
  if len(mtitle) == 0:
    return render_template('main.html',username=username, pid=pid, error_message="Please give the name you want to rate")
  val = 0
  try:
    val = int(rate)
  except ValueError:
    return render_template('main.html',username=username, pid=pid, error_message="Rate is not valid")
  if val <= 0 or val > 10:
    return render_template('main.html',username=username, pid=pid, error_message="Come on! Give a rate in (0, 10]")


  res = g.conn.execute('SELECT * FROM movie where title = (%s)', mtitle).fetchall()
  if len(res) == 0:
    return render_template('main.html',username=username, pid=pid, error_message="Oops! Movie is not found in the system!")
  mid = res[0]['mid']
  ts = datetime.now().strftime('%Y-%m-%d')
  res = g.conn.execute("SELECT * from rate where pid = (%s) and mid = (%s) and time = (%s)", pid, mid, ts).fetchall()
  if len(res) != 0:
    return render_template('main.html',username=username, pid=pid, error_message="Oops! You can only rate the same movie on the same day once!")
  res = g.conn.execute("INSERT INTO rate values ((%s), (%s), (%s), %s)", pid, mid, rate, ts)
  return render_template('afterRate.html')



if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8121, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
