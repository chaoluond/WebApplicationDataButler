import cherrypy
import apiutil
import sys
sys.stdout = sys.stderr # Turn off console output; it will get logged by Apache
import json
from apiutil import errorJSON
from config import conf
from cherrypy.lib import sessions
import os
import os.path
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(os.path.abspath(os.path.dirname(__file__))+'/templates/'))


class UserLogout(object):
    exposed = True

    def GET(self):
        sess = cherrypy.session
        username = sess.get('username', None)
        print "logout SESSION KEY %s" % username
        print "logout value of SESSION KEY %s" % cherrypy.session['username']
        sess['username'] = None
        sessions.expire()
        if username:
            print "found username %s " % username
            cherrypy.request.login = None

        output_format = cherrypy.lib.cptools.accept(['text/html', 'application/json'])
        if output_format == 'text/html':
          return env.get_template('userlogout-tmpl.html').render(
             base=cherrypy.request.base.rstrip('/') + '/',
	  
          )
        else:
          r={'errors':[]}
          return json.dumps(r)

application = cherrypy.Application(UserLogout(), None, conf)
