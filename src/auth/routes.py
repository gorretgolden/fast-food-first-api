from src.dbcon.db import conn
from flask import redirect, render_template, request, Blueprint, url_for
from flask import Blueprint, flash, jsonify, render_template, request
import validators
from werkzeug.security import check_password_hash,generate_password_hash
from flask_jwt_extended import unset_jwt_cookies, create_access_token,create_refresh_token,jwt_required,get_jwt_identity
import psycopg2.extras

auth = Blueprint('auth', __name__, url_prefix='/auth')
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

@auth.route('/signup', methods= ['POST','GET'])
def register_user():
  
  if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['user_address']
        password1 = request.form['user_password']
        password2 = request.form['password2']
        
        
        #checking if email exists
        email_exists = cur.execute("SELECT email FROM users WHERE email = %(email)s", {'email':email})
        if email_exists:
              flash('Email address already exists!')
          
         #checking if username exists
        username_exists = cur.execute("SELECT username FROM users WHERE username = %(username)s", {'username':username})
        if username_exists:
              flash('Username already in use!')      
          
          
       #checking if phonenumber exists
        phone_number_exists = cur.execute("SELECT phone_number FROM users WHERE phone_number = %(phone_number)s", {'phone_number':phone_number})
        if phone_number_exists:
              flash('Phone number already in use!')     
        #do passwords match
        if password1!=password2:
              flash("Passwords don\t match!",'error')
        
        if len(password1) < 4:
          flash("Password is too short")  
        
        #username alphabetic
        if username.isalpha():
          flash('Username must be alphabetic')  
          
         #validate email
        if not validators.email(email):
          flash('Please enter a valid email address')      
        
        #creating a hashed password in the database
        hashed_password = generate_password_hash(password1,method="sha256")
        
        #inserting values
        cur.execute("INSERT INTO users (phone_number,username,email,user_address,user_password) VALUES (%s,%s,%s,%s,%s)", (phone_number,username,email,address,hashed_password))
        conn.commit()
        flash('New user added successfully!','success')
        return redirect(url_for('auth.login_user'))
  return render_template('user-sign-up.html')  


@auth.route('/login', methods= ['POST','GET'])
def login_user():
      
      if request.method == "POST" and "email" in request.form and "user_password" in request.form:
          email = request.form['email']
          password = request.form['user_password']
            
          #check if email exits
          cur.execute('SELECT * FROM users WHERE email = %(email)s',{'email':email})
          user = cur.fetchone()
          if user:
                #check if userpassword matches the sha password in db
                password_check = check_password_hash(user['user_password'],password)
                print(password_check)
                if password_check:
                      #create refresh and acces tokens
                      access_token = create_access_token(identity=user['id'])
                      refresh_token = create_refresh_token(identity=user['id'])
                      print(access_token,refresh_token)
                      #redirect the user to home page for succesful login
                      flash('You logged in successfully!','success')
                      return redirect(url_for('main.home'))
          else:
              flash("Incorrect credentials!",'error')

       
            
      return render_template('user-login.html')  





#logout endpoint
@auth.route('/logout')
def logout_user():
    response = jsonify({"msg": "logged out successfully"})
    unset_jwt_cookies(response)
    print(response)
    flash('Your are logged out')
    return redirect(url_for('auth.login_user'))
    
    

#refresh token endpoint
@auth.route('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
      identity = get_jwt_identity()
      access = create_access_token(identity=identity)
      return jsonify({
            'access':access
      })




 


