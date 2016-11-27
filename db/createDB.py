import mysql.connector

#Define database variables
DATABASE_USER = 'root'
DATABASE_HOST = '127.0.0.1'
DATABASE_NAME = 'databutler'

#Create connection to MySQL
cnx = mysql.connector.connect(user=DATABASE_USER, host=DATABASE_HOST, use_unicode=True)
cursor = cnx.cursor()

###################################
## Create DB if it doesn't exist ##
###################################

createDB = (("CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET utf8mb4") % (DATABASE_NAME))
cursor.execute(createDB)

#############################
## Switch to databutler DB ##
#############################

useDB = (("USE %s") % (DATABASE_NAME))
cursor.execute(useDB)

###########################
## Drop all tables first ##
###########################

#datafiles
dropTableQuery = ("DROP TABLE IF EXISTS datafiles")
cursor.execute(dropTableQuery)

#projUser
dropTableQuery = ("DROP TABLE IF EXISTS projUser")
cursor.execute(dropTableQuery)

#Users
dropTableQuery = ("DROP TABLE IF EXISTS users")
cursor.execute(dropTableQuery)

#Projects
dropTableQuery = ("DROP TABLE IF EXISTS projects")
cursor.execute(dropTableQuery)

########################
## Create tables next ##
########################

#Users
createTableQuery = ("CREATE TABLE users ("
						"userID INT NOT NULL AUTO_INCREMENT,"
						"fullname VARCHAR(45) CHARACTER SET utf8mb4  NOT NULL,"
						"email VARCHAR(45)  CHARACTER SET utf8mb4 NOT NULL,"
						"password VARCHAR(120)  CHARACTER SET utf8mb4 NOT NULL,"
						"UNIQUE KEY (email) USING BTREE,"
						"PRIMARY KEY (userID))")
cursor.execute(createTableQuery)

#Projects
createTableQuery = '''CREATE TABLE projects (
					projID INT NOT NULL AUTO_INCREMENT,
					projName VARCHAR(50)  CHARACTER SET utf8mb4  NOT NULL,
					description VARCHAR(200) CHARACTER SET utf8mb4,
					author INT NOT NULL,
					FOREIGN KEY(author) REFERENCES users(userID) ON DELETE CASCADE,
					PRIMARY KEY (projID),
					UNIQUE KEY (author, projName) USING BTREE
					)'''
cursor.execute(createTableQuery)

#project-user
createTableQuery = '''CREATE TABLE projUser (
						projID INT NOT NULL,
						userID INT NOT NULL,
						FOREIGN KEY(projID) REFERENCES projects(projID) ON DELETE CASCADE,
						FOREIGN KEY(userID) REFERENCES users(userID) ON DELETE CASCADE,
						PRIMARY KEY(projID, userID)
						);'''
cursor.execute(createTableQuery)
						
#datafiles
createTableQuery = '''CREATE TABLE datafiles (
			dataID INT NOT NULL AUTO_INCREMENT,
			url VARCHAR(100) NOT NULL,
			filename VARCHAR(50) NOT NULL,
			date DATE NOT NULL,
			projID INT NOT NULL,
			FOREIGN KEY(projID) REFERENCES projects(projID) ON DELETE CASCADE,
			PRIMARY KEY(dataID),
			UNIQUE KEY (url) USING BTREE
			)'''
cursor.execute(createTableQuery)



#Commit the data and close the connection to MySQL
cnx.commit()
cnx.close()
