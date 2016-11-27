import cherrypy
import operator, os, pickle, sys, os.path
import tempfile
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
import datetime
import boto
from cherrypy.lib.static import serve_file
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

class NamedPart(cherrypy._cpreqbody.Part):
	def make_file(self):
		return tempfile.NamedTemporaryFile()

cherrypy._cpreqbody.Entity.part_class = NamedPart

class Datafiles(object):
	exposed = True

	def __init__(self):
		self.preview = DataPreview()
		self.download = DataDownload()
		self.delete = DataDelete()
		
	def _cp_dispatch(self, vpath):
		if len(vpath) == 1:
			temp = vpath.pop()
			if temp == 'upload':
				return self
			else:
				cherrypy.request.params['dataID'] = temp;
				return self
		elif len(vpath) == 2:
			temp = vpath.pop()
			cherrypy.request.params['dataID'] = vpath.pop()
			if temp == 'preview':
				return self.preview
			elif temp == 'download':
				return self.download
			elif temp == 'delete':
				return self.delete
		return vpath	

	connMysql = createCnx

	def GET(self, dataID):
		if cherrypy.session.has_key('username'):
			# connect to mysql
			cnx, cursor = self.connMysql()
			email = cherrypy.session['username']
			q = "select * from users where email='%s'" % email
			cursor.execute(q)
			temp = cursor.fetchall()[0]
			userID = temp[0]
			fullname = temp[1]
			firstname = fullname.split(' ')[0]
			q = "select projID from projUser where userID=%s" % userID
			cursor.execute(q)
			user_projects = cursor.fetchall()[0]
			q = "select projID from datafiles where dataID=%s" % dataID
			cursor.execute(q)
			data_project = cursor.fetchall()[0][0];
			if data_project in user_projects:
				q = "select filename, date from datafiles where dataID=%s" % dataID
				cursor.execute(q)
				temp = cursor.fetchall()[0]
				filename = temp[0]
				date = temp[1]
				q = "select projName from projects where projID=%s" % data_project
				cursor.execute(q)
				projName = cursor.fetchall()[0][0]
				cnx.close()
				return env.get_template('datafile-tmpl.html').render(signed_in=True, fullname = firstname, filename=filename, date=date, dataID = dataID, projName = projName, projID = data_project)
				
			else:
				cnx.close()
				return errorJSON(code=6000, message="No access to selected content!")
			
		else:
			print "Must login first!"
			return errorJSON(code=3000, message = "Operation requires login!")

	@cherrypy.config(**{'response.timeout': 3600}) # default is 300s	
	def POST(self, userfile, description, projID):
		if cherrypy.session.has_key('username'):
			assert isinstance(userfile, cherrypy._cpreqbody.Part)
			filename=userfile.filename
			destination = os.path.join('/var/www/databutler/temp', filename)
			os.link(userfile.file.name, destination)
			# connect to mysql
			cnx, cursor = self.connMysql()
			email = cherrypy.session['username']
			q = "select userID from users where email='%s'" % email
			cursor.execute(q)
			userID = cursor.fetchall()[0][0]
			today = datetime.date.today().strftime("%Y-%m-%d")
			url = str(userID)+'/'+today+'/'+filename
			q = "insert into datafiles (url, filename, date, projID) values ('%s','%s','%s',%s)"\
				% (url, filename, today, projID)
			cursor.execute(q)
			cnx.commit()
			cnx.close()
			# send file to s3
			s3 = boto.connect_s3()
			bucket = s3.get_bucket('databutler')
			key = bucket.new_key(url)
			key.set_contents_from_filename(destination)	
			#clean up the temporary file
			os.remove(destination)
			#return the result
			#result = {'filename': filename, 'status':'successfully uploaded'}
			#return json.dumps(result)
			return env.get_template('redirect-projid.html').render(projID=projID)
		
		else:
			print "Must login first!"
			return errorJSON(code=3000, message = "Operation requires login!")

class DataPreview(object):
	exposed = True
	connMysql = createCnx

	def GET(self, dataID):
		if cherrypy.session.has_key('username'):
			# connect to mysql
			cnx, cursor = self.connMysql()
			email = cherrypy.session['username']
			q = "select * from users where email='%s'" % email
			cursor.execute(q)
			temp = cursor.fetchall()[0]
			userID = temp[0]
			fullname = temp[1]
			firstname = fullname.split(' ')[0]
			q = "select projID from projUser where userID=%s" % userID
			cursor.execute(q)
			user_projects = cursor.fetchall()
			q = "select projID from datafiles where dataID=%s" % dataID
			cursor.execute(q)
			data_project = cursor.fetchall()[0];
			if data_project in user_projects:
				q = "select url from datafiles where dataID=%s" % dataID
				cursor.execute(q)
				url = cursor.fetchall()[0][0]
				q = "select filename from datafiles where dataID=%s" % dataID
				cursor.execute(q)
				filename = cursor.fetchall()[0][0]
				s3 = boto.connect_s3()
				bucket = s3.get_bucket('databutler')
				key = bucket.get_key(url)
				destination = '/var/www/databutler/temp/'+filename
				key.get_contents_to_filename(destination)
				#file_for_download = serve_file(destination,"application/x-download","attachment")
				file_for_download = serve_file(destination)
				os.remove(destination)
				cnx.close()
				return file_for_download
			else:
				cnx.close()
				return errorJSON(code=6000, message="No access to selected content!")
			
		else:
			print "Must login first!"
			return errorJSON(code=3000, message = "Operation requires login!")


class DataDelete(object):
	exposed = True
	connMysql = createCnx

	def GET(self, dataID):
		if cherrypy.session.has_key('username'):
			cnx, cursor = self.connMysql()

			email = cherrypy.session['username']
                        q = "select userID from users where email='%s'" % email
                        cursor.execute(q)
                        userID = cursor.fetchone()[0]
                        q = "select projID from projUser where userID=%s" % userID
                        cursor.execute(q)
                        user_projects = cursor.fetchall()
                        q = "select projID from datafiles where dataID=%s" % dataID
                        cursor.execute(q)
                        data_project = cursor.fetchall()[0];
                        if data_project in user_projects:
			
				q = "select url, projID from datafiles where dataID = '%s'" % dataID
				cursor.execute(q)
				result = cursor.fetchone()
				url = result[0]
				projID = result[1]
			
				# Delete the file from s3
				s3 = boto.connect_s3()
                        	bucket = s3.get_bucket('databutler')
                        	key = bucket.get_key(url)
				bucket.delete_key(key)
			

				# Delete the file from database
				q = "delete from datafiles where dataID = '%s'" % dataID
				cursor.execute(q)
				cnx.commit()
				cnx.close()

			
				# Redirect to project_view page
				return env.get_template('redirect-projid.html').render(projID=projID)
			else:
				return errorJSON(code=6000, message="No access to selected content!")
			

		else:
			print "Must login first!"
			return errorJSON(code = 3000, message = "Operation requires login!")
		


class DataDownload(object):
	exposed = True
	connMysql = createCnx

	def GET(self, dataID):
		if cherrypy.session.has_key('username'):
			# connect to mysql
			cnx, cursor = self.connMysql()
			email = cherrypy.session['username']
			q = "select * from users where email='%s'" % email
			cursor.execute(q)
			temp = cursor.fetchall()[0]
			userID = temp[0]
			fullname = temp[1]
			firstname = fullname.split(' ')[0]
			q = "select projID from projUser where userID=%s" % userID
			cursor.execute(q)
			user_projects = cursor.fetchall()
			q = "select projID from datafiles where dataID=%s" % dataID
			cursor.execute(q)
			data_project = cursor.fetchall()[0];
			if data_project in user_projects:
				q = "select url from datafiles where dataID=%s" % dataID
				cursor.execute(q)
				url = cursor.fetchall()[0][0]
				q = "select filename from datafiles where dataID=%s" % dataID
				cursor.execute(q)
				filename = cursor.fetchall()[0][0]
				s3 = boto.connect_s3()
				bucket = s3.get_bucket('databutler')
				key = bucket.get_key(url)
				destination = '/var/www/databutler/temp/'+filename
				key.get_contents_to_filename(destination)
				file_for_download = serve_file(destination,"application/x-download","attachment")
				os.remove(destination)
				return file_for_download
				
			else:
				return errorJSON(code=6000, message="No access to selected content!")
			
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
	application = cherrypy.Application(Datafiles(),None,conf)
