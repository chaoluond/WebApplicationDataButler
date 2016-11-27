import cherrypy
import apiutil
import mysql.connector
from mysql.connector import Error
import sys
sys.stdout = sys.stderr # Turn off console output; it will get logged by Apache
import json
from apiutil import errorJSON
from passlib.apps import custom_app_context as pwd_context
from config import conf
import os
import os.path
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(os.path.abspath(os.path.dirname(__file__))+'/templates/'))

class UserLogin(object):
    exposed = True

    def GET(self, logout_sign=False):
        ''' return user login form '''

        output_format = cherrypy.lib.cptools.accept(['text/html', 'application/json'])

        if output_format == 'text/html':
            return env.get_template('userlogin-tmpl.html').render(
                base=cherrypy.request.base.rstrip('/') + '/',
                logout_sign = logout_sign
                )

    @cherrypy.tools.json_in(force=False)
    def POST(self,username=None,password=None):
        ''' login existing user
        should only be used through SSL connection
        expects JSON:
        { 'username' : username,
          'password' : password
        }
        return JSON:
        { 'errors' : [] }
        error code / message:
        3000 : Expected username and password
        3001 : Incorrect username or password
        '''
        output_format = cherrypy.lib.cptools.accept(['text/html', 'application/json'])
        
	if not username:
            try:
                username = cherrypy.request.json["username"]
            except:
                if output_format == 'text/html':
                  return env.get_template('loginerror-tmpl.html').render(
                  base=cherrypy.request.base.rstrip('/') + '/'
                  )
                else:
                  return errorJSON(code=3001, message="Expected username and password")
        if not password:
            try:
                password = cherrypy.request.json["password"]
            except:
                if output_format == 'text/html':
                  return env.get_template('loginerror-tmpl.html').render(
                  base=cherrypy.request.base.rstrip('/') + '/'
                  )
                else:
                  return errorJSON(code=3001, message="Expected username and password")

        cnx = mysql.connector.connect(user='root',host='127.0.0.1',database='databutler',charset='utf8mb4')
        cursor = cnx.cursor()
        q="select password from users where email=%s";
        cursor.execute(q,(username,))
        r=cursor.fetchall()
        if len(r) == 0:
            if output_format == 'text/html':
              return env.get_template('loginerror-tmpl.html').render(
                base=cherrypy.request.base.rstrip('/') + '/'
              )
            else:
              return errorJSON(code=3002, message="Incorrect username or password")
        hash=r[0][0]
        match=pwd_context.verify(password,hash)
        #print "\nHash: %s \nmatch %s" % (hash,match)
        password=""
        if not match:
            # username / hash do not exist in database
            if output_format == 'text/html':
              return env.get_template('loginerror-tmpl.html').render(
                base=cherrypy.request.base.rstrip('/') + '/'
              )
            else:
              return errorJSON(code=3002, message="Incorrect username or password")
        else:
            # username / password correct
            cherrypy.session.regenerate()
            cherrypy.session['username'] = username
            print "SAVED session['username'] = %s" % username

            if output_format == 'text/html':
              return env.get_template('redirect-tmpl.html').render(
                base=cherrypy.request.base.rstrip('/') + '/'
              )
            else:
              result={'errors':[]}
              return json.dumps(result)

application = cherrypy.Application(UserLogin(), None, conf)
