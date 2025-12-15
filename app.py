# importing required add-ons
from flask import Flask, request, render_template, redirect, url_for, send_from_directory # pyright: ignore[reportMissingImports]
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime

# creating engine for site
app = Flask(__name__)
app.secret_key = 'key'

app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///tastetracker_td.db'
app.config["SQLALCHEMY_TRACK_MODIFICATION"]=False

db= SQLAlchemy(app) 

#creating db schema
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date, default=datetime.utcnow)

class Review(db.Model):
    review_id = db.relationship("Review", backref='author', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    restaurant_name = db.Column(db.String(100), nullable=False)
    cuisine_type = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Text, nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Date, default=datetime.utcnow)

@app.route('/')
def home():
    query = text('SELECT * FROM restaurants ORDER BY review_score DESC;')
    result = connection.execute(query).fetchall()

    return render_template('base.html', restaurants=result)

@app.route('/')
def search():
    return render_template('search.html')

#@app.authenticate('/user_page')
#def authenticate():
    

@app.route('/create_account')
def create_account():
    username = request.form['username']
    password = request.form['password']
    creation_date = datetime.now().strftime('%Y-%m-%d')

@app.route('/filter', methods=['GET'])
def filter():
    cuisine = request.args.get('cuisine', '')
    review_score = request.args.get('review_score', '')

    conditions = []
    if cuisine:
        conditions.append("cuisine='{}'".format(cuisine))
    if review_score:
        conditions.append('review_score>={}'.format(review_score))

    condition_str = ' AND '.join(conditions)

    query = text('SELECT * FROM restaurants WHERE {}'.format(condition_str))
    result = connection.execute(query).fetchall()

    return render_template('filter.html', Resturants=result)

# add review page access
@app.route('/add_review', methods=['GET'])
def show_form():
    return render_template('add_review.html')

# Review adding system
    
@app.route('/add_review', methods=['POST'])
def add_review():
    # Requesting form data
    name = request.form['name']
    cuisine = request.form['cuisine']
    location = request.form['location']
    review_score = request.form['review_score']
    review_text = request.form['review_text']
    review_date = datetime.now().strftime('%Y-%m-%d')

    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            image_path = 'uploads/{}'.format(image.filename)
            image.save(image_path)
        else:
            image_path = None
    else:
        image_path = None

    insert_statement = '''
        INSERT INTO restaurants (name, cuisine, location, review_date, review_score, review_text, image)
        VALUES ('{}', '{}', '{}', '{}', {}, '{}', '{}')
    '''.format(name, cuisine, location, review_date, review_score, review_text, image.filename)

    connection.execute(text(insert_statement))
    connection.commit()
    
    return redirect(url_for('home'))

app.run(debug=True, reloader_type='stat', port=5000)