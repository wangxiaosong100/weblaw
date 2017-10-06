from flask_mongoengine import MongoEngine
import datetime

mongo=MongoEngine()

available_roles=('admin','poster','default')

class User(mongo.Document):
      username=mongo.StringField(required=True)
      password=mongo.StringField(required=True)
      roles=mongo.ListField(
          mongo.StringField(choices=available_roles)
          )
      user_head=mongo.StringField()
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

class Comment(mongo.EmbeddedDocument):
    name=mongo.StringField(required=True)
    text=mongo.StringField(required=True)
    date=mongo.DateTimeField(default=datetime.datetime.now())

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])
class Law(mongo.Document):
    LawTitle=mongo.StringField(required=True)
    LawFileNo=mongo.StringField(required=True)
    LawType=mongo.StringField(required=True)
    LawPublishDate=mongo.DateTimeField()
    LawMark=mongo.StringField()
    LawContent=mongo.StringField(required=True)
    LawTags=mongo.ListField(mongo.StringField())
    Lawcomments=mongo.ListField(
        mongo.EmbeddedDocumentField(Comment)
        )
    time=mongo.DateTimeField()
    user=mongo.ReferenceField(User)
    def __repr__(self):
        return "<Law '{}'>".format(self.LawTitle)
    def get_commentslen(self):
        return len(self.Lawcomments)
    def get_tags(self):
        return len(self.LawTags)
class Post(mongo.Document):
    title=mongo.StringField(required=True)
    publish_date=mongo.DateTimeField(
        default=datetime.datetime.now()
        )
    user=mongo.ReferenceField(User)
    comments=mongo.ListField(
        mongo.EmbeddedDocumentField(Comment)
        )
    tags=mongo.ListField(mongo.StringField())
    meta={
        'allow_inheritance':True
        }
    def __repr__(self):
        return "<Post '{}'>".format(self.title)
    def get_commentslen(self):
        return len(self.comments)

class BlogPost(Post):
    text=mongo.StringField(required=True)

    @property
    def type(self):
        return "Blog"

class VideoPost(Post):
    url=mongo.StringField(required=True)
    @property
    def type(self):
        return "VideoBlog"
class ImagePost(Post):
    image_url=mongo.StringField(required=True)
    @property
    def type(self):
        return "ImageBlog"
class QuotePost(Post):
    quote=mongo.StringField(required=True)
    author=mongo.StringField(required=True)
    @property
    def type(self):
        return "QuoteBlog"