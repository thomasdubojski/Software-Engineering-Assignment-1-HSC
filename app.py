# importing required add-ons
from flask import Flask, request, render_template, redirect, url_for, send_from_directory # pyright: ignore[reportMissingImports]
from flask_sqlalchemy import SQLAlchemy # pyright: ignore[reportMissingImports]
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash # pyright: ignore[reportMissingImports]
from flask import session # pyright: ignore[reportMissingImports]
from sqlalchemy import CheckConstraint # pyright: ignore[reportMissingImports]
import time

# creating engine for site
app = Flask(__name__)
app.secret_key = 'key'

app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///tastetracker_td.db'
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db= SQLAlchemy(app) 

#creating db schema
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date, default=datetime.utcnow)

    reviews = db.relationship("Review", backref='author', lazy=True)

class Review(db.Model):
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    restaurant_name = db.Column(db.String(100), nullable=False)
    cuisine_type = db.Column(db.String(100), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Date, default=datetime.utcnow)
    __table_args__ = (
        CheckConstraint('rating >= 0 AND rating <= 5', name='rating_range'), # serverside rating constraint
    )

# defining home route
@app.route('/')
def home():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('base.html', reviews=reviews)

# defining search route
@app.route('/search')
def search():
    return render_template('search.html')

# defining login route
@app.route('/login', methods=['GET'])
def show_form_login():
    return render_template('login.html')

# defining login form
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    # authenticating user
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.user_id
        return redirect(url_for('member_page'))
    else:
        return "Invalid credentials", 401

# defining logout function
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# defining create account route
@app.route('/create_account', methods=['GET'])
def show_form_create_account():
    return render_template('create_account.html')

# defining create account form
@app.route('/create_account', methods=['POST'])
def create_account():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    creation_date = datetime.now().strftime('%Y-%m-%d')
    hashed_password = generate_password_hash(password)

    # adding new user to db
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()
    
    return redirect(url_for('home'))

# defining filter system
@app.route('/filter', methods=['GET'])
def filter():
    cuisine = request.args.get('cuisine')
    review_score = request.args.get('review_score')

    query = Review.query

    # filter criteria
    if cuisine:
        query = query.filter(Review.cuisine_type == cuisine)

    if review_score:
        query = query.filter(Review.rating >= review_score)

    results = query.order_by(Review.created_at.desc()).all()

    return render_template('filter.html', restaurants=results)

# defining review page route
@app.route('/add_review', methods=['GET'])
def show_form_add_review():
    return render_template('add_review.html')

# defining add review form  
@app.route('/add_review', methods=['POST'])
def add_review():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    name = request.form.get('name')
    cuisine = request.form.get('cuisine')
    review_score = request.form.get('review_score')
    review_text = request.form.get('review_text')

    # ensure required fields are present
    if not all([name, review_score]): 
        return "Missing review data", 400

    # convert rating to integer and validate
    try:

        if int(review_score) < 1 or int(review_score) > 5:
            return "Rating must be between 1 and 5", 400
    except ValueError:
        return "Rating must be a number", 400

    # adding new review to db
    new_review = Review(
        user_id=session['user_id'],
        restaurant_name=name,
        cuisine_type=cuisine,
        rating=int(review_score),
        review_text=review_text
    )

    db.session.add(new_review)
    db.session.commit()

    return redirect(url_for('home'))

# defining all reviews route
@app.route('/all_reviews')
def all_reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('all_reviews.html', reviews=reviews)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # Creates tables if they don’t exist
    app.run(debug=True)

# runs app
app.run(debug=True, reloader_type='stat', port=5000)