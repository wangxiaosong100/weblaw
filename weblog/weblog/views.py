#-*- coding:utf-8-*-

from datetime import datetime
from flask import render_template
from weblog import app
from weblog.forms import SearchForm

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    form=SearchForm()
    return render_template(
        'index.html',
        title='主页',
        year=datetime.now().year,
        form=form
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
