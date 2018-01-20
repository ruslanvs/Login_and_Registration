from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
app = Flask(__name__)
app.secret_key = "MySessionSecretKey"
mysql = MySQLConnector( app, "login_and_registration")

@app.route( "/" )
def lr():
    return render_template( "index.html" )

app.run( debug = True )