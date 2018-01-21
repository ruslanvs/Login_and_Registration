from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re, md5
app = Flask(__name__)
app.secret_key = "MySessionSecretKey"
mysql = MySQLConnector( app, "login_and_registration")
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route( "/" )
def lr():
    if session['user_id']:
        return redirect( "/welcome" )
    return render_template( "index.html" )

@app.route( "/welcome")
def welcome():
    print "session id:", session['user_id']
    query = "SELECT name FROM users WHERE id = :id"
    parameters = { 'id': session['user_id'] }
    data = {}
    data['name'] = mysql.query_db( query, parameters )[0]['name']

    return render_template( "welcome.html", data = data )

@app.route( "/authorisation", methods = ["POST"] )
def pr():
    if not email_regex.match( request.form['email'] ):
        flash( "Invalid email" )
    else:        
        email = request.form['email']
        pw = request.form['pw']
        query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
        parameters = { 'email': email }
        user = mysql.query_db( query, parameters )
        if not user:
            flash( "Email " + email + " is not registered with any user" )
        else:
            pw_h = md5.new( pw ).hexdigest()
            if user[0]['password'] != pw_h:
                flash( "Wrong password" )
            else:  # succesful login
                session['user_id']= user[0]['id']
                return redirect( "/welcome" )

    return redirect( "/" )

@app.route( "/signup", methods = ["POST"] )
def s():
    error = False

    # FORM INPUT VALIDATIONS
    # VALIDATE NAME
    if len( request.form['name'] ) < 2: # NAME LENGTH
        error = True
        flash( "Name is too short" )
    elif not str.isalpha( str( request.form['name'] ) ): # NAME CONVENTIONS
        error = True
        flash( "Invalid characters in the name" )
    
    # VALIDATE EMAIL
    if not email_regex.match( request.form['email'] ): # EMAIL CONVENTIONS
        error = True
        flash( "Invalid email" )
    else: # CHECK IF EMAIL ALREADY REGISTERED
        email = request.form['email']
        query = "SELECT email FROM users WHERE users.email = :email LIMIT 1"
        parameters = { 'email': email }
        existing_email = mysql.query_db( query, parameters )
        if existing_email:
            error = True
            flash( "Email " + email + " is already in use" )

    # VALIDATE PASSWORD
    if len( str( request.form['pw'] ) ) < 8: # PASSWORD CONVENTIONS
        error = True
        flash( "Password should be at least 8 characters long")
    elif request.form['pw'] != request.form['rpt_pw']: # REPEAT PASSWORD
        error = True
        flash( "Repeat password does not match")

    if error:
        return redirect( "/" )

    else: # INSERT NEW USER INTO THE DATABASE
        print "No errors"
        flash( "User account saved" )
        query = "INSERT INTO users( name, email, password, created_at, updated_at ) VALUES( :name, :email, :pw_h, NOW(), NOW() )"
        parameters = {
            'name': request.form['name'],
            'email': request.form['email'],
            'pw_h': md5.new( request.form['pw'] ).hexdigest()
        }
        mysql.query_db( query, parameters )
        
        # FETCH THE NEW USER ID FROM THE DATABASE FOR SESSION LOGIN
        query = "SELECT id FROM users WHERE email = :email LIMIT 1"
        parameters = { 'email': request.form['email'] }
        session['user_id']= mysql.query_db( query, parameters )[0]['id']
        
    return redirect( "/welcome" )

app.run( debug = True )