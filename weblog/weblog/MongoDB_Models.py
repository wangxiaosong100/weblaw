#-*- coding:utf-8-*-

from flask_mongoengine import MongoEngine
import datetime
mongo=MongoEngine()
available_roles=('admin','poster','default')

#部门信息
class Department(mongo.Document):
    departmentCode=mongo.StringField(required=True)
    departmentname=mongo.StringField(required=True)
    parentCode=mongo.StringField()

    def __repr__(self):
          return "<Department '{}'>".format(self.departmentname)

#用户信息
class User(mongo.Document):
      username=mongo.StringField(required=True)
      password=mongo.StringField(required=True)
      roles=mongo.ListField(
          mongo.StringField(choices=available_roles)
          )
      user_head=mongo.StringField()
      department=mongo.ReferenceField(Department)

      def getBcrypt_password(self,password):
        return bcrypt.generate_password_hash(password)
      def check_password(self,password):
        #return bcrypt.check_password_hash(self.password,password)
        if self.password==password:
            return True
        else:
            return False
      def __repr__(self):
          return "<User '{}'>".format(self.username)
#法规分类
class LawType(mongo.Document):
    LawTypName=mongo.StringField(required=True)
    parentId=mongo.StringField()
    typeimage=mongo.StringField()#法规显示的图标
    def __repr__(self):
          return "<LawType '{}'>".format(self.LawTypName)

#法规评论
class Comment(mongo.EmbeddedDocument):
    name=mongo.StringField(required=True)
    text=mongo.StringField(required=True)
    date=mongo.DateTimeField(default=datetime.datetime.now())

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])

#法规主体
class Law(mongo.Document):
    __tablename__='Law'
    __searchable__ = ['LawTitle', 'LawFileNo','LawContent']

    LawTitle=mongo.StringField(required=True)#标题
    LawFileNo=mongo.StringField(required=True)#文号
    LawPublishDepart=mongo.StringField()#发布部门
    LawType=mongo.ReferenceField(LawType) #法规分类
    LawPublishDate=mongo.DateTimeField()#发布/生效日期
    LawMark=mongo.StringField()#备注
    LawContent=mongo.StringField(required=True)#正文
    LawTags=mongo.ListField(mongo.StringField())#标签
    Lawcomments=mongo.ListField(
        mongo.EmbeddedDocumentField(Comment)
        )#评论
    time=mongo.DateTimeField()#添加时间
    user=mongo.ReferenceField(User)#添加用户
    check=mongo.StringField(required=True)#是否审核通过
    def __repr__(self):
        return "<Law '{}'>".format(self.LawTitle)
    
    def get_commentslen(self):
        return len(self.Lawcomments)
    def get_tags(self):
        return len(self.LawTags)


#class Post(mongo.Document):
#    title=mongo.StringField(required=True)
#    publish_date=mongo.DateTimeField(
#        default=datetime.datetime.now()
#        )
#    user=mongo.ReferenceField(User)
#    comments=mongo.ListField(
#        mongo.EmbeddedDocumentField(Comment)
#        )
#    tags=mongo.ListField(mongo.StringField())
#    meta={
#        'allow_inheritance':True
#        }
#    def __repr__(self):
#        return "<Post '{}'>".format(self.title)
#    def get_commentslen(self):
#        return len(self.comments)

#class BlogPost(Post):
#    text=mongo.StringField(required=True)

#    @property
#    def type(self):
#        return "Blog"

#class VideoPost(Post):
#    url=mongo.StringField(required=True)
#    @property
#    def type(self):
#        return "VideoBlog"
#class ImagePost(Post):
#    image_url=mongo.StringField(required=True)
#    @property
#    def type(self):
#        return "ImageBlog"
#class QuotePost(Post):
#    quote=mongo.StringField(required=True)
#    author=mongo.StringField(required=True)
#    @property
#    def type(self):
#        return "QuoteBlog"