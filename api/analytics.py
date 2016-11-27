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
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
import matplotlib.pyplot as plt
from cherrypy.lib.static import serve_file




#Create connection to MySQL
def createCnx(self):
        #Define database variables
        DATABASE_USER='root'
        DATABASE_HOST='127.0.0.1'
        DATABASE_NAME='databutler'

        cnx=mysql.connector.connect(user=DATABASE_USER, host=DATABASE_HOST, database=DATABASE_NAME)
        cursor=cnx.cursor()
        return cnx, cursor

class Analysis(object):
    exposed = True

    connMysql = createCnx

    def __init__(self):
	self.xyPlot = XYPlot()
	self.figureview = Figureview()
	


    def _cp_dispatch(self, vpath):
	if len(vpath) == 1:
	    temp = vpath.pop()
            cherrypy.request.params['dataID'] = temp
	    return self
	elif len(vpath) == 2:
	    temp = vpath.pop()
	    cherrypy.request.params['dataID'] = vpath.pop()
	    if temp == 'xyplot':
	        return self.xyPlot
	    elif temp == 'figureview':
		return self.figureview
	return vpath


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
                q = "select filename, date from datafiles where dataID=%s" % dataID
                cursor.execute(q)
                temp = cursor.fetchall()[0]
                filename = temp[0]
                date = temp[1]
	        cnx.close()
                return env.get_template('analysis-tmpl.html').render(signed_in=True, display = False, fullname = firstname, dataID = dataID, date=date, filename=filename)

            else:
                return errorJSON(code=7000, message="No access to selected content!")

	else:
            print "Must login first!"
            return errorJSON(code=3000, message = "Operation requires login!")


		    
	
class XYPlot(object):
   
    exposed = True
    
    connMysql = createCnx

    def GET(self, dataID):
	# connect to mysql
        cnx, cursor = self.connMysql()
        email = cherrypy.session['username']
        q = "select * from users where email='%s'" % email
        cursor.execute(q)
        temp = cursor.fetchall()[0]
        userID = temp[0]
        fullname = temp[1]
        firstname = fullname.split(' ')[0]

	q = "select filename, date from datafiles where dataID=%s" % dataID
        cursor.execute(q)
        temp = cursor.fetchall()[0]
        filename = temp[0]
        date = temp[1]

	x, y = self.loadData(dataID)
	plt.plot(x, y)
	plt.ylabel('x-y plot')
	plt.savefig('/var/www/databutler/temp/' + dataID + '_xyplot.png')
	plt.close()
	return env.get_template('analysis-tmpl.html').render(signed_in=True, display = True, fullname = firstname, dataID = dataID, date=date, filename=filename)


	
    def loadData(self, dataID):

        x = []
        y = []

        cnx, cursor = self.connMysql()
        q = "select url, filename from datafiles where dataID=%s" % dataID
        cursor.execute(q)
        result = cursor.fetchone()
        url = result[0]
        filename = result[1]

        s3 = boto.connect_s3()
        bucket = s3.get_bucket('databutler')
        key = bucket.get_key(url)
        destination = '/var/www/databutler/temp/'+filename
        key.get_contents_to_filename(destination)

        # Read file into data
        txt = open(destination)
        for line in txt:
            temp = line.split('\t')
            x.append(float(temp[0]))
            y.append(float(temp[1]))



        # Delete the original file from server
        os.remove(destination)
	
	
	return x, y	


class Figureview(object):
   

    exposed = True


    def GET(self, dataID):
	
	destination = '/var/www/databutler/temp/' + dataID + '_xyplot.png'
	file_for_download = serve_file(destination)
	return file_for_download


	
	
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
		cherrypy.quickstart(Analysis(),'/databutler',conf)
else:
	application = cherrypy.Application(Analysis(),None,conf)
