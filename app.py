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

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']
app.jinja_env.globals['csrf_token'] = generate_csrf_token

def validate_csrf():
    token = session.get('_csrf_token', None)
    form_token = request.form.get('_csrf_token')
    if not token or not form_token or token != form_token:
        abort(403)


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
    restaurant_name = db.Column(db.String(100), nullable=False, index=True)
    cuisine_type = db.Column(db.String(100), nullable=True, index=True)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Date, default=datetime.utcnow)
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range'), # serverside rating constraint
    )

# defining home route
@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)

    reviews = Review.query.order_by(
        Review.created_at.desc()
    ).paginate(page=page, per_page=8)

    return render_template(
        'base.html',
        reviews=reviews.items,
        pagination=reviews
    )

# defining dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('show_form_login'))

    # Fetch reviews (all, or just user’s, or latest)
    reviews = Review.query.order_by(Review.created_at.desc()).limit(8).all()

    return render_template('dashboard.html', reviews=reviews)

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

    sort = request.args.get('sort', 'new')

    if sort == 'rating':
        results = reviews.order_by(Review.rating.desc()).all()
    else:
        results = reviews.order_by(Review.created_at.desc()).all()

    return render_template('search.html', reviews=results)

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# defining login route
@app.route('/login', methods=['GET'])
def show_form_login():
    return render_template('login.html')

# defining login form
@app.route('/login', methods=['POST'])
def login():
    validate_csrf()
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
    validate_csrf()
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
    validate_csrf()
    if 'user_id' not in session:
        return redirect(url_for('login'))

    name = request.form.get('name', '').strip()
    cuisine = request.form.get('cuisine', '').strip()
    review_score = request.form.get('review_score', '').strip()
    review_text = request.form.get('review_text', '').strip()

    # required fields validation
    if not name or not cuisine or not review_text:
        flash("All fields are required.")
        return redirect(url_for('show_form_add_review'))

    # rating validation
    try:
        rating = int(review_score)
        if rating < 1 or rating > 5:
            flash("Rating must be between 1 and 5.")
            return redirect(url_for('show_form_add_review'))
    except ValueError:
        flash("Rating must be a number.")
        return redirect(url_for('show_form_add_review'))

    new_review = Review(
        user_id=session['user_id'],
        restaurant_name=name,
        cuisine_type=cuisine,
        rating=rating,
        review_text=review_text
    )

    db.session.add(new_review)
    db.session.commit()

    flash("Review added successfully!")
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
    validate_csrf()
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

        if not review.restaurant_name or not review.cuisine_type or not review.review_text:
            flash("All fields are required.")
            return redirect(url_for('edit_review', review_id=review_id))

        if review.rating < 1 or review.rating > 5:
            flash("Rating must be between 1 and 5.")
            return redirect(url_for('edit_review', review_id=review_id))


        db.session.commit()
        return redirect(url_for('my_reviews'))

    return render_template('edit_review.html', review=review)

# defining delete review route
@app.route('/delete_review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    validate_csrf()
    if 'user_id' not in session:
        return redirect(url_for('show_form_login'))

    review = Review.query.get_or_404(review_id)

    if review.user_id != session['user_id']:
        return "Unauthorized", 403

    db.session.delete(review)
    db.session.commit()

    flash("Review deleted successfully")
    return redirect(url_for('my_reviews'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('show_form_login'))

    user = get_current_user()
    return render_template('profile.html', user=user)

@app.route('/profile/change_password', methods=['POST'])
def change_password():
    validate_csrf()
    if 'user_id' not in session:
        return redirect(url_for('show_form_login'))

    user = get_current_user()

    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if not check_password_hash(user.password_hash, current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('profile'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('profile'))

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    flash('Password changed successfully.', 'success')
    return redirect(url_for('profile'))

@app.route('/profile/password')
def change_password_page():
    if 'user_id' not in session:
        return redirect(url_for('show_form_login'))

    return render_template('change_password.html')

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    validate_csrf()
    if 'user_id' not in session:
        return redirect(url_for('show_form_login'))

    user = get_current_user()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()

        if username and username != user.username:
            if User.query.filter_by(username=username).first():
                flash('Username already taken.', 'error')
                return redirect(url_for('edit_profile'))
            user.username = username
            session['username'] = username

        if email and email != user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already in use.', 'error')
                return redirect(url_for('edit_profile'))
            user.email = email

        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user=user)

@app.route('/profile/delete', methods=['POST'])
def delete_account():
    validate_csrf()
    if 'user_id' not in session:
        return redirect(url_for('show_form_login'))

    user = get_current_user()

    # logout first
    session.clear()

    db.session.delete(user)
    db.session.commit()

    flash('Your account has been deleted.', 'success')
    return redirect(url_for('home'))

# runs app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # Creates tables if they don’t exist
    app.run(debug=True)

# runs app
app.run(debug=True, reloader_type='stat', port=5000)