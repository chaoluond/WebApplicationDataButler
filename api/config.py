import cherrypy
conf = {
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.secureheaders.on': True,
        'tools.sessions.on' :True,
        'tools.sessions.debug' : True,
        'tools.sessions.storage_type': "file",
        'tools.sessions.storage_path': "/var/www/sessions",
        'tools.sessions.timeout': 15,
        #'tools.sessions.secure':True,
        #'tools.sessions.httponly':True
        }
    }
