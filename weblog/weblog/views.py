#-*- coding:utf-8-*-

from datetime import datetime
from flask import render_template,url_for,request,make_response
from flask import redirect,flash,session,g
from weblog import app
from weblog.forms import SearchForm,LoginForm,RegisterForm,newLawForm,CommentForm
from weblog.MongoDB_Models import User,Post,Law,Comment
import os,re,random
from os import path
from html.parser import HTMLParser


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
    laws=Law.objects().all()
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
        new_user.username=form.username.data
        new_user.password=form.password.data
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
    form.name.data=""
    form.text.data=""
    law=Law.objects(id=law_id).first()
    tags=law.LawTags
    comments=law.Lawcomments

    #return (WriteHtml(law))
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
    form=newLawForm()
    if form.validate_on_submit():
        law_tags=form.LawTags.data
        taglist=law_tags.split()
        newlaw=Law()
        newlaw.LawTitle=form.LawTitle.data
        newlaw.LawFileNo=form.LawFileNo.data
        newlaw.LawType=form.LawType.data
        newlaw.LawPublishDate=form.LawPublishDate.data
        newlaw.LawAbolishDate=form.LawAbolishDate.data
        newlaw.LawContent=form.LawContent.data
        newlaw.LawTags=taglist
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

#def filter_tag(htmlstr):  
#    re_cdata = re.compile('<!DOCTYPE HTML PUBLIC[^>]*>', re.I)  
#    re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I) #过滤脚本  
#    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I) #过滤style  
#    re_br = re.compile('<br\s*?/?>')  
#    re_h = re.compile('</?\w+[^>]*>')  
#    re_comment = re.compile('<!--[\s\S]*-->')  
#    s = re_cdata.sub('', htmlstr)  
#    s = re_script.sub('', s)  
#    s=re_style.sub('',s)  
#    s=re_br.sub('\n',s)  
#    s=re_h.sub(' ',s)  
#    s=re_comment.sub('',s)  
#    blank_line=re.compile('\n+')  
#    s=blank_line.sub('\n',s)  
#    s=re.sub('\s+',' ',s)  
#    #s=replaceCharEntity(s)  
#    return s  

def WriteHtml(law:Law):
    message="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>%s - 审计法规库</title>
    <link rel="stylesheet" type="text/css" href="/static/content/bootstrap.min.css" />
    <link rel="stylesheet" type="text/css" href="/static/content/bootstrap-datetimepicker.css" />
    <link rel="stylesheet" type="text/css" href="/static/content/site.css" />
   
    <script src="../static/ckeditor/ckeditor.js"></script>
    <script charset="utf-8" src="/static/kindeditor/plugins/code/prettify.js"></script>
    <script src="/static/scripts/modernizr-2.6.2.js"></script>
</head>
<body>
<div class="navbar navbar-inverse navbar-fixed-top">
        <div class="container">
            <div class="navbar-header">
                <label class="btn-toolbar"><img src="../static/image/logo.jpg" width="50" height="50" class="img-circle"/></label>
                <label class="btn-toolbar">&nbsp;</label>
            </div>
            <div class="navbar-header">
                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a href="/" class="navbar-brand">审计法规库</a>
            </div>
            <div class="navbar-collapse collapse">
                <ul class="nav navbar-nav">
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
                            综合 <b class="caret"></b>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="#">宪政</a></li>
                            <li><a href="#">行政</a></li>
                            <li><a href="#">行事</a></li>
                            <li><a href="#">民事</a></li>
                        </ul>
                    </li>
                        
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
                            审计 <b class="caret"></b>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="#">国家审计</a></li>
                            <li><a href="#">内部审计</a></li>
                            <li><a href="#">注册会计师</a></li>
                            <li><a href="#">其他</a></li>
                        </ul>
                    </li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
                            财政财务 <b class="caret"></b>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="#">综合</a></li>
                            <li><a href="#">行政</a></li>
                            <li><a href="#">事业</a></li>
                            <li><a href="#">海关</a></li>
                            <li><a href="#">农业</a></li>
                            <li><a href="#">社保</a></li>
                            <li><a href="#">外资</a></li>
                            <li><a href="#">基建</a></li>
                            <li><a href="#">其也</a></li>
                        </ul>
                    </li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
                            税收 <b class="caret"></b>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="#">综合</a></li>
                            <li><a href="#">征管</a></li>
                            <li><a href="#">流转税</a></li>
                            <li><a href="#">所得税</a></li>
                            <li><a href="#">其他税费</a></li>
                            <li><a href="#">其他</a></li>
                        </ul>
                    </li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
                            金融 <b class="caret"></b>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="#">综合</a></li>
                            <li><a href="#">商业银行</a></li>
                            <li><a href="#">政策性银行</a></li>
                            <li><a href="#">证券期货</a></li>
                            <li><a href="#">保险</a></li>                          
                            <li><a href="#">其也</a></li>
                        </ul>
                    </li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
                            企业 <b class="caret"></b>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="#">综合</a></li>
                            <li><a href="#">工业</a></li>
                            <li><a href="#">贸易</a></li>
                            <li><a href="#">交通运输</a></li>
                            <li><a href="#">建设</a></li>
                            <li><a href="#">信息邮政</a></li>
                            <li><a href="#">军工</a></li>
                            <li><a href="#">三资</a></li>
                            <li><a href="#">其也</a></li>
                        </ul>
                    </li>
                    <li><a href="{{ url_for('contact') }}">党内规章制度</a></li>
                </ul>
            </div>
                   
    </div>
</div>
<div class="container">
    <div class="row">
        <div class="col-lg-12">
            <div class="list-group">
                <div class="list-group-item">
                    <div class="list-group-item-heading" style="align-content:center">
                        <h3><p style="text-align:center"> %s </p></h3>
                        <p style="text-align:center">
                            文号：%s &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                            分类：%s
                        </p>
                    </div>
                    <div class="list-group-item-text">   
                        <pre>
                            %s
                        </pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
    </body></html>"""%('法规浏览',law.LawTitle,law.LawFileNo,law.LawType,law.LawContent)
    return message