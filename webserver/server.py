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
DATABASEURI = "postgresql://qx2155:cj9sw@104.196.175.120/postgres"


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
  '''
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()
  '''
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

'''
# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print name
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  g.conn.execute(cmd, name1 = name, name2 = name);
  return redirect('/')
'''

# merchants index page, list all the dishes
@app.route('/merchants/<uid>')
def merchants_index(uid):
  cur = g.conn.execute('SELECT name FROM Dishes WHERE uid = %d;', uid)
  dishes = cur.fetchall()
  cur.close()
  return render_template("merchants_index.html", dishes=dishes)

# dishes index page, list dish and reviews
@app.route('/merchants/<uid>/dishes/<did>')
def dishes_index(uid, did):
  dish = g.conn.execute('SELECT * FROM Dishes WHERE did = %d;', did)
  review = g.conn.execute('SELECT * FROM Reviews WHERE uid = %d AND did = %d;', uid, did)
  dishes = dish.fetchall()
  reviews = review.fetchall()
  dishes.close()
  reviews.close()
  return render_template("dishes_index.html", dishes=dishes, reviews=reviews)

# add dish
@app.route('/merchants/<uid>/dishes/add', methods=['POST'])
def add_dish(uid):
  name = request.form['name']
  description = request.form['description']
  price = request.form['price']
  category = request.form['category']
  cur = g.conn.execute('SELECT cid FROM Categories WHERE name = %s;', category)
  cid = cur.fetchone()
  cmd = 'INSERT INTO Dishes(name, description, price, uid, cid) VALUES (%s, %s, %f, %d, %d);'
  g.conn.execute(cmd, (name, description, price, uid, cid))
  cur.close()
  return render_template("add_dish.html")

# update an existing dish
@app.route('/merchants/<uid>/dishes/<did>/change', methods=['POST', 'GET'])
def change_dish(uid, did):
  description = request.form['description']
  price = request.form['price']
  cmd = 'UPDATE Dishes SET description = %s, price = %f WHERE uid = %d AND did = %d;'
  g.conn.execute(cmd, (description, price, uid, did))
  return render_template("change_dish.html")

# add a review to an existing dish
@app.route('/merchants/<uid>/dishes/<did>/reviews/add', methods=['POST'])
def add_review(uid, did):
  rev_time = request.form['rev_time']
  rating = request.form['rating']
  comment = request.form['comment']
  cmd = 'INSERT INTO Reviews(uid, did, rev_time, rating, comment) VALUES (%d, %d, %s, %d, %s);'
  g.conn.execute(cmd, (uid, did, rev_time, rating, comment))
  return render_template("add_review.html")

# delete a review
@app.route('/merchants/<uid>/dishes/<did>/reviews/<rev_id>/delete', methods=['GET'])
def delete_review(uid, did, rev_id):
  cmd = 'DELETE FROM Reviews WHERE rev_id = %d;'
  g.conn.execute(cmd, (rev_id))
  return redirect('/merchants/<uid>/dishes/<did>', uid=uid, did=did)

# add a category
@app.route('/categories/add', methods=['POST'])
def add_category():
  name = request.form['name']
  description = request.form['description']
  cmd = 'INSERT INTO Categories(name, description) VALUES (%s, %s);'
  g.conn.execute(cmd, (name, description))
  return render_template("add_category.html")


'''
@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()
'''

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
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
