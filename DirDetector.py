#coding: utf8
import runDetector

class DirDetector:
	def __init__(self):
		self.defaultThreadAmount = 4
		self.detector = runDetector.Detector(self.defaultThreadAmount)
				
	def run(self, status):
		self.detector.run( status )
		
	def status(self):
		return {'url': None, 'threadAmount': self.defaultThreadAmount}
	
	def result(self):
		return {}		############# TODO
			
	def help(self):
		return("Description: used to detect sensitive directories under an url.\n" + 
			"You must to pass an url, and the other argument 'threadAmount' is \
			 optional (which is between 1 and 10), 4 is default.\n\n"
		)
	
if __name__ == '__main__':
	import sys

	status = { 'url': None, 'threadAmount': '4' }
	detector = DirDetector()
	
	if len(sys.argv) > 1:
		status["url"] = sys.argv[1]
		if len(sys.argv) == 3:
			status["threadAmount"] = sys.argv[2]
	else:
		print("Error: invalid arguments!")
		print( detector.help() )
		sys.exit( 1 )
	detector.run( status )

