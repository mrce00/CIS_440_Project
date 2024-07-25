from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from threading import Timer
import webbrowser

app = Flask(__name__)

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the manager login page and authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    mydb = mysql.connector.connect(
        host="107.180.1.16",
        user="summer2024team2",
        password="summer2024team2",
        database="summer2024team2"
    )

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Authentication logic specific to manager
        mycursor = mydb.cursor()
        mycursor.execute("SELECT password FROM manager_table WHERE username = %s", (username,))
        myresult = mycursor.fetchall()

        
        if username == 'manager' and password == 'password':
            return redirect(url_for('dashboard'))

        return 'Invalid Username/Password'
    return render_template('login.html')

# Route for the manager dashboard
@app.route('/dashboard')
def dashboard():
    return 'Manager Dashboard'

# Route for handling button clicks
@app.route('/button_clicked', methods=['POST'])
def button_clicked():
    mydb = mysql.connector.connect(
        host="107.180.1.16",
        user="summer2024team2",
        password="summer2024team2",
        database="summer2024team2"
    )

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM manager_table")
    myresult = mycursor.fetchall()

    # Test by printing results
    return str(myresult)

# Function to automatically open the browser and navigate to the Flask app URL
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

# Main entry point for running the Flask app
if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=False)
