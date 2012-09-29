import os

from flask.ext.script import Manager
from flask.ext.evolution import Evolution
from whenworks import app


manager = Manager(app)
evolution = Evolution(app)

@manager.command
def migrate(action):
    evolution.manager(action)

@manager.command
def serve():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    manager.run()
