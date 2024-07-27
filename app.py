from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from threading import Timer
import webbrowser

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/button_clicked', methods=['POST'])
def button_clicked():
    # Handle the button click event here
    mydb = mysql.connector.connect(
        host="107.180.1.16",
        user="summer2024team2",
        password="summer2024team2",
        database="summer2024team2"
    )

    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM manager_table")

    myresult = mycursor.fetchall()

    for x in myresult:
        return (x)


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


if __name__ == '__main__':
    # Start a timer to open the browser after Flask starts
    Timer(1, open_browser).start()
    app.run(debug=False)
