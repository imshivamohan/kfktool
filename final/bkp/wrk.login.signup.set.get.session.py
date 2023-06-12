import pg8000
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from datetime import datetime, timedelta

app = Flask(__name__)

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=2)
Session(app)

# Check session timeout on every request
@app.before_request
def check_session_timeout():
    if 'last_activity' in session:
        # Calculate the time difference between the current time and the last activity time
        last_activity = session['last_activity']
        current_time = datetime.now()
        time_diff = current_time - last_activity

        # Check if the session has exceeded the session lifetime
        if time_diff > app.config['PERMANENT_SESSION_LIFETIME']:
            session.clear()  # Clear the session data
            return redirect('/login')  # Redirect the user to the login page or any appropriate page

    # Update the last activity time in the session
    session['last_activity'] = datetime.now()


def get_connection():
    return pg8000.connect(
        host="localhost",
        user="kfkuser",
        password="kfk@9989Ss",
        database="kfkdata",
        port=5432
    )


@app.route('/')
def index():
    return render_template('initialpage.html', display_login=True)


@app.route('/home')
def home():
    if 'username' in session:
        success_message = session.get('success_message')
        return render_template('initialpage.html', display_home=True, success_message=success_message)
    else:
        return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect('/home')  # Redirect to home if user is already logged in

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user exists in the database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            if user[2] == password:
                # Valid login, store user session
                session['username'] = username
                session['success_message'] = "Login successful!"
                session.permanent = True  # Enable permanent session
                return redirect('/home')
            else:
                # Invalid password, ask for correct password
                error_message = "Invalid password. Please enter the correct password."
                return render_template('initialpage.html', error_message=error_message, display_login=True)

        else:
            # User does not exist, redirect to signup
            error_message = "Username not found. Please signup."
            return render_template('initialpage.html', error_message=error_message, display_signup=True)

    return render_template('initialpage.html')


@app.route('/set')
def set():
    if 'username' not in session:
        return redirect('/login')  # Redirect to login if user is not logged in
    return render_template('initialpage.html', display_home=True, display_setconfig=True)


@app.route('/signup', methods=['POST'])
def signup():
    if 'username' in session:
        return redirect('/home')  # Redirect to home if user is already logged in

    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    # Check if username already exists in the database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        # Username already exists, show error message
        error_message = "Username already taken. Please choose a different username."
        return render_template('initialpage.html', error_message=error_message, display_signup=True)
    else:
        # Create new user in the database
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                       (username, password, email))
        conn.commit()
        cursor.close()
        conn.close()

        # Signup successful, redirect to login page
        success_message = "Signup successful! Please log in."
        return render_template('initialpage.html', display_login=True, success_message=success_message)


@app.route('/setconfig', methods=['GET', 'POST'])
def set_config():
    if 'username' not in session:
        return redirect('/login')  # Redirect to login if user is not logged in

    if request.method == 'POST':
        api_key = request.form['api_key']
        api_secret = request.form['api_secret']
        schema_api_key = request.form['schema_api_key']
        schema_api_secret = request.form['schema_api_secret']
        schema_url = request.form['schema_url']
        bootstrap_server = request.form['bootstrap_server']

        username = session['username']  # Get the current user's username from the session

        # Check if the user already has a configuration in the database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_config WHERE username = %s", (username,))
        existing_config = cursor.fetchone()

        if existing_config:
            # Update the existing configuration
            cursor.execute("UPDATE user_config SET api_key = %s, api_secret = %s, schema_api_key = %s, "
                           "schema_api_secret = %s, schema_url = %s, bootstrap_server = %s WHERE username = %s",
                           (api_key, api_secret, schema_api_key, schema_api_secret, schema_url, bootstrap_server, username))
            success_message = "Configuration updated successfully!"
        else:
            # Insert a new configuration for the user
            cursor.execute("INSERT INTO user_config (username, api_key, api_secret, schema_api_key, "
                           "schema_api_secret, schema_url, bootstrap_server) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (username, api_key, api_secret, schema_api_key, schema_api_secret, schema_url, bootstrap_server))
            success_message = "Configuration saved successfully!"

        conn.commit()
        cursor.close()
        conn.close()

        session['success_message'] = success_message
        return redirect('/home')

    return render_template('initialpage.html', display_setconfig=True)


@app.route('/get')
def get_config():
    if 'username' not in session:
        return redirect('/login')  # Redirect to login if user is not logged in

    conn = get_connection()
    cursor = conn.cursor()
    username = session['username']
    select_query = "SELECT * FROM user_config WHERE username = %s"
    cursor.execute(select_query, (username,))
    config = cursor.fetchone()
    conn.close()

    if config:
        # Convert the configuration data into a dictionary for easier access in the HTML template
        config_data = {
            'API Key': config[2],
            'API Secret': config[3],
            'Schema API Key': config[4],
            'Schema API Secret': config[5],
            'Schema URL': config[6],
            'Bootstrap Server': config[7]
        }

        return render_template('initialpage.html', display_getconfig=True, display_home=True, config_data=config_data)
    else:
        error_message = "No configuration found for the user."
        return render_template('initialpage.html', error_message=error_message, display_home=True)


if __name__ == '__main__':
    app.run(host='localhost', port=8501)
