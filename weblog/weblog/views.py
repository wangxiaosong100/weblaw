﻿#-*- coding:utf-8-*-

from datetime import datetime
from flask import render_template,url_for,request,make_response,render_template_string
from flask import redirect,flash,session,g
from weblog import app
#from weblog.getchoices import registerform
from weblog.forms import SearchForm,LoginForm,newLawForm,CommentForm,RegisterForm,LawtypeForm

from weblog.MongoDB_Models import User,Law,Comment,Department,LawType,available_roles
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
    types=LawType.objects(parentId='').order_by("+order").all()
    return render_template('default.html',
                           form=form,
                           year=datetime.now().year,
                           title='主页',
                           types=types)

@app.route('/admin')
def admin():
    form=SearchForm()
    if not g.current_user:
        flash('请登录','danger')
        return redirect(url_for('.login'))
    if is_admin(g.current_user.username):        
        laws=Law.objects(check='0').order_by("-time").all()
        alllaws=Law.objects(check='1').order_by("-time").all()
        return render_template('admin.html',
                               form=form,
                               laws=laws,
                               alllaws=alllaws,
                               title='管理页面',
                               year=datetime.now().year)
    else:
        return render_template('adminError.html',
                               form=form,
                               title='出错',
                               year=datetime.now().year)




@app.route('/listlaw/<int:page>,<string:type>',methods=['GET', 'POST'])
def listlaw(page,type):
    recent=sidebar_data()
    form=SearchForm()
    lawtype=LawType.objects(LawTypName=type).first()
    lawtypedetail=LawType.objects(parentId=str(lawtype.id)).all()
    lawtypedetailsub=LawType.objects(parentId__in=(str(detail.id) for detail in lawtypedetail))
    laws=Law.objects(LawType__in=lawtypedetail,check='1').paginate(page,5)
    return render_template('listlaw.html',
                           form=form,#搜索
                           lawtype=lawtype,#父类
                           laws=laws,
                           recent=recent,#侧边栏数据
                           lawtypedetail=lawtypedetail,#子类
                           title='法规列表',
                           lawtypedetailsub=lawtypedetailsub,
                           year=datetime.now().year
                           )#孙子类
##这个页界显示在listLaw页面的iframe框架中
@app.route('/listlawFrame/<int:page>,<string:type>',methods=['GET', 'POST'])
def listlawFrame(page,type):
    recent=sidebar_data()
    lawtypedetail=LawType.objects(LawTypName=type).first()
    laws=Law.objects(LawType=lawtypedetail,check='1').paginate(page,15)
    return render_template('listlawFrame.html',
                           laws=laws,type=type)

@app.route('/searchLaw/<int:page>',methods=['GET', 'POST'])
def searchLaw(page=1):
    form=SearchForm()
    if form.content.data!="":
        recent=sidebar_data()
        searchdata=form.content.data
        searchtype=''
        print(form.searchtype.data)
        if form.searchtype.data=='LawTitle':
            laws=Law.objects(LawTitle__contains=searchdata,check='1').order_by("-time").paginate(page,5)
            searchtype='标题'
            return render_template('search.html',
                                   form=form,
                                   type=searchdata,
                                   laws=laws,
                                   recent=recent,
                                   searchtype=searchtype,
                                   titile='查询',
                                   year=datetime.now().year
                                   )
        elif form.searchtype.data=='LawFileNo':
            laws=Law.objects(LawFileNo__contains=searchdata,check='1').order_by("-time").paginate(page,5)
            searchtype='文号'
            return render_template('search.html',
                                   form=form,
                                   type=searchdata,
                                   laws=laws,
                                   recent=recent,
                                   searchtype=searchtype,
                                   titile='查询',
                                   year=datetime.now().year)
        elif form.searchtype.data=='LawContent':
            laws=Law.objects(LawContent__contains=searchdata,check='1').order_by("-time").paginate(page,5)
            searchtype='内容'
            return render_template('search.html',
                                   form=form,
                                   type=searchdata,
                                   laws=laws,
                                   recent=recent,
                                   searchtype=searchtype,
                                   titile='查询',
                                   year=datetime.now().year)
    else:
        flash('非法搜索,请输入要搜索的内容','danger')
        return redirect(url_for('default'))

#分页
@app.route('/paginate/<int:page>,<string:searchtype>,<string:keywords>')
def paginate(page,searchtype,keywords):
    form=SearchForm()
    recent=sidebar_data()
    if searchtype=='标题':
        laws=Law.objects(LawTitle__contains=keywords,check='1').order_by("-time").paginate(page,5)
            
        return render_template('search.html',form=form,type=keywords,laws=laws,recent=recent,searchtype=searchtype)
    elif searchtype=='文号':
        laws=Law.objects(LawFileNo__contains=keywords,check='1').order_by("-time").paginate(page,5)
            
        return render_template('search.html',form=form,type=keywords,laws=laws,recent=recent,searchtype=searchtype)
    elif searchtype=='内容':
        laws=Law.objects(LawContent__contains=keywords,check='1').order_by("-time").paginate(page,5)
            
        return render_template('search.html',form=form,type=keywords,laws=laws,recent=recent,searchtype=searchtype)
    else:
        laws=Law.objects(LawType=searchtype,check='1').order_by("-time").paginate(page,5)
        return render_template('listlaw.html',form=form,type=searchtype,laws=laws,recent=recent)



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
    registerform=RegisterForm()  
    if registerform.validate_on_submit():        
        new_user=User()
        department=Department.objects(departmentCode=registerform.county.data).first()
        file=request.files['user_head_image']
        print(str(file.filename));
        if file.filename=='':
            new_user.user_head=''
        else:
            extention=str(file.filename).split('.')[1]
            p=app.static_folder+'/image/userface/'+registerform.username.data+'.'+extention
            new_user.user_head=registerform.username.data+'.'+extention
            file.save(p)
        new_user.username=registerform.username.data
        new_user.password=registerform.password.data
        new_user.department=department        
        new_user.roles=[available_roles[2]]       
        new_user.save()
        flash('注册成功，请登录.',category="success")
        return redirect(url_for('.login'))
    registerform.username.data=""
    registerform.password.data=""
    registerform.confirm.data=""
    registerform.county.data=""   
    return render_template(
        'register.html',
        Registerform=registerform,
        form=form,
        title='用户注册',       
        year=datetime.now().year
        )
#set_county,set_lawdetail分别用来设置注册界面中区县下拉框和法规分类明细下拉框的选项目
#set_county函数的参数citycode作为区县的parentCode的值
#set_lawdetail的parentId与citycode参数类似
@app.route('/set_county/<string:citycode>')
def set_county(citycode):
    registerform=RegisterForm() 
    registerform.county1.choices=[(dep.departmentCode,dep.departmentname)
        for dep in Department.objects(parentCode=citycode).all()]
    return render_template_string("{{registerform.county1(class_='form-control')}}",registerform=registerform)


@app.route('/set_lawdetail/<string:parentId>')
def set_lawdetail(parentId):
    form=newLawForm()
    form.LawTypeDetail1.choices=[
        (str(type.id),type.LawTypName)
        for type in LawType.objects(parentId=parentId).all()
        ]
    return render_template_string("{{form.LawTypeDetail1(class_='form-control')}}",form=form)

@app.route('/edit/<string:law_id>',methods=['GET', 'POST'])
def edit(law_id):
    if  not g.current_user:
        flash('需要登录才能修改法规',category="danger")
        return redirect(url_for('login'))
    form=SearchForm()
    fromedit=newLawForm()
    law=Law.objects(id=law_id).first()
    ss=""
    for s in law.LawTags:        
        ss=ss+" "+s
    
    if fromedit.validate_on_submit():
        fromcomment=CommentForm()
        law_tags=fromedit.LawTags.data
        taglist=law_tags.split()
        lawtyp=LawType.objects(LawTypName=fromedit.LawTypeDetail.data).first()
        result=Law.objects(id=law_id).update(
            LawTitle=fromedit.LawTitle.data,
            LawFileNo=fromedit.LawFileNo.data,
            LawPublishDepart=fromedit.LawDepartment.data,
            LawType=lawtyp,
            LawPublishDate=fromedit.LawPublishDate.data,
            LawContent=fromedit.LawContent.data,
            LawMark=fromedit.LawMark.data,
            LawTags=taglist
            )
        if result==1:
            flash('修改成功')
            return redirect(url_for('admin'))
        
    return render_template(
        'edit.html',
        form=form,
        fromedit=fromedit,
        law=law,
        tags=ss,
        year=datetime.now().year,
        title='修改法规'
        )

@app.route('/delete/<string:law_id>')
def delete(law_id):
    law=Law.objects(id=law_id).first()
    law.delete()
    flash('成功删除','message')
    return redirect(url_for('admin'))

@app.route('/detail/<string:law_id>,<string:check>',methods=['GET', 'POST'])
def detail(law_id,check):
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
    law=Law.objects(id=law_id,check=check).first()
    parentType=LawType.objects(id=law.LawType.parentId).first()
    tags=law.LawTags
    comments=law.Lawcomments

    #return (WriteHtml(law,form))
    return render_template(
        'detail.html',
        law=law,
        parentType=parentType,
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
        lawtype=LawType.objects(id=newform.LawTypeDetail.data).first()
        law_tags=newform.LawTags.data
        taglist=law_tags.split()
        newlaw=Law()
        newlaw.LawTitle=newform.LawTitle.data
        newlaw.LawFileNo=newform.LawFileNo.data
        newlaw.LawPublishDepart=newform.LawDepartment.data
        newlaw.LawType=lawtype
        newlaw.LawPublishDate=newform.LawPublishDate.data
        newlaw.LawMark=newform.LawMark.data
        newlaw.LawContent=newform.LawContent.data
        newlaw.LawTags=taglist
        newlaw.time=datetime.now()
        newlaw.user=g.current_user
        newlaw.check="0"
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
    recent=Law.objects(check='1').order_by("-time").limit(10).all()
    return recent

def is_admin(username):
    u=User.objects(username=username).first()
    if u.roles[0]=='admin':
        return True
    else:
        return False
@app.route('/checkLaw/<string:law_id>,<string:check>')
def checkLaw(law_id,check):
    law=Law.objects(id=law_id).first()
    law.check=check
    law.save()
    flash('操作成功','message')
    return redirect(url_for('admin'))

@app.route('/lawtype',methods=['GET', 'POST'])
def lawtype():
    form=SearchForm()
    lawtypeform=LawtypeForm()
    ptypes=LawType.objects(parentId='').all()
    types=LawType.objects(parentId__ne='').all()
    if lawtypeform.validate_on_submit():
        if lawtypeform.addType.data=='一级分类':
            type=LawType()
            #添加显示图片  
            file=request.files['typeimage']          
            if file.filename!="":                
                extention=str(file.filename).split('.')[1]#取扩展名
                p=app.static_folder+'/image/icon/'+lawtypeform.typename.data+'.'+extention#保存路径
                file.save(p)#保存图片
                type.typeimage=lawtypeform.typename.data+'.'+extention#保存到数据库里面的文件名
            else:
                type.typeimage=''            
            type.LawTypName=lawtypeform.typename.data
            type.parentId=""
            type.save()
            flash('添加成功','message')
        elif lawtypeform.addType.data=='二级分类':
            type=LawType()
            type.LawTypName=lawtypeform.typename.data
            type.parentId=lawtypeform.parentName.data
            type.save()
            flash('添加成功','message')
        elif lawtypeform.addType.data=='三级分类':
            type=LawType()
            type.LawTypName=lawtypeform.typename.data
            type.parentId=lawtypeform.detailTypeName.data
            type.save()
            flash('添加成功','message')
        return redirect(url_for('lawtype'))
    return render_template('lawtype.html',form=form,lawtypeform=lawtypeform,ptypes=ptypes,types=types)

@app.route('/dowloadlaw/<string:law_id>')
def dowloadlaw(law_id):
    law=Law.objects(id=str(law_id)).first()    
    return render_template('dowloadlaw.html',law=law)
