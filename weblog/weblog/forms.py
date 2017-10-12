#-*- coding:utf-8-*-
from flask import flash
from flask_wtf import Form
from weblog.MongoDB_Models import mongo,User,Comment,Law,Department
from weblog.MongoDB_Models import LawType as MYLawType
from wtforms import (
    StringField,
    TextAreaField,
    PasswordField,
    BooleanField,
    SelectField,
    FileField,
    DateField,
    DateTimeField
    )
from wtforms.validators import DataRequired,Length,EqualTo,URL


class SearchForm(Form):
    content=StringField(
        'content',
        [DataRequired()]
        )
    searchtype=SelectField('搜索类型',choices=[
        ('LawTitle','标题'),
        ('LawFileNo','文号'),
        ('LawContent','内容')
        ])
    #def validate(self):
    #    if  self.content.data=="":
    #        self.content.errors.append("请输入要搜索的值后再点‘搜一下’，谢谢！")
    #        return False

class CommentForm(Form):
      name=StringField(
          'Name',
          validators=[DataRequired(),Length(max=255)]
          )
      text=TextAreaField(u'Comment',validators=[DataRequired(),Length(max=1000)])

class LoginForm(Form):
    username=StringField('Username',[
        DataRequired(),Length(max=255)
        ])
    password=PasswordField('Password',[DataRequired()])
    remember=BooleanField("Remember Me")
    
    def validate(self):
        check_validate=super(LoginForm,self).validate()

        if not check_validate:
            return False
        user=User.objects(
            username=self.username.data
            ).first()
        if not user:
            self.username.errors.append(
                '用户名不存在'
                )
            return False

        if not user.check_password(self.password.data):
            self.username.errors.append(
                '密码错误'
                )
            return False
        return True

class RegisterForm(Form):
    username=StringField('Username',[
        DataRequired(),
        Length(max=255)
        ])
    city=SelectField('州市',choices=[
        (dep.departmentCode,dep.departmentname)
        for dep in Department.objects(parentCode='YN530000').all()
        ])
    
    county=SelectField('县区',choices=[])
    county1=SelectField('县区',choices=[])
    #,choices=[
    #    (dep.departmentCode,dep.departmentname)
    #    for dep in Department.objects(parentCode__ne='').all()
    #    ]
    password=PasswordField('Password',[
        DataRequired(),
        Length(min=8)
        ])
    confirm=PasswordField('Confirm Password',[
        DataRequired(),
        EqualTo('password')
        ])
    user_head_image=FileField('请选择头像文件')
    
    
    #recaptcha=RecaptchaField()
    def validate(self):
        #check_validate=super(RegisterForm,self).validate()

        #if not check_validate:
        #    return False
        user=User.objects(
            username=self.username.data
            ).first()
        if user:
            self.username.errors.append(
                '用户名:'+self.username.data+' 已经存在请重新输入用户名'
                )
            return False
        #if not '.' not in self.user_head_image.:
        #    self.user_head_image.errors.append('文件名非法')
        #    return False
        return True



class newLawForm(Form):
    LawTitle=StringField('法规标题',[
        DataRequired()
        ])
    LawDepartment=StringField('发布部门')
    LawFileNo=StringField('法规文号',[
        DataRequired(),
        Length(max=255)
        ])
    LawType=SelectField('法规分类',choices=[
        (str(type.id),type.LawTypName)
        for type in MYLawType.objects(parentId='').all()
        ])
    LawTypeDetail=SelectField('分类明细',choices=[])
    LawTypeDetail1=SelectField('分类明细',choices=[])
    LawPublishDate=DateField('发布日期',[DataRequired()])
    LawMark=StringField('备注')
    LawContent=TextAreaField('法规正文',[DataRequired()])
    LawTags=StringField('标签')

    def validate(self):
        return True

#class PostForm(Form):
#    title=StringField('Title',[
#        DataRequired(),
#        Length(max=255)
#        ])
#    type=SelectField('Post Type',choices=[
#        ('Blog','文字'),
#        ('VideoBlog','视频'),
#        ('ImageBlog','图片'),
#        ('QuoteBlog','Quto')
#        ])

#    text=TextAreaField('内容')
#    image=StringField('图片URL',[Length(max=500)])
#    video=StringField('视频URL',[Length(max=500)])
#    author=StringField('作者',[Length(max=500)])
#    tag=StringField('Tags')

#class OpenIDForm(Form):
#    openid=StringField('OpenID URL',[DataRequired()],URL)