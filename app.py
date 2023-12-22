from bson import ObjectId
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import timedelta
from werkzeug.exceptions import abort
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import re


app = Flask(__name__)

CLIENT=MongoClient("localhost:27017")
DB = CLIENT.Users
COLLECTION_USERS = DB.Users

app.config['SECRET_KEY'] = 'your secret key'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    user_data = DB.Users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data['_id'], user_data['username'], user_data['email'], user_data['password'])
    return None

class User(UserMixin):
    def __init__(self, user_id,username,email,password):
        self.id = user_id
        self.username = username
        self.email = email
        self.password = password
    # Implement the required methods for Flask-Login
    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False


def is_password_strong(password):
    # Minimum 8 characters, at least one uppercase letter, one lowercase letter, one number, and one special character
    pattern = r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}'
    return re.match(pattern, password) is not None


def get_task(task_id):
    task = DB.Task.find_one({'_id': ObjectId(task_id)})
    if task is None:
        abort(404)
    return task

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        user = DB.Users.find_one({'username':username})
        em = DB.Users.find_one({'email':email})

        # Validate password strength
        if not is_password_strong(password):
            flash('Password is not strong enough. It must have at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character.', 'error')
            return redirect(url_for('register'))
            # Check if passwords match
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        elif user != None:
            flash('User already exist!','error')
            return redirect(url_for('register'))
        elif em != None:
            flash('Email is already in use!','error')
            return redirect(url_for('register'))
        else:
            # Hash the password
            hashed_password = generate_password_hash(password)
      
            DB.Users.insert_one({'username': username, 'email': email, 'password': hashed_password})
            flash('Registration successful!', 'success')
            return render_template('success.html', username=username)

    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        
        user = DB.Users.find_one({'username':identifier})

        if not user:
            user = DB.Users.find_one({'email':identifier})
        else:
            user = DB.Users.find_one({'username':identifier})

        if user and check_password_hash(user['password'], password):
            # Use Flask-Login's login_user function to log in the user
            u = User(user['_id'], user['username'], user['email'], user['password'])
            login_user(u, remember=True)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')
    # If login fails, or if it's a GET request, redirect to the login page


@app.route('/')
#@login_required
def index():
    try:
        if current_user.is_authenticated:
            tasks = list(DB.Task.find({'userID': ObjectId(current_user.id)}))
            return render_template('index.html', tasks=tasks)
        else:
            return redirect(url_for('login'))
    except PyMongoError as e:
        flash(f"No tasks to show... {e}")
        return render_template('index.html')
    

@app.route('/<string:task_id>')
#@login_required
def task(task_id):
    task = DB.Task.find_one({'_id': ObjectId(task_id)})

    if task and task.get('userID') != current_user.id:
        flash('You do not have permission to view this task.', 'error')
        return redirect(url_for('index'))

    else:
        return render_template('task.html', task=task)


@app.route('/create', methods=['GET','POST'])
@login_required
def create():
    if request.method == 'POST':
        Title = request.form['tName']
        content = request.form['tDescription']
        DueDate = request.form['endDate']

        DB.Task.insert_one({"tName": Title, "tDescription": content, "endDate": DueDate, "userID" : ObjectId(current_user.id)})
        flash("note created successfully")
        return redirect(url_for('index'))  
    return render_template('create.html')

@app.route('/<string:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    task = get_task(id)

    if request.method == 'POST':
        Title = request.form['tName']
        content = request.form['tDescription']
        DueDate = request.form['endDate']

        if not Title:
            flash('Task name is required!')
        else:
            DB.Task.update_one({"_id":ObjectId(id)},{"$set":{"tName": Title, "tDescription": content, "endDate": DueDate}})
            flash('Task updated successfully!')
            return redirect(url_for('index'))
    return render_template('edit.html', task=task)

@app.route('/<string:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if request.method == 'POST':
        DB.Task.delete_one({"_id":ObjectId(id)})
        flash('task deleted successfully!')
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
