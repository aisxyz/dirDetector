# coding: utf8
import re
import os
import time
import urllib2
import urlparse
import Queue
import threading

import fileConfigPath
from urlDbManager import UrlDbManager
	
class Detector:
	def __init__(self, threadAmount):
		self.subdomainQueue = Queue.Queue()
		self.subdomainFollowQueue = Queue.Queue()
		self.threadLock = threading.Lock()
		self.defaultThreadAmount = threadAmount
		self.maxThreadAmount = 10
		self.actualThreadAmount = self.defaultThreadAmount
		self.matchRule = None
		self.urlInfoTableName = None
		self.isScanFinished = False
		self.urlDbManager = UrlDbManager()
		
		self.linkMatchRule = re.compile( r'''href=['"](.*?)['"]''', re.S )
		
	def run(self, status):
		self.normalStatus( status )
		self.urlDbManager.addToUrlRecordTable( status['url'] )
		self.matchRule = self.subdomainMatchRule( status['url'] )
		self.urlInfoTableName = self.matchRule.replace( '.', '_' )
		self.urlDbManager.createUrlInfoTable( self.urlInfoTableName )
		
		self.addToTwoQueues( status['url'] )			
		self.scanSensitiveDirectory()	
	
	def subdomainMatchRule(self, url):
		# Not very accurite, maybe be missing some subdomains
		return urlparse.urlsplit(url).hostname #.split('.')[1]
	
	def normalUrl(self, url):
		# There should be protocol in url
		return( url if '://' in url else 'http://' + url )
	
	def normalStatus(self, status):
		status['url'] = self.normalUrl( status['url'] )
		
		# threadAmount should between 1 and maxThreadAmount, and be integer.
		if str(status['threadAmount']).isdigit():
			if int(status['threadAmount']) > self.maxThreadAmount:
				self.actualThreadAmount = status['threadAmount'] = self.maxThreadAmount
			elif int(status['threadAmount']) >= 1:
				self.actualThreadAmount = status['threadAmount'] = int(status['threadAmount'])
			else:
				self.actualThreadAmount = status['threadAmount'] = self.defaultThreadAmount
	
	def getMatchSubdomain(self, url):
		try:
			html_page = urllib2.urlopen( url ).read()
		except:
			return
		for link in self.linkMatchRule.finditer( html_page ):
			if self.matchRule in link.group(1):
				yield link.group(1)
	
	def getSensitiveLinkInfo(self, link):
		with open( fileConfigPath.g_sensitiveWordsFile ) as fd:
			for line in fd:
				line = line.split('-->')
				if line[0].strip() in link:
					return (link, line[0].strip(), line[1].strip())
		return (link, 'null', 'null')
		
	def scanSingleLink(self):
		while not self.isScanFinished:
			while not self.subdomainQueue.empty():
				link = self.subdomainQueue.get()
				linkInfo = self.getSensitiveLinkInfo( link )
				self.threadLock.acquire()
				self.urlDbManager.addToUrlInfoTable( self.urlInfoTableName, linkInfo )
				print(linkInfo)					####### Test output
				self.threadLock.release()
			time.sleep(1)
		
	def followSublink(self):
		while not self.subdomainFollowQueue.empty():
			link = self.subdomainFollowQueue.get()
			for sublink in self.getMatchSubdomain( link ):
				self.addToTwoQueues( sublink )
		self.isScanFinished = True
				
	def scanSensitiveDirectory(self):
		allThreads = []
		for threadCount in range( self.actualThreadAmount ):
			followLinkThread = threading.Thread( target=self.followSublink )
			followLinkThread.start()
			allThreads.append( followLinkThread )
			
			scanSensitiveDirThread = threading.Thread( target=self.scanSingleLink )
			scanSensitiveDirThread.start()
			allThreads.append( scanSensitiveDirThread )
			
		for thread in allThreads:
			thread.join()		
	
	def stripPage(self, link):
		'''Remove specific link page, for example: .html etc.'''
		linkParts = link.rsplit('/', 1)
		# Judge protocol in case of link like http://www.baidu.com
		return( link if '://' not in linkParts[0] or '.' not in linkParts[-1] else linkParts[0] + '/' )
		
	def addToTwoQueues(self, url):
		for link in self.getMatchSubdomain( url ):
			try:
				link = self.stripPage( self.normalUrl( link ) )
				if not self.urlDbManager.isStoredIntoUrlInfoTable( link, self.urlInfoTableName ):
					self.subdomainQueue.put( link )
					self.subdomainFollowQueue.put( link )
			except: 			# There may be some coding errors, but I don't know how to fix them. 
				self.threadLock.acquire()
				with open( fileConfigPath.g_linkErrorFilePath, 'a+', 1) as fd:
					fd.write( link + os.linesep )
				self.threadLock.release()
				
