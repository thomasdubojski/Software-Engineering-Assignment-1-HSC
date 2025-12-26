
# Flask App Setup (Core Structure)

This is the foundation of everything.

I will:

- Create app.py
- Set up the first route: / (Home)

# Jinja Templates (Modular Layout)

This is the modular code requirement.

I will create:

- base.html → shared layout (navbar, footer)

Using:

{% extends "base.html" %}  
{% block content %}  
{% endblock %}

# 3. Forms (HTML + Flask Handling)

This satisfies the Forms requirement.

I will build:

- Registration form with input for username, email and password
- Review form with input for restaurant name, rating and review text
- Login form with input for username and password

# 4. JavaScript (Dynamic Features)

This satisfies the JavaScript requirement.

I will use JS for nav menu

# 5. PWA Features

This is what upgrades the site into a Progressive Web App.

I will create PWA service worker for offline functions

# 6. Modular Code

This means create a separate:

- templates/
- static/css/
- static/js/
- app.py

No HTML embedded directly inside Python
