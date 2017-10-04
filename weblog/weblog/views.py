#-*- coding:utf-8-*-

from datetime import datetime
from flask import render_template,url_for
from flask import redirect,flash,session,g
from weblog import app
from weblog.forms import SearchForm,LoginForm,RegisterForm
from weblog.MongoDB_Models import User,Post

@app.before_request
def before_request():
    if  'username' in session:
        g.current_user=User.objects(username=session['username']).first()
    else:
        g.current_user=None  

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
@app.route('/login',methods=['GET', 'POST'])
def login():
    form=LoginForm()
    #openid_form=OpenIDForm()
    #if openid_form.validate_on_submit():
    #    return oid.try_login(
    #        openid_form.openid.data,
    #        ask_for=['nickname','email'],
    #        ask_for_optional=['fullname']
    #        )
    if form.validate_on_submit():
        #user=User.query.filter_by(
        #    username=form.username.data
        #    ).first()
        user=User.objects(username=form.username.data).first()
        if user is not None:
            session['username']=form.username.data
            session['password']=form.password.data
            session['remember']=form.remember.data            
            flash('登录成功.',category="success")
            return redirect(url_for('home'))
    #openid_errors=oid.fetch_error()
    #if openid_errors:
    #    flash(openid_errors,category="danger")

    #if 'username' in session:
    #    form.username.data=session['username']
    #    form.password.data=session['password']
    form.password.data=""
    form.username.data=""
    return render_template(
        'login.html',
        form=form,
        year=datetime.now().year,
        title='用户登录'
        #,openid_form=openid_form
        )
@app.route('/logout',methods=['GET', 'POST'])
def logout():
        flash("你已退出登录","success")
        g.current_user=None
        if session['remember']==True:
            pass
        else:
            session.pop('username',None)
            session.pop('passowrd',None)
            #session['remember']=False
            
        return redirect(url_for('home'))
@app.route('/register',methods=['GET', 'POST'])
def register():
    form=RegisterForm()
    #openid_form=OpenIDForm()

    #if openid_form.validate_on_submit():
    #    return oid.try_login(
    #        openid_form.openid.data,
    #        ask_for=['nickname','email'],
    #        ask_for_optional=['fullname']
    #        )

    if form.validate_on_submit():
        #new_user=User(username=form.username.data)
        #new_user.set_password(form.password.data)
        #db.session.add(new_user)
        #db.session.commit()
        new_user=User()
        new_user.username=form.username.data
        new_user.password=form.password.data
        #new_user.password=new_user.getBcrypt_password(form.password.data)
        new_user.save()
        flash('注册成功，请登录.',category="success")
        return redirect(url_for('.login'))

    #openid_errors=oid.fetch_error()
    #if openid_errors:
    #    flash(openid_errors,category="danger")
    form.username.data=""
    form.password.data=""
    form.confirm.data=""
    return render_template(
        'register.html',
        form=form
        )

@app.route('/new')
def new():
    return render_template('new.html')

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
