#-*- coding:utf-8-*-
from flask import flash
from flask_wtf import Form
#from AppFiles.models import User,Post,Comment,tags,Tag
from weblog.MongoDB_Models import mongo,Post,User,Comment,BlogPost,VideoPost,ImagePost,QuotePost
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
        validators=[Length(max=255)]
        )

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
        check_validate=super(RegisterForm,self).validate()

        if not check_validate:
            return False
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
    LawFileNo=StringField('法规文号',[
        DataRequired(),
        Length(max=255)
        ])
    LawType=SelectField('法规分类',choices=[
        ('综合','综合'),
        ('审计','审计'),
        ('财政财务','财政财务'),
        ('税收','税收'),
        ('金融','金融'),
        ('企业','企业'),
        ('党内规章规制度','党内规章规制度')
        ])
    LawPublishDate=DateField('发布日期',[DataRequired()])
    LawMark=StringField('备注')
    LawContent=TextAreaField('法规正文',[DataRequired()])
    LawTags=StringField('标签')

class PostForm(Form):
    title=StringField('Title',[
        DataRequired(),
        Length(max=255)
        ])
    type=SelectField('Post Type',choices=[
        ('Blog','文字'),
        ('VideoBlog','视频'),
        ('ImageBlog','图片'),
        ('QuoteBlog','Quto')
        ])

    text=TextAreaField('内容')
    image=StringField('图片URL',[Length(max=500)])
    video=StringField('视频URL',[Length(max=500)])
    author=StringField('作者',[Length(max=500)])
    tag=StringField('Tags')

class OpenIDForm(Form):
    openid=StringField('OpenID URL',[DataRequired()],URL)