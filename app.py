import datetime
import random
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from threading import Timer
from werkzeug.utils import secure_filename
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
from werkzeug.utils import secure_filename

@app.route('/storefront')
@login_required
def storefront():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM storefront")
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('storefront.html', products=products)

@app.route('/add_item', methods=['POST'])
@login_required
def add_item():
    title = request.form.get('title')
    description = request.form.get('description')
    points = request.form.get('points')
    image = request.files.get('image')

    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join('static', 'uploads', filename))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    sql = "INSERT INTO storefront (product_title, description, image, points) VALUES (%s, %s, %s, %s)"
    val = (title, description, filename, points)
    cursor.execute(sql, val)
    conn.commit()
    
    cursor.close()
    conn.close()
    
    flash('Product added successfully!', 'success')
    return redirect(url_for('storefront'))

@app.route('/update_item/<int:item_id>', methods=['POST'])
@login_required
def update_item(item_id):
    title = request.form.get('title')
    description = request.form.get('description')
    points = request.form.get('points')
    image = request.files.get('image')
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join('static', 'uploads', filename))
        sql = "UPDATE storefront SET product_title = %s, description = %s, image = %s, points = %s WHERE id = %s"
        val = (title, description, filename, points, item_id)
    else:
        sql = "UPDATE storefront SET product_title = %s, description = %s, points = %s WHERE id = %s"
        val = (title, description, points, item_id)
    
    cursor.execute(sql, val)
    conn.commit()
    
    cursor.close()
    conn.close()
    
    flash('Product updated successfully!', 'success')
    return redirect(url_for('storefront'))


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
    data = request.form
    questions = [key for key in data.keys() if key.startswith('q') and not key.endswith('_type') and not key.endswith('Details')]
    answers = {}
    for question in questions:
        answers[question] = {
            'answer': data.get(question),
            'type': data.get(f'{question}_type'),
            'details': data.get(f'{question}Details')
        }
    comments = data.get('comments')
    reward_id = data.get('rewardID')
    datenow = datetime.datetime.now()

    with open('question_points.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        question_types = {row[0]: int(row[1]) for row in reader}
        
    write_in_point_value = question_types['write_in']
    
    # Calculate the total point value
    total_point_value = 0
    for question, answer in answers.items():
        total_point_value += question_types.get(answer['type'], 0)
        if answer['details']:
            total_point_value += write_in_point_value

    if comments:
        total_point_value += write_in_point_value
        
    mydb = mysql.connector.connect(
        host="107.180.1.16",
        user="summer2024team2",
        password="summer2024team2",
        database="summer2024team2"
    )
    try:
        mycursor = mydb.cursor()

        # Insert data into responses_table
        sql = "INSERT INTO responses_table (comments, period, reward_id) VALUES (%s, %s, %s)"
        val = (comments, datenow, reward_id)
        mycursor.execute(sql, val)
        response_id = mycursor.lastrowid
        mydb.commit()

        # Get the question IDs from the questions_table
        question_ids = {}
        for question in questions:
            sql = "SELECT question_id FROM questions_table WHERE question_text = %s"
            val = (question,)
            mycursor.execute(sql, val)
            result = mycursor.fetchone()
            if result:
                question_ids[question] = result[0]
            else:
                # If the question is not found in the questions_table, insert it
                sql = "INSERT INTO questions_table (question_text, question_type) VALUES (%s, %s)"
                val = (question, answers[question]['type'])
                mycursor.execute(sql, val)
                question_ids[question] = mycursor.lastrowid
                mydb.commit()

        # Insert data into answers_table
        for question, answer in answers.items():
            sql = "INSERT INTO answers_table (response_id, question_id, answer, details) VALUES (%s, %s, %s, %s)"
            val = (response_id, question_ids[question], answer['answer'], answer['details'])
            mycursor.execute(sql, val)
            mydb.commit()

        # Update the points in the rewards_table
        sql = "UPDATE rewards_table SET points = points + %s WHERE reward_id = %s"
        val = (total_point_value, reward_id)
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
    num_general = request.form.get('numGeneralQuestions')
    num_specific = request.form.get('numSpecificQuestions')
    
    mydb = mysql.connector.connect(
        host="107.180.1.16",
        user="summer2024team2",
        password="summer2024team2",
        database="summer2024team2"
    )
    try:
        mycursor = mydb.cursor()
        
        query = "UPDATE ques_num SET value = %s WHERE public_key = 1"
        mycursor.execute(query, (num_general,))
        
        query = "UPDATE ques_num SET value = %s WHERE public_key = 2"
        mycursor.execute(query, (num_specific,))

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

def get_survey_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = '''
    SELECT r.username, a1.answer AS q1, a2.answer AS q2, a3.answer AS q3, a4.answer AS q4, r.comments
    FROM responses_table r
    JOIN answers_table a1 ON r.q1_id = a1.id
    JOIN answers_table a2 ON r.q2_id = a2.id
    JOIN answers_table a3 ON r.q3_id = a3.id
    JOIN answers_table a4 ON r.q4_id = a4.id;
    '''
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data

# @app.route('/')
# def survey_results():
#     surveys = get_survey_data()
#     return render_template('survey_results.html', surveys=surveys)


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
        
        # SQL query to get survey results, including questions and answers
        query = """
        SELECT r.response_id, r.comments, r.period, r.reward_id, 
               q.question_id, q.question_text, a.answer_id, a.answer_text
        FROM responses_table r
        LEFT JOIN questions_table q ON r.question_id = q.question_id
        LEFT JOIN answers_table a ON r.answer_id = a.answer_id;
        """
        mycursor.execute(query)
        surveys = mycursor.fetchall()
    except Exception as e:
        flash(f'Error fetching survey results: {str(e)}')
        surveys = []
    finally:
        mycursor.close()
        mydb.close()

    return render_template('survey_results.html', surveys=surveys)






def shuffle_table(conn, cursor, table_name, columns):
    try:
        print(f"Shuffling {table_name} table")
        
        # Retrieve rows from the table
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        rows = list(cursor.fetchall())
        if not rows:
            print(f"No data in {table_name} table")
            return False
        
        # Check if the table has a department column
        has_department = "department" in columns
        
        if has_department:
            # Separate the primary key column and the department column from the other columns
            primary_key_column = columns[0]
            department_column = columns[2]
            other_columns = columns[1:2] + columns[3:]
            
            # Group the rows by department
            department_rows = {}
            for row in rows:
                department_value = row[columns.index(department_column)]
                if department_value not in department_rows:
                    department_rows[department_value] = []
                department_rows[department_value].append(row)
            
            # Shuffle the rows within each department
            shuffled_rows = []
            for department, department_row_list in department_rows.items():
                transposed_department_rows = list(map(list, zip(*department_row_list)))
                for i in range(1, len(transposed_department_rows)):
                    random.shuffle(transposed_department_rows[i])
                shuffled_department_rows = list(map(list, zip(*transposed_department_rows)))
                shuffled_rows.extend(shuffled_department_rows)
        else:
            # Transpose the data (swap rows and columns)
            transposed_rows = list(map(list, zip(*rows)))
            
            # Shuffle each column (now a row)
            for row in transposed_rows:
                random.shuffle(row)
            
            # Transpose it back
            shuffled_rows = list(map(list, zip(*transposed_rows)))
        
        # Delete existing data in the table
        query = f"DELETE FROM {table_name}"
        cursor.execute(query)
        
        # Re-insert the shuffled rows
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        for row in shuffled_rows:
            cursor.execute(query, row)
        
        # Commit the changes
        conn.commit()
        print(f"Changes committed for {table_name} table")
        
        return True
    except mysql.connector.Error as err:
        # Roll back the changes if an error occurs
        print(f"Error: {err}")
        conn.rollback()
        return False

def shuffle_data(conn, cursor):
    tables_to_shuffle = {
        "specific_questions": ["question_number", "question", "department"],
        "general_questions": ["question_number", "question"]
    }
    
    for table, columns in tables_to_shuffle.items():
        if not shuffle_table(conn, cursor, table, columns):
            print(f"Error shuffling {table} table")
            return False
    
    print("Data shuffled successfully!")
    return True

@app.route('/shuffle_data', methods=['POST'])
def shuffle_data_route():
    print("Shuffle data route called")
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        conn.start_transaction()
        if shuffle_data(conn, cursor):
            conn.commit()
            return jsonify({"message": "Data shuffled successfully!"}), 200
        else:
            conn.rollback()
            return jsonify({"error": "Error shuffling data"}), 500
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'conn' in locals():
            conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Define a function to get questions from the database
def get_questions(department):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Fetch the number of questions to display from the ques_num table
    cursor.execute('SELECT value FROM ques_num WHERE question_type = %s', ('general',))
    general_num_questions = cursor.fetchone()[0]
    cursor.execute('SELECT value FROM ques_num WHERE question_type = %s', ('specific',))
    specific_num_questions = cursor.fetchone()[0]
    
    # Fetch the questions from the specific and general questions tables
    cursor.execute('SELECT question FROM specific_questions WHERE department = %s', (department,))
    specific_questions = cursor.fetchall()[:specific_num_questions]
    cursor.execute('SELECT question from general_questions')
    general_questions = cursor.fetchall()[:general_num_questions]
    
    conn.close()
    questions_to_return = {'general_questions': general_questions,
                           'specific_questions': specific_questions}
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
