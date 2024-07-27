from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from threading import Timer
import webbrowser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a strong secret key

# Example data
accounts = [
    {'id': 1, 'username': 'user1', 'email': 'user1@example.com', 'role': 'user'},
    {'id': 2, 'username': 'user2', 'email': 'user2@example.com', 'role': 'manager'},
    {'id': 3, 'username': 'user3', 'email': 'user3@example.com', 'role': 'user'}
]

surveys = []  # List to store survey responses

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'magarvin':
        user = User()
        user.id = user_id
        return user
    return None

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
        
        if username == 'magarvin' and password == 'CIS440':
            user = User()
            user.id = username
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    
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
    return render_template('dashboard.html', accounts=accounts, surveys=surveys)

@app.route('/submit_survey', methods=['POST'])
@login_required
def submit_survey():
    q1 = request.form.get('q1')
    q2 = request.form.get('q2')
    q3 = request.form.get('q3')
    q4 = request.form.get('q4')
    comments = request.form.get('comments')

    survey_id = len(surveys) + 1
    surveys.append({
        'id': survey_id,
        'q1': q1,
        'q2': q2,
        'q3': q3,
        'q4': q4,
        'comments': comments
    })

    return jsonify({'status': 'success'})

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

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=False, port=5001)