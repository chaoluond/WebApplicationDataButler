import operator, os, pickle, sys, os.path
import cherrypy
import mysql.connector
from mysql.connector import Error
import logging
import json
from config import conf
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(os.path.abspath(os.path.dirname(__file__))+'/templates/'))
import apiutil
from apiutil import errorJSON
import boto
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

class ProjectID(object):
    exposed = True

    connMysql = createCnx

    def GET(self, projID):

	if cherrypy.session.has_key('username'):
		

		cnx, cursor = self.connMysql()
		email = cherrypy.session['username']
                q = "select userID from users where email='%s'" % email
                cursor.execute(q)
                userID = cursor.fetchone()[0]
                q = "select projID from projUser where userID = %s" % userID
                cursor.execute(q)
                user_projects = cursor.fetchall()
		user_projects = [item[0] for item in user_projects]
                if int(projID) in user_projects:
                        

			# Retrieve fullname
                	q = "Select fullname from users where email = '%s'" % email
                	cursor.execute(q)
                	fullname = cursor.fetchall()[0][0]
                	firstname = fullname.split(' ')[0]
	

			#Select project name and project desciption
			q = "SELECT projName, description, author FROM projects WHERE projID = '%s'" % projID
			cursor.execute(q)
			result = cursor.fetchone()
			projName = result[0]
			description = result[1]
			author = result[2]
	        

			#Select project creator 
			q = "SELECT fullname from users WHERE userID = '%s'" % author
			cursor.execute(q)
			creator = cursor.fetchone()
			creator = creator[0]
	
			#Select all users of the project
			users = []
			q = "SELECT userID FROM projUser WHERE projID = '%s'" % projID
			cursor.execute(q)
			userIDs = cursor.fetchall()
			for userID in userIDs:
				q = "SELECT fullname FROM users WHERE userID = '%s'" % userID
				cursor.execute(q)
				result = cursor.fetchone()
				users.append(str(result[0]))
		
			#Return all files in this project
			q = "SELECT dataID, url, filename, date FROM datafiles WHERE projID = '%s'" % projID
			cursor.execute(q)
			files = cursor.fetchall()
	
			cnx.commit()
			cnx.close()
			return env.get_template('project_view.html').render(signed_in = True, creator = creator,
					fullname = firstname,
					projName = projName,
					description = description,
					users = users,
					files = files,
					projID = projID)
		else:
			return errorJSON(code=5000, message = "No access to selected contents!")	
	else:
	    return env.get_template('userlogin.html').render(signed_in = False)


	
    def DELETE(self, projID):
				            
		if cherrypy.session.has_key('username'):


                	cnx, cursor = self.connMysql()
                	email = cherrypy.session['username']
                	q = "select userID from users where email='%s'" % email
                	cursor.execute(q)
                	userID = cursor.fetchone()[0]
                	q = "select projID from projUser where userID = %s" % userID
                	cursor.execute(q)
                	user_projects = cursor.fetchall()
                	user_projects = [item[0] for item in user_projects]
                	if int(projID) in user_projects:
				
				# Step 1: delete all data files in s3
				q = "select url from datafiles where projID = '%s'" % projID
				cursor.execute(q)
				urls = cursor.fetchall()


				# Connect to s3
				s3 = boto.connect_s3()
                                bucket = s3.get_bucket('databutler')
				
				for item in urls:
					url = item[0]
					key = bucket.get_key(url)
                                	bucket.delete_key(key)

				# Step 2: delete the records in datafiles table
				q = "delete from datafiles where projID = '%s'" % projID
				cursor.execute(q)
				
				
				# Step 3: delete the records in projUser table
				q = "delete from projUser where projID = '%s'" % projID
				cursor.execute(q)


				# Step 4: delete the records in projects table
				q = "delete from projects where projID = '%s'" % projID
				cursor.execute(q)
				cnx.commit()
				cnx.close()
				return env.get_template('redirect-tmpl.html').render(signed_in = True)
				
			else:
				return errorJSON(code=5000, message="No access to selected content!")
		else:
			print "Must login first!"
                        return errorJSON(code = 3000, message = "Operation requires login!")
 
					
					
				
				

		

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
	application = cherrypy.Application(ProjectID(),None,conf)
