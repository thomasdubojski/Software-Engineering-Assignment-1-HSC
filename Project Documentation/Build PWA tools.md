
## **1. Flask App Setup (Core Structure)**

_Foundation of the application._

I will:

- Create `app.py` as the main Flask application file.
- Set up the first route / (Home) to display latest reviews or a landing page.
- Organize routes for registration, login, review CRUD, and filtering/searching.
- Initialize Flask, SQLAlchemy, and Flask-Login for authentication.

## **2. Jinja Templates (Modular Layout)**

_Demonstrates modular coding using templates._

I will create:

- `base.html` with shared layout with navbar, footer, and linked CSS/JS.
- All other templates will extend `base.html`
- Templates include: `search.html`, `login.html`, `create_account.html`, `aa_review.html`, `filter.html`.

## **3. Forms (HTML + Flask Handling)**

_Satisfies the requirement for data input._

I will build:

- Registration form: username, email, password 
- Login form: username/email + password 
- Review form: restaurant name, cuisine type, rating, review text 
- Client-side validation using JavaScript and server-side validation in Flask.

## **4. JavaScript (Dynamic Features)**

_Satisfies dynamic front-end interactivity requirement._

I will implement:

- Navigation menu toggle for mobile responsiveness.
- Autocomplete suggestions for restaurant names in filter/search.
- Optional: live filtering and sorting of reviews without page reload.

## **5. PWA Features**

_Upgrades the site into a Progressive Web App._

I will:

- Create `service-worker.js` to cache static assets and pages for offline use.
- Add `manifest.json` with app name, icons, and start URL.
- Register the service worker in `base.html` to enable offline functionality.

## **6. Modular Code Structure**

_Demonstrates separation of concerns and clean project architecture._

I will maintain:

- Folder structure:
	templates/ → all HTML templates 
	static/css/ → CSS files 
	static/js/ → JavaScript files 
	app.py → main application logic 
	service-worker.js → PWA offline support 
	models.py → database models`
- Ensure no HTML is embedded directly in Python. All logic handled in `app.py` and rendered via templates.