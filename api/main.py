import cherrypy
import operator, os, pickle, sys, os.path
import mysql.connector
from mysql.connector import Error
import logging
import json
from config import conf
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(os.path.abspath(os.path.dirname(__file__))+'/templates/'))
import apiutil
import threading

#Define logging file
#logging.basicConfig(filename='mysql.log', level=logging.DEBUG, format='%(asctime)s %(message)s')


#create connection to MySQL
def createCnx(self):
        #Define database variables
        DATABASE_USER='root'
        DATABASE_HOST='127.0.0.1'
        DATABASE_NAME='databutler'

        cnx=mysql.connector.connect(user=DATABASE_USER, host=DATABASE_HOST, database=DATABASE_NAME)
        cursor=cnx.cursor()
        return cnx, cursor

class Databutler(object):
    exposed = True
    connMysql = createCnx
    def GET(self):
	if cherrypy.session.has_key('username'):
	    signed_in = True
	    email = cherrypy.session['username']
	    cnx, cursor = self.connMysql()
	    q = "SELECT fullname FROM users WHERE email = '%s'" % email
	    cursor.execute(q)
	    fullname = cursor.fetchall()[0][0]
	    firstname = fullname.split(' ')[0]
	    return env.get_template('welcomepage.html').render(signed_in = True, fullname = firstname)
	else:
	    return env.get_template('welcomepage.html').render(signed_in = False)	


if __name__ == '__main__':
		conf = {
			'/': {
				'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
				'tools.sessions.on': True,
				'tools.staticdir.root': os.path.abspath(os.getcwd())
			},
			'/css': {
				'tools.staticdir.on': True,
				'tools.staticdir.dir': './css'
			},
			'/js': {
				'tools.staticdir.on': True,
				'tools.staticdir.dir': './js'
			}
		}
		cherrypy.quickstart(Databutler(),'/databutler',conf)
else:
	application = cherrypy.Application(Databutler(),None,conf)
