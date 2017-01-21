#!/usr/local/bin/python
try:
    import flask
except ImportError:
    print "Install flask to run the web-app"
    raise

from dothub.web import app

if __name__ == '__main__':
    app.run()
