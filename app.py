# importing required add-ons
from flask import Flask, request, render_template, redirect, url_for, send_from_directory # pyright: ignore[reportMissingImports]
from flask_sqlalchemy import SQLAlchemy # pyright: ignore[reportMissingImports]
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash # pyright: ignore[reportMissingImports]
from flask import session # pyright: ignore[reportMissingImports]
from sqlalchemy import CheckConstraint # pyright: ignore[reportMissingImports]
from flask import flash # pyright: ignore[reportMissingImports]

# creating engine for site
app = Flask(__name__)
app.secret_key = 'key'

app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///tastetracker_td.db'
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db= SQLAlchemy(app) 

# creating db schema
# users table
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date, default=datetime.utcnow)

    reviews = db.relationship("Review", backref='author', lazy=True)

# reviews table
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
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    cuisine = request.args.get('cuisine', '')
    min_rating = request.args.get('review_score', '')

    reviews = Review.query

    if query:
        reviews = reviews.filter(
            (Review.restaurant_name.ilike(f"%{query}%")) |
            (Review.review_text.ilike(f"%{query}%"))
        )

    if cuisine:
        reviews = reviews.filter(Review.cuisine_type == cuisine)

    if min_rating.isdigit():
        reviews = reviews.filter(Review.rating >= int(min_rating))

    results = reviews.order_by(Review.created_at.desc()).all()

    return render_template('search.html', reviews=results)


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
        session['username'] = user.username

        return redirect(url_for('home'))
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

    # convert rating to integer and validating it
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

# this code throughout strings prevents unauthed access to certain feautures/pages
# 
# Not logged in at all 
# if 'user_id' not in session:
#        return redirect(url_for('show_form_login'))
#
# Incorrect account logged in
#    if review.user_id != session['user_id']:
#        return "Unauthorized", 403

@app.route('/my_reviews')
def my_reviews():
    if 'user_id' not in session:
        return redirect(url_for('show_form_login'))

    reviews = Review.query.filter_by(user_id=session['user_id']).all()
    return render_template('my_reviews.html', reviews=reviews)

# defining edit review route
@app.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    if 'user_id' not in session:
        return redirect(url_for('show_form_login'))

    review = Review.query.get_or_404(review_id)

    if review.user_id != session['user_id']:
        return "Unauthorized", 403

    if request.method == 'POST':
        review.restaurant_name = request.form['name']
        review.cuisine_type = request.form['cuisine']
        review.rating = int(request.form['review_score'])
        review.review_text = request.form['review_text']

        db.session.commit()
        return redirect(url_for('my_reviews'))

    return render_template('edit_review.html', review=review)

# defining delete review route
@app.route('/delete_review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    if 'user_id' not in session:
        return redirect(url_for('show_form_login'))

    review = Review.query.get_or_404(review_id)

    if review.user_id != session['user_id']:
        return "Unauthorized", 403

    db.session.delete(review)
    db.session.commit()

    flash("Review deleted successfully")
    return redirect(url_for('my_reviews'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # Creates tables if they don’t exist
    app.run(debug=True)

# runs app
app.run(debug=True, reloader_type='stat', port=5000)