from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

# initialize the 'CLI facing' flask extensions on the created app:

manager = Manager(app)
migrate = Migrate(app, db)

# add the flask-script commands to be run from the CLI:---to remove later
manager.add_command('db', MigrateCommand)

@manager.command
def test():
   """Discovers and runs unit tests"""
   import unittest
   tests = unittest.TestLoader().discover('tests')
   unittest.TextTestRunner(verbosity=2).run(tests)




if __name__ == '__main__':
    manager.run()


