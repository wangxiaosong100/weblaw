#-*- coding:utf-8-*-

from datetime import datetime
from flask import render_template,url_for,request,make_response
from flask import redirect,flash,session,g
from weblog import app
from weblog.forms import SearchForm,LoginForm,RegisterForm,newLawForm,CommentForm
from weblog.MongoDB_Models import User,Post,Law,Comment
import os,re,random
from os import path,pardir

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
    laws=Law.objects.order_by("-time").all()
    return render_template(
        'index.html',
        title='主页',
        laws=laws,
        year=datetime.now().year,
        form=form
    )
@app.route('/login',methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.objects(username=form.username.data).first()
        if user is not None:
            session['username']=form.username.data
            session['password']=form.password.data
            session['remember']=form.remember.data            
            flash('登录成功.',category="success")
            return redirect(url_for('home'))
    form.password.data=""
    form.username.data=""
    return render_template(
        'login.html',
        form=form,
        year=datetime.now().year,
        title='用户登录'
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
            
        return redirect(url_for('home'))
@app.route('/register',methods=['GET', 'POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():        
        new_user=User()

        file=request.files['user_head_image']
        extention=str(file.filename).split('.')[1]
        p=app.static_folder+'/image/userface/'+form.username.data+'.'+extention

        new_user.username=form.username.data
        new_user.password=form.password.data
        new_user.user_head=form.username.data+'.'+extention
        
        print(p)
        file.save(p)
        new_user.save()

        flash('注册成功，请登录.',category="success")
        return redirect(url_for('.login'))
    form.username.data=""
    form.password.data=""
    form.confirm.data=""
    return render_template(
        'register.html',
        form=form
        )
@app.route('/detail/<string:law_id>',methods=['GET', 'POST'])
def detail(law_id):
    form=CommentForm()
    if form.validate_on_submit():
        update_law=Law.objects(id=law_id).first()
        new_comment=Comment()
        new_comment.name=form.name.data
        new_comment.text=form.text.data
        new_comment.date=datetime.now()
        update_law.Lawcomments.append(new_comment)
        update_law.save()
        return redirect(url_for('detail',law_id=law_id))
    form.name.data=""
    form.text.data=""
    law=Law.objects(id=law_id).first()
    tags=law.LawTags
    comments=law.Lawcomments

    #return (WriteHtml(law,form))
    return render_template(
        'detail.html',
        law=law,
        form=form,
        comments=comments,
        tags=tags,
        title='法规详细信息',
        year=datetime.now().year
        )

@app.route('/new',methods=['GET', 'POST'])
def new():
    if  not g.current_user:
        flash('需要登录才能新增法规',category="danger")
        return redirect(url_for('login'))
    form=newLawForm()
    if form.validate_on_submit():
        law_tags=form.LawTags.data
        taglist=law_tags.split()
        newlaw=Law()
        newlaw.LawTitle=form.LawTitle.data
        newlaw.LawFileNo=form.LawFileNo.data
        newlaw.LawType=form.LawType.data
        newlaw.LawPublishDate=form.LawPublishDate.data
        newlaw.LawMark=form.LawMark.data
        newlaw.LawContent=form.LawContent.data
        newlaw.LawTags=taglist
        newlaw.time=datetime.now()
        newlaw.user=g.current_user
        newlaw.save()
        flash('新增成功')
        return redirect(url_for('home'))
    return render_template(
        'new.html',
        form=form,
        year=datetime.now().year,
        title='新增法律法规'
        )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='联系我们',
        year=datetime.now().year,
        message='您可以通过以下方式联系到我们.'
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
def gen_rnd_filename():
  filename_prefix = datetime.now().strftime('%Y%m%d%H%M%S')
  return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))
 
@app.route('/ckupload/', methods=['POST'])
def ckupload():
      """CKEditor file upload"""
      print("CKEDITOR HERE")
      error = ''
      url = ''
      callback = request.args.get("CKEditorFuncNum")
      if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(app.static_folder, 'upload', rnd_name)
        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
          try:
            os.makedirs(dirname)
          except:
            error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
          error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
          fileobj.save(filepath)
          url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
      else:
        error = 'post error'
      res = """
 
    <script type="text/javascript">
     window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
    </script>
 
    """ % (callback, url, error)
      response = make_response(res)
      response.headers["Content-Type"] = "text/html"
      return response
