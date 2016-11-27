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
from apiutil import errorJSON
from projectid import ProjectID
#import threading

#Create connection to MySQL
def createCnx(self):
        #Define database variables
        DATABASE_USER='root'
        DATABASE_HOST='127.0.0.1'
        DATABASE_NAME='databutler'

        cnx=mysql.connector.connect(user=DATABASE_USER, host=DATABASE_HOST, database=DATABASE_NAME)
        cursor=cnx.cursor()
        return cnx, cursor

class Projects(object):
    exposed = True

    def __init__(self):
	self.new_project = NewProject()
        self.a_project = ProjectID()
    
    def _cp_dispatch(self, vpath):
        if len(vpath) == 1:
	  temp = vpath.pop()
          if temp == 'new':
            return self.new_project
          else:
            cherrypy.request.params['projID'] = temp
            return self.a_project
	return vpath

    connMysql = createCnx

    def GET(self):

	if cherrypy.session.has_key('username'):
		email = cherrypy.session['username']
		#return email
		cnx, cursor = self.connMysql()
		# Retrieve fullname
		q = "Select fullname from users where email = '%s'" % email
		cursor.execute(q)
		fullname = cursor.fetchall()[0][0]
		fullname = fullname.split(' ')[0]
		q = "SELECT userID FROM users WHERE email= '%s'" % email 
		cursor.execute(q)
		userID = cursor.fetchall()[0][0]
		q = "SELECT projID FROM projUser WHERE userID= %s" % userID
		cursor.execute(q)
		projIDs = cursor.fetchall()
		projects_info = []
		for projID in projIDs:
			q = "SELECT * FROM projects WHERE projID = %s" % projID
			cursor.execute(q)
			temp = cursor.fetchall()[0]
			projects_info.append(temp)
		cnx.commit()
		cnx.close()
		return env.get_template('projects.html').render(signed_in = True, projects = projects_info, fullname = fullname)
		
	else:
	    return env.get_template('userlogin.html').render(signed_in = False)	

class NewProject(object):
	exposed = True
	connMysql = createCnx
	def GET(self):
		if cherrypy.session.has_key('username'):
			email = cherrypy.session['username']
			cnx, cursor = self.connMysql()
			# Retrieve fullname
			q = "Select fullname from users where email = '%s'" % email
			cursor.execute(q)
			fullname = cursor.fetchall()[0][0]
			firstname = fullname.split(' ')[0]
			return env.get_template('new_project.html').render(signed_in = True, fullname = firstname)
		else:
			return env.get_template('userlogin.html').render(signed_in = False)
	
	@cherrypy.tools.json_in(force=False)
	def POST(self, projName=None, description=None):
		if cherrypy.session.has_key('username'):
			email = cherrypy.session['username']
			if not projName:
				try:
					projName = cherrypy.request.json["projName"]
					print "project name received!"
				except:
					print "project name not received"
					return errorJSON(code=4002, message="Expected text 'projName' for project as JSON input")
			if not description:
				try:
					description = cherrypy.request.json["description"]
					print "description received!"
				except:
					print "description not received"
					return errorJSON(code=4003, message="Expected 'description' for project as JSON input")
			cnx, cursor = self.connMysql()
			# get the author's ID
			q = "SELECT userID FROM users WHERE email = '%s'" % email
			cursor.execute(q)
			userID = cursor.fetchall()[0][0]
			# check if project already exists
			q = "SELECT EXISTS(SELECT 1 FROM projects WHERE projName='%s' AND author=%s)" % (projName, userID)
			cursor.execute(q)
			if cursor.fetchall()[0][0]:
				return errorJSON(code=4001, message="Project already exists.")
			# insert a new row in projects
			q = "INSERT INTO projects (projName, description, author) VALUES ('%s', '%s', %s)" % (projName, description, userID)
			try:
				cursor.execute(q)
			except Error as e:
				print "mysql error: %s" % e
				return errorJSON(code=4000, message="Failed to add project")
			# insert a new row in projUser
			q = "SELECT projID FROM projects WHERE author=%s AND projName='%s'" % (userID, projName)
			cursor.execute(q)
			projID = cursor.fetchall()[0][0]
			q = "INSERT INTO projUser (projID, userID) VALUES (%s, %s)" % (projID, userID)
			cursor.execute(q)
			cnx.commit()
			cnx.close()		
			return env.get_template('redirect-tmpl.html').render()

		else:
			print "Must login first!"
			return errorJSON(code=3000, message = "Operation requires login!")


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
	application = cherrypy.Application(Projects(),None,conf)
