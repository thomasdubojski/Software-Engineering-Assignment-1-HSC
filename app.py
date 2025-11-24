from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from sqlalchemy import create_engine, text
from datetime import datetime

app = Flask(__name__)

engine = create_engine('sqlite:///restaurants.db')
connection = engine.connect()

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory('uploads/', name)

@app.route('/')
def home():
    query = text('SELECT * FROM restaurants ORDER BY review_score DESC;')
    result = connection.execute(query).fetchall()

    return render_template('index.html', restaurants=result)

@app.route('/add_review', methods=['GET'])
def show_form():
    return render_template('add_review.html')

@app.route('/add_review', methods=['POST'])
def add_review():
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