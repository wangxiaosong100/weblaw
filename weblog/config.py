from os import path

class Config(object):
    SECRET_KEY='aba8211275f56d02cd3fbeb8bab7c333'

class ProdConfig(Config):
    pass

class DevConfig(Config):
    DEBUG=True
    SQLALCHEMY_ECHO=False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(path.pardir, 'app.db')
    SQLALCHEMY_MIGRATE_REPO = path.join(path.pardir, 'db_repository')
    CELERY_BROKER_URL="amqp://guest:guest@localhost:5672//"
    CELERY_BACKEND="amqp://guest:guest@localhost:5672//"

    MONGODB_SETTINGS={
       'db':'local',
       'host':'localhost',
       'port':27017
        }