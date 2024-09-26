from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors 
import MySQLdb.cursors, re, hashlib


app = Flask(__name__)
if __name__ =="__main__":
    app.run(debug = True)

#Secret Key for extra protection (first initial + last digit of birth year)
app.secret_key = 'S9S3L2R'

#SQL database connection 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']= 'Losartan50mg?'
app.config['MYSQL_DB'] = 'pythonlogin'

# initialize MySQL 
mysql = MySQL(app)


@app.route('/pythonlogin', methods = ['GET', 'POST'])
def login():
    # Output message if something goes wrong
    msg = ''

    # Check if Username and Password POST requests exist
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Log the incoming username and password
        print(f"Username: {username}, Password: {password}")

        # Check if account exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()

        # Log the account details
        print(f"Account: {account}")

        if account:
            # Create session data
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Log success message
            print("Logged in successfully!")
            # Redirect to homepage
            return redirect(url_for('home'))
        else:
            # Account does not exist or username/password incorrect
            msg = 'Incorrect username or password.'
            print(msg)

    return render_template('index.html', msg=msg)


def home():
    return 'Hello, Flask!'
    

@app.route('/pythonlogin/logout')
def logout():
    # remove session data
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    #return to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/register', methods=['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            # Check if an account exists with this username
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()

            if account:
                msg = 'Account already exists'
            elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                msg = 'Invalid email address'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers.'
            elif not username or not password or not email:
                msg = 'Please fill out the form.'
            else:
                # Hash the password
                hashed_password = hashlib.sha1((password + app.secret_key).encode()).hexdigest()
                

                # Create a new account in the database
                cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)', (username, hashed_password, email))
                mysql.connection.commit()
                msg = 'Account successfully created!'

        except Exception as e:
            print(f"Error: {str(e)}")  # Print any SQL or internal errors for debugging
            msg = 'An error occurred during registration.'

    elif request.method == 'POST':
        msg = 'Please fill out the registration form!'

    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for logged in users
@app.route('/pythonlogin/home')
def home():
    # Check if the user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for logged in users
@app.route('/pythonlogin/profile')
def profile():
    # Check if the user is logged in
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not logged in redirect to login page
    return redirect(url_for('login'))


 
