#-*- coding:utf-8-*-

from datetime import datetime
from flask import render_template,url_for,request,make_response
from flask import redirect,flash,session,g
from weblog import app
from weblog.forms import SearchForm,LoginForm,RegisterForm,newLawForm,CommentForm
from weblog.MongoDB_Models import User,Law,Comment
import os,re,random
from os import path,pardir

@app.before_request
def before_request():
    if  'username' in session:
        g.current_user=User.objects(username=session['username']).first()
    else:
        g.current_user=None  

@app.errorhandler(404)
def page_not_found(error):
    form=SearchForm()
    return render_template('page_not_found.html',form=form),404

@app.route('/')
@app.route('/default')
def default():
    form=SearchForm()
    return render_template('default.html',form=form,year=datetime.now().year)

@app.route('/listlaw/<string:type>')
def listlaw(type):
    recent=sidebar_data()
    form=SearchForm()
    laws=Law.objects(LawType=type).all()
    return render_template('listlaw.html',form=form,type=type,laws=laws,recent=recent)

@app.route('/searchLaw',methods=['GET', 'POST'])
def searchLaw():
    form=SearchForm()
    recent=sidebar_data()
    if form.validate_on_submit():
        searchdata=form.content.data
        if form.searchtype.data=='LawTitle':
            laws=Law.objects(LawTitle__in__contains=searchdata).order_by("-time").all()
        elif form.searchtype.data=='LawFileNo':
            laws=Law.objects(LawFileNo__in__contains=searchdata).order_by("-time").all()
        elif form.searchtype.data=='LawContent':
            laws=Law.objects(LawContent__in__contains=searchdata).order_by("-time").all()
        return render_template('listlaw.html',form=form,type=searchdata,laws=laws,recent=recent)

    return redirect(url_for('listlaw',type=form.content.data))

@app.route('/login',methods=['GET', 'POST'])
def login():
    loginform=LoginForm()
    form=SearchForm()
    if loginform.validate_on_submit():
        user=User.objects(username=loginform.username.data).first()
        if user is not None:
            session['username']=loginform.username.data
            session['password']=loginform.password.data
            session['remember']=loginform.remember.data            
            flash('登录成功.',category="success")
            return redirect(url_for('default'))
    loginform.password.data=""
    loginform.username.data=""
    return render_template(
        'login.html',
        loginform=loginform,
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
            
        return redirect(url_for('default'))

@app.route('/register',methods=['GET', 'POST'])
def register():
    form=SearchForm()
    Registerform=RegisterForm()
    if Registerform.validate_on_submit():        
        new_user=User()

        file=request.files['user_head_image']
        extention=str(file.filename).split('.')[1]
        p=app.static_folder+'/image/userface/'+Registerform.username.data+'.'+extention

        new_user.username=Registerform.username.data
        new_user.password=Registerform.password.data
        new_user.user_head=Registerform.username.data+'.'+extention
        
        print(p)
        file.save(p)
        new_user.save()

        flash('注册成功，请登录.',category="success")
        return redirect(url_for('.login'))
    Registerform.username.data=""
    Registerform.password.data=""
    Registerform.confirm.data=""
    return render_template(
        'register.html',
        Registerform=Registerform,
        form=form
        )


@app.route('/edit/<string:law_id>',methods=['GET', 'POST'])
def edit(law_id):
    if  not g.current_user:
        flash('需要登录才能新增法规',category="danger")
        return redirect(url_for('login'))
    form=newLawForm()
    law=Law.objects(id=law_id).first()
    ss=""
    for s in law.LawTags:
        ss=ss+" "+s
    
    if form.validate_on_submit():
        fromcomment=CommentForm()
        law_tags=form.LawTags.data
        taglist=law_tags.split()
        result=Law.objects(id=law_id).update(
            LawTitle=form.LawTitle.data,
            LawFileNo=form.LawFileNo.data,
            LawType=form.LawType.data,
            LawPublishDate=form.LawPublishDate.data,
            LawContent=form.LawContent.data,
            LawMark=form.LawMark.data,
            LawTags=taglist
            )
        if result==1:
            flash('修改成功')
            print("AAAUPDATE"+str(result))
            return redirect(url_for('detail',law_id=law_id))
        
    return render_template(
        'edit.html',
        form=form,
        law=law,
        tags=ss,
        year=datetime.now().year,
        title='修改法规'
        )



@app.route('/detail/<string:law_id>',methods=['GET', 'POST'])
def detail(law_id):
    form=SearchForm()
    commentform=CommentForm()
    if commentform.validate_on_submit():
        update_law=Law.objects(id=law_id).first()
        new_comment=Comment()
        new_comment.name=commentform.name.data
        new_comment.text=commentform.text.data
        new_comment.date=datetime.now()
        update_law.Lawcomments.append(new_comment)
        update_law.save()
        return redirect(url_for('detail',law_id=law_id))
    commentform.name.data=""
    commentform.text.data=""
    law=Law.objects(id=law_id).first()
    tags=law.LawTags
    comments=law.Lawcomments

    #return (WriteHtml(law,form))
    return render_template(
        'detail.html',
        law=law,
        form=form,
        commentform=commentform,
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
    form=SearchForm()
    newform=newLawForm()
    if newform.validate_on_submit():
        law_tags=newform.LawTags.data
        taglist=law_tags.split()
        newlaw=Law()
        newlaw.LawTitle=newform.LawTitle.data
        newlaw.LawFileNo=newform.LawFileNo.data
        newlaw.LawType=newform.LawType.data
        newlaw.LawPublishDate=newform.LawPublishDate.data
        newlaw.LawMark=newform.LawMark.data
        newlaw.LawContent=newform.LawContent.data
        newlaw.LawTags=taglist
        newlaw.time=datetime.now()
        newlaw.user=g.current_user
        newlaw.save()
        flash('新增成功')
        return redirect(url_for('default'))
    return render_template(
        'new.html',
        newform=newform,
        form=form,
        year=datetime.now().year,
        title='新增法律法规'
        )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    form=SearchForm()
    return render_template(
        'contact.html',
        title='联系我们',
        year=datetime.now().year,
        form=form,
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
def sidebar_data():
    recent=Law.objects.order_by("-publish_date").limit(5).all()
    return recent
#@app.route('/home')
#def home():
#    """Renders the home page."""
#    form=SearchForm()
#    if form.validate_on_submit():
#        keywords=form.content.data
#        #result=search.whoosh_search(Law,query=keyword,fields=['LawContent'],limit=20)
#        #return result
#    laws=Law.objects.order_by("-time").all()
#    return render_template(
#        'index.html',
#        title='主页',
#        laws=laws,
#        year=datetime.now().year,
#        form=form
#    )

#@app.route('/type/<string:law_type>')
#def type(law_type='ALL'):
#    form=SearchForm()
#    if law_type=='ALL':
#        laws=Law.objects.order_by("-time").all()
#    else:
#        laws=Law.objects(LawType=law_type).order_by("-time").all()
#    return render_template(
#        'index.html',
#        title='主页',
#        laws=laws,
#        year=datetime.now().year,
#        form=form)