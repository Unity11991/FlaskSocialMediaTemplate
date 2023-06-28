from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social_media.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)


app.config['MAIL_SERVER'] = 'your_mail_server'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_username'
app.config['MAIL_PASSWORD'] = 'your_password'
mail = Mail(app)


def generate_reset_token():
    return secrets.token_urlsafe(32)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            error = 'Username already exists. Please try a different username.'
            return render_template('signup.html', error=error)

        if existing_email:
            error = 'Email address already exists. Please try a different email address.'
            return render_template('signup.html', error=error)

        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect(url_for('profile'))

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        return render_template('profile.html', user=user)

    return redirect(url_for('login'))


def send_reset_email(email, token):
    msg = Message('Password Reset', sender='your_email@example.com', recipients=[email])
    msg.body = f"Please click the following link to reset your password: {url_for('reset_password', token=token, _external=True)}"
    mail.send(msg)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate a unique token and save it in the user's record (e.g., in a 'reset_token' field)
            token = generate_reset_token()
            user.reset_token = token
            db.session.commit()

            # Send the reset password email to the user
            send_reset_email(user.email, token)

            # Redirect the user to a page indicating that an email has been sent
            return render_template('password_reset_sent.html')

        # If the email is not found in the database, display an error message
        error = 'Email address not found. Please enter a valid email address.'
        return render_template('forgot_password.html', error=error)

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query




if __name__ == '__main__':
    app.run(debug=True)
