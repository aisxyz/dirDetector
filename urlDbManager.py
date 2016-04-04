#coding: utf8
import sqlite3
import os.path
import fileConfigPath

class UrlDbManager:
	def __init__(self):
		self.recordDbPath = fileConfigPath.g_recordDbPath
		self.createUrlRecordTable()
	
	def createUrlRecordTable(self):
		if os.path.exists( self.recordDbPath ):
			return
		dbConn = sqlite3.connect( self.recordDbPath )
		dbCursor = dbConn.cursor()
		#if not os.path.getsize( self.recordDbPath ):
		dbCursor.execute('create table urlRecord (url text)')
		dbConn.commit()
		dbCursor.close()
		dbConn.close()
		
	def addToUrlRecordTable(self, url):
		dbConn = sqlite3.connect( self.recordDbPath )
		dbCursor = dbConn.cursor()
		if not list(dbCursor.execute('select * from urlRecord where url= ?', (url,))):
			dbCursor.execute('insert into urlRecord values (?)', (url,))
			dbConn.commit()
		dbCursor.close()
		dbConn.close()
		
	def createUrlInfoTable(self, tableName):
		try:
			dbConn = sqlite3.connect( self.recordDbPath )
			dbCursor = dbConn.cursor()
			dbCursor.execute( 'create table %s (subdomain text, sensitiveWord text, sensitiveInfo text)' %tableName )
			dbConn.commit()
			dbCursor.close()
			dbConn.close()
		#except sqlite3.OperationalError:
		except:
			pass		# if table has been created, just ignore it.
			
	def addToUrlInfoTable(self, tableName, insertInfo):
		dbConn = sqlite3.connect( self.recordDbPath )
		dbCursor = dbConn.cursor()
		if list(dbCursor.execute('select * from {0} where subdomain= ?'.format(tableName), (insertInfo[0], ))):
			dbCursor.execute( 'update {0} set sensitiveWord= ?, sensitiveInfo= ?'.format(tableName), insertInfo[1:] )
		else:
			dbCursor.execute('insert into {0} values (?, ?, ?)'.format(tableName), insertInfo)
		dbConn.commit()
		dbCursor.close()
		dbConn.close()
			
	def isStoredIntoUrlInfoTable(self, link, tableName):
		dbConn = sqlite3.connect( self.recordDbPath )
		dbCursor = dbConn.cursor()
		if list(dbCursor.execute('select * from {0} where subdomain= ?'.format(tableName), (link, ))):
			isStored = True
		else:
			isStored = False
		dbCursor.close()
		dbConn.close()
		return isStored
		
