import datetime
import random

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from threading import Timer
import webbrowser
import mysql.connector
import uuid
import csv
import os
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a strong secret key

# Set threshold value for write-in answers
threshold = 3

# Example data
accounts = [
    {'id': 1, 'username': 'user1', 'email': 'user1@example.com', 'role': 'user'},
    {'id': 2, 'username': 'user2', 'email': 'user2@example.com', 'role': 'manager'},
    {'id': 3, 'username': 'user3', 'email': 'user3@example.com', 'role': 'user'}
]

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Defining default values
default_data = {
    'write_in': 3,
    'specific_question': 2,
    'general_question': 3
}

# Check if the file exists, if not create it with default values

if not os.path.exists('question_points.csv'):
    with open('question_points.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['question_type', 'point_value'])
        for question, points in default_data.items():
            writer.writerow([question, points])

# Read the CSV file
question_points = {}
with open('question_points.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        question_points[row[0]] = int(row[1])
        
@app.route('/question_values', methods=['GET', 'POST'])
def question_values():
    if request.method == 'POST':
        question_points['write_in'] = int(request.form['write_in_points'])
        question_points['specific_question'] = int(request.form['specific_question_points'])
        question_points['general_question'] = int(request.form['general_question_points'])

        # Update the CSV file
        with open('question_points.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['question_type', 'point_value'])
            for question, points in question_points.items():
                writer.writerow([question, points])
        flash('Points updated successfully!')
        return redirect(url_for('index'))
    else:
        return render_template('question_values.html', 
                               write_in_points=question_points['write_in'],
                               specific_question_points=question_points['specific_question'],
                               general_question_points=question_points['general_question'])


# User class
class User(UserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    if user_id == user_id:
        user = User()
        user.id = user_id
        return user


# WTForms LoginForm
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')


# WTForms SurveyForm
class SurveyForm(FlaskForm):
    q1 = StringField('Did you feel productive this week?', validators=[DataRequired()])
    q2 = StringField('Did you have any obstacles that affected your work?', validators=[DataRequired()])
    q3 = StringField('Were you satisfied with the support you received?', validators=[DataRequired()])
    q4 = StringField('Did you meet your goals for the week?', validators=[DataRequired()])
    comments = TextAreaField('Additional Comments')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        mydb = mysql.connector.connect(
            host="107.180.1.16",
            user="summer2024team2",
            password="summer2024team2",
            database="summer2024team2"
        )

        mycursor = mydb.cursor()
        mycursor.execute("SELECT password FROM manager_table WHERE username = %s", (username,))
        myresult = mycursor.fetchall()
        mycursor.close()

        try:
            if password == myresult[0][0]:
                user = User()
                user.id = username
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Login unsuccessful. Please check your username and password.', 'danger')
                return render_template('login.html', form=form)
        except:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', accounts=accounts)


@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    # Retrieve form data
    q1 = request.form.get('q1')
    q1_details = request.form.get('q1Details') if q1 in ['1', '2', '3'] else None
    q2 = request.form.get('q2')
    q2_details = request.form.get('q2Details') if q2 in ['1', '2', '3'] else None
    q3 = request.form.get('q3')
    q3_details = request.form.get('q3Details') if q3 in ['1', '2', '3'] else None
    q4 = request.form.get('q4')
    q4_details = request.form.get('q4Details') if q4 in ['1', '2', '3'] else None
    comments = request.form.get('comments')
    datenow = str(datetime.datetime.now())

    mydb = mysql.connector.connect(
        host="107.180.1.16",
        user="summer2024team2",
        password="summer2024team2",
        database="summer2024team2"
    )
    try:
        mycursor = mydb.cursor()
        sql = "INSERT INTO responses_table (q1, q1_details, q2, q2_details, q3, q3_details, q4, q4_details, comments, period) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val = (q1, q1_details, q2, q2_details, q3, q3_details, q4, q4_details, comments, datenow)
        mycursor.execute(sql, val)
        mydb.commit()

        mycursor.close()
        flash("Survey Submitted!", "success")
        return redirect(url_for('index'))
    except Exception as error:
        mydb.rollback()  # Rollback to handle errors
        mycursor.close()
        flash(f"An error occurred: {error}", "error")
        return redirect(url_for('index'))

@app.route('/set_survey_date_range', methods=['POST'])
@login_required
def set_survey_date_range():
    start_date = request.form.get('startDate')
    end_date = request.form.get('endDate')

    # Connect to the database
    mydb = mysql.connector.connect(
        host="107.180.1.16",
        user="summer2024team2",
        password="summer2024team2",
        database="summer2024team2"
    )
    try:
        mycursor = mydb.cursor()
        # Assuming you have a table `survey_settings` with columns `start_date` and `end_date`
        sql = "UPDATE survey_settings SET start_date = %s, end_date = %s WHERE id = 1"
        val = (start_date, end_date)
        mycursor.execute(sql, val)
        mydb.commit()

        flash('Survey date range updated successfully!')
    except Exception as e:
        flash(f'Error: {str(e)}')
    finally:
        mycursor.close()
        mydb.close()

    return redirect(url_for('dashboard'))

@app.route('/set_num_ques')
@login_required
def set_num_ques():
    return render_template('set_num_ques.html')


@app.route('/set_num_ques_value', methods=['POST'])
@login_required
def set_num_ques_value():
    num = request.form.get('numQuestions')
    mydb = mysql.connector.connect(
        host="107.180.1.16",
        user="summer2024team2",
        password="summer2024team2",
        database="summer2024team2"
    )
    try:
        mycursor = mydb.cursor()
        query = "UPDATE ques_num SET value = %s WHERE public_key = 1"
        mycursor.execute(query, (num,))
        mydb.commit()
        mycursor.close()
        flash("Question Number updated!", "success")
        return redirect(url_for('set_num_ques'))
    except Exception as error:
        mydb.rollback()  # Rollback to handle errors
        mycursor.close()
        flash(f"An error occurred: {error}", "error")
        return redirect(url_for('set_num_ques'))


@app.route('/create_account', methods=['POST'])
@login_required
def create_account():
    # Placeholder for account creation logic
    return jsonify({'status': 'success'})


@app.route('/edit_account/<int:account_id>', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    # Placeholder for editing account logic
    return f"Edit Account {account_id}"


@app.route('/delete_account/<int:account_id>')
@login_required
def delete_account(account_id):
    # Placeholder for deleting account logic
    return redirect(url_for('dashboard'))


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5001/')


# In-memory databases for simplicity
general_questions = []  # List to store general questions
department_questions = {}  # Dictionary to store department-specific questions
respondent_ratings = {}  # Dictionary to store respondent ratings

# Database configuration using provided credentials
db_config = {
    'user': 'summer2024team2',
    'password': 'summer2024team2',
    'host': '107.180.1.16',
    'database': 'summer2024team2'
}

@app.route('/add_specific_question', methods=['POST'])
@login_required
def add_specific_question():
    question = request.form['specific_question']
    department = request.form['department']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Get the next question number
    cursor.execute("SELECT COALESCE(MAX(question_number), 0) + 1 FROM specific_questions")
    next_question_number = cursor.fetchone()[0]

    sql = "INSERT INTO specific_questions (question_number, question, department) VALUES (%s, %s, %s)"
    val = (next_question_number, question, department)

    cursor.execute(sql, val)
    conn.commit()

    cursor.close()
    conn.close()

    return '', 200  # Return success status

@app.route('/add_general_question', methods=['POST'])
@login_required
def add_general_question():
    question = request.form['general_question']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Get the next question number
    cursor.execute("SELECT COALESCE(MAX(question_number), 0) + 1 FROM general_questions")
    next_question_number = cursor.fetchone()[0]

    sql = "INSERT INTO general_questions (question_number, question) VALUES (%s, %s)"
    val = (next_question_number, question)

    cursor.execute(sql, val)
    conn.commit()

    cursor.close()
    conn.close()

    return '', 200  # Return success status



@app.route('/questions')
@login_required
def questions():
    return render_template('questions.html')

# Endpoint to rate a question and possibly trigger a follow-up
@app.route('/rate_question', methods=['POST'])
def rate_question():
    respondent_id = request.json.get('respondent_id')
    question_id = request.json.get('question_id')
    rating = request.json.get('rating')

    if respondent_id not in respondent_ratings:
        respondent_ratings[respondent_id] = {}
    respondent_ratings[respondent_id][question_id] = rating

    if rating < 3:
        return jsonify({'status': 'success', 'follow_up': 'Please provide more details'})
    return jsonify({'status': 'success', 'message': 'Thank you for your feedback'})

# Endpoint to generate a reward ID and store it in the database.
@app.route('/generate_reward_id')
def generate_reward_id():
    new_reward_id = random.randint(10000, 99999)

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO rewards_table (reward_id, points) VALUES (%s, %s)"
        val = (new_reward_id, 0)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return jsonify({'value': new_reward_id})
    except Exception as error:
        conn.rollback()  # Rollback to handle errors
        cursor.close()
        flash(f"An error occurred: {error}", "error")
        return redirect(url_for('index'))

@app.route('/survey_results')
@login_required
def survey_results():
    # Connect to the database
    mydb = mysql.connector.connect(
        host="107.180.1.16",
        user="summer2024team2",
        password="summer2024team2",
        database="summer2024team2"
    )
    try:
        mycursor = mydb.cursor(dictionary=True)  # Use dictionary=True for easier access to column names
        mycursor.execute("SELECT * FROM responses_table")
        surveys = mycursor.fetchall()
    except Exception as e:
        flash(f'Error fetching survey results: {str(e)}')
        surveys = []
    finally:
        mycursor.close()
        mydb.close()

    return render_template('survey_results.html', surveys=surveys)


# def shuffle_data():
#     try:
#         # Connect to the database with a timeout
#         conn = mysql.connector.connect(**db_config, connect_timeout=10)
#         cursor = conn.cursor()
    
#         # Shuffle general_questions table
#         query = f"SELECT * FROM general_questions ORDER BY RAND()"
#         cursor.execute(query)
#         rows = cursor.fetchall()
#         query = f"DELETE FROM general_questions"
#         cursor.execute(query)
#         query = f"INSERT INTO general_questions (question_number, question) VALUES (%s, %s)"
#         for row in rows:
#             cursor.execute(query, row)
            
#         # Shuffle specific_questions table
#         query = f"SELECT question_number, question, department FROM specific_questions ORDER BY RAND()"
#         cursor.execute(query)
#         rows = cursor.fetchall()
#         query = f"DELETE FROM specific_questions"
#         cursor.execute(query)
#         query = f"INSERT INTO specific_questions (question_number, question, department) VALUES (%s, %s, %s)"
#         for row in rows:
#             cursor.execute(query, row)
#         # Commit the changes
#         try:
#             conn.commit()
#         except mysql.connector.Error as err:
#             print(f"Error committing changes: {err}")
#             return f"Error committing changes: {err}"
#         # Close the cursor and connection
#         try:
#             cursor.close()
#         except Exception as e:
#             print(f"Error closing cursor: {e}")
#         try:
#             conn.close()
#         except Exception as e:
#             print(f"Error closing connection: {e}")
#         print("Data shuffled successfully!")
#         return "Data shuffled successfully!"
#     except mysql.connector.Error as err:
#         print(f"Error shuffling data: {err}")
#         return f"Error shuffling data: {err}"
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return f"An error occurred: {e}"

def shuffle_data():
    try:
        # Connect to the database with a timeout
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor() 
        # Shuffle specific_questions table
        query = f"SELECT * FROM specific_questions ORDER BY RAND()"
        cursor.execute(query)
        rows = cursor.fetchall()
        # Delete existing data
        query = "DELETE FROM specific_questions"
        cursor.execute(query)
        # Insert shuffled data
        query = "INSERT INTO specific_questions (question_number, question, department) VALUES (%s, %s, %s)"
        for row in rows:
            cursor.execute(query, row) 
        # Commit the changes
        conn.commit()
        # Shuffle general_questions table
        query = f"SELECT * FROM general_questions ORDER BY RAND()"
        cursor.execute(query)
        rows = cursor.fetchall()
        # Delete existing data
        query = "DELETE FROM general_questions"
        cursor.execute(query)
        # Insert shuffled data
        query = "INSERT INTO general_questions (question_number, question) VALUES (%s, %s)"
        for row in rows:
            cursor.execute(query, row)   
        # Commit the changes
        conn.commit()
        print("Data shuffled successfully!")
    except mysql.connector.Error as err:
        # Roll back the changes if an error occurs
        conn.rollback()
        print(f"Error: {err}")
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()
  
@app.route('/shuffle_data', methods=['POST'])
def shuffle_data_route():
    shuffle_data()
    return 'Data shuffled successfully!', 200

# Define a function to get questions from the database
def get_questions(department):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('SELECT question FROM specific_questions WHERE department = %s', (department,))
    specific_questions = cursor.fetchall()
    cursor.execute('SELECT question from general_questions')
    general_questions = cursor.fetchall()
    conn.close()
    questions_to_return = {'general_questions': general_questions[:2],
                           'specific_questions': specific_questions[:2]}
    return questions_to_return


# Define a route to get questions for a specific department
@app.route('/get_questions', methods=['POST'])
def get_questions_route():
    data = request.get_json()
    department = data['department']
    questions = get_questions(department)
    return jsonify(questions)

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=False, port=5001)
