"""
This script runs the weblog application using a development server.
"""
from flask_script import Manager,Server
from os import environ
from weblog import app
from weblog.MongoDB_Models import mongo,Post,User,Comment,BlogPost,VideoPost,ImagePost,QuotePost 

HOST = environ.get('SERVER_HOST', '192.168.1.104')
try:
    PORT = int(environ.get('SERVER_PORT', '5000'))
except ValueError:
    PORT = 5000

manager=Manager(app)
manager.add_command("server",Server(HOST,PORT))

@manager.shell
def make_shell_context():
    return dict(app=app,Post=Post,User=User,Comment=Comment,BlogPost=BlogPost,VideoPost=VideoPost,ImagePost=ImagePost)

if __name__ == '__main__':
    manager.run()
