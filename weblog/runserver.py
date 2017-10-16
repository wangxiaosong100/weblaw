"""
This script runs the weblog application using a development server.
"""
from flask_script import Manager,Server
from os import environ
from weblog import app
from weblog.MongoDB_Models import mongo,User,Comment,Law,Department,LawType
import win32com

HOST = environ.get('SERVER_HOST', '127.0.0.1')
try:
    PORT = int(environ.get('SERVER_PORT', '5000'))
except ValueError:
    PORT = 5000

manager=Manager(app)
manager.add_command("server",Server(HOST,PORT))

@manager.shell
def make_shell_context():
    return dict(app=app,User=User,Comment=Comment,Law=Law,Department=Department,LawType=LawType)

if __name__ == '__main__':
    manager.run()
