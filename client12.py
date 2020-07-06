#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
/**********************************************************************
* Filename    : client.py
* Description : Client for PiCar-V. Use python3 + pyqt5
* Author      : Dream
* Company     : Sunfounder
* E-mail      : service@sunfounder.com
* website     : www.sunfounder.com
* Update      : Dream    2016/09/12
**********************************************************************/
'''
import http.server
import socketserver

#PORT = 8000
#Handler = http.server.SimpleHTTPRequestHandler

#with socketserver.TCPServer(("",PORT),Handler) as httpd:
  #  print("Server is running at ", PORT)
   # print("To test from dockerized version , please run http://localhost:<exposed port>")
    #httpd.serve_forever()
import sys
if sys.version_info.major < 3 or sys.version_info.minor < 4:
    raise RuntimeError('At least Python 3.4 is required')

import sys, time, http.client
from PyQt5 import QtCore, uic, QtWidgets  
import icons_rc
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from urllib.request import urlopen
import requests

login_screen     = "login_screen.ui" 
running_screen   = "running_screen.ui"
setting_screen   = "setting_screen.ui"
calibrate_screen = "calibrate_screen.ui"

# Load the ui files 
Ui_Login_screen, QtBaseClass     = uic.loadUiType(login_screen)
Ui_Running_screen, QtBaseClass   = uic.loadUiType(running_screen)
Ui_Setting_screen, QtBaseClass   = uic.loadUiType(setting_screen)
Ui_Calibrate_screen, QtBaseClass = uic.loadUiType(calibrate_screen)
 
 # Set speed content, and speed level content
MAX_SPEED = 100
MIN_SPEED = 40
SPEED_LEVEL_1 = MIN_SPEED
SPEED_LEVEL_2 = (MAX_SPEED - MIN_SPEED) / 4 * 1 + MIN_SPEED
SPEED_LEVEL_3 = (MAX_SPEED - MIN_SPEED) / 4 * 2 + MIN_SPEED
SPEED_LEVEL_4 = (MAX_SPEED - MIN_SPEED) / 4 * 3 + MIN_SPEED
SPEED_LEVEL_5 = MAX_SPEED
SPEED = [0, SPEED_LEVEL_1, SPEED_LEVEL_2, SPEED_LEVEL_3, SPEED_LEVEL_4, SPEED_LEVEL_5]

HOST      = '192.168.0.133'
PORT 	  = '8000'
autologin = 1

# BASE_URL is variant use to save the format of host and port 
BASE_URL = 'http://' + HOST + ':'+ PORT + '/'

def __reflash_url__():
	global BASE_URL
	BASE_URL = 'http://' + HOST + ':'+ PORT + '/'


def __read_auto_inf__():
	try:
		fp = open("auto_ip.inf", 'r')
		lines = fp.readlines()
		for line in lines:
			if "ip" in line:
				ip = line.replace(' ', '').replace('\n','').split(':')[1]

			elif "port" in line:
				port = line.replace(' ', '').replace('\n','').split(':')[1]	

			elif "remember_status" in line:
				remember_status = line.replace(' ', '').replace('\n','').split(':')[1]	
		fp.close()
		return ip, port, int(remember_status)
	except IOError:
		return -1

def __write_auto_inf__(ip=None, port=None, rem_status=None):
	fp = open("auto_ip.inf", 'w')
	string = "ip: %s \nport: %s\nremember_status: %s\n" %(ip, port, rem_status)  
	fp.write(string)
	fp.close()

class LoginScreen(QtWidgets.QDialog, Ui_Login_screen):
	"""Login Screen

	To creat a Graphical User Interface, inherit from Ui_Login_screen. And define functions
	that use for the control.

	Attributes:
		none
	"""
	def __init__(self):
		global autologin
		global HOST,PORT

		info = __read_auto_inf__()
		if info == -1:
			HOST = ''
			PORT = ''
			autologin = -1
		else:
			HOST = info[0]
			PORT = info[1]
			autologin = info[2]
	
		QtWidgets.QDialog.__init__(self)	
		Ui_Login_screen.__init__(self)
		self.setupUi(self)
		self.setWindowTitle("Log In - SunFounder PiCar-V Client")
		# Check value of autologin, if True, set text of host line edit with saved host
		if autologin == 1:
			self.lEd_host.setText(HOST)
			self.label_Error.setText("")
			self.pBtn_checkbox.setStyleSheet("border-image: url(./images/check2.png);")
		# not autologin, line edit will fill with blank
		else:
			self.lEd_host.setText("")
			self.label_Error.setText("")
			self.pBtn_checkbox.setStyleSheet("border-image: url(./images/uncheck1.png);")
		# connect the signal and slot
		self.pBtn_checkbox.clicked.connect(self.on_pBtn_checkbox_clicked)

	def on_pBtn_login_clicked(self):
		"""Slot for signal that Login button clicked

		The login button clicked, this function will run. This function use for logining,
		first, check the length of text in line edit, if ok, saved them to variable HOST 
		and PORT, after that, call function connection_ok(), if get 'OK' return, login 
		succeed, close this screen, show running screen

		Args:
			None

		Returns:
			if login succeed return True
			else return False

		"""
		global HOST,PORT
		# check whether the length of input host and port is allowable
		if 7<len(self.lEd_host.text())<16 :
			HOST = self.lEd_host.text()
			PORT = self.lEd_port.text()
			__reflash_url__()
			self.label_Error.setText("Connecting....")
			
			# check whethe server is connected
			if connection_ok() == True: # request respon 'OK', connected
				if autologin == 1:	# autologin checked, record HOST
					HOST = self.lEd_host.text()
					PORT = self.lEd_port.text()
				else:
					self.lEd_host.setText("")
					self.label_Error.setText("")

				__write_auto_inf__(HOST, PORT, autologin)
				self.label_Error.setText("")
				# login succeed, login1 screen close, running screen show, function start_stream() run
					
				login1.close()
				running1.start_stream()
				running1.show()
				return True
			# connected failed, set the information
			else:
				self.label_Error.setText("Failed to connect")
				return False
		# the input length in line edit not allowable 
		else:
			self.label_Error.setText("Host or port not correct")
			return False
		print ("on_pBtn_login_clicked", HOST,PORT,autologin,"\n")
	
	# pressed and released, each set their stylesheet, so it make a feedback of press
	
	def on_pBtn_checkbox_clicked(self):
		"""Slot for checkbox button clicked signal

		The checkbox button clicked, this function will run. This function use for autologin, 
		when clicked, the status of autologin(check or not check) will changed, if autologin 
		checked, save HOST and PORT, and next show this screen, line edit will auto fill with 
		the saved value

		Args:
			None

		#TODO: save the HOST and PORT to file in local
		"""
		global autologin
		# when clicked checkbox button, change value of various autologin
		autologin = -autologin
		print('autolongin = %s'%autologin) 
		if autologin == 1:
			# the checked picture
			self.pBtn_checkbox.setStyleSheet("border-image: url(./images/check2.png);")
		else:
			# the unchecked picture
			self.pBtn_checkbox.setStyleSheet("border-image: url(./images/uncheck1.png);")
		print ("on_pBtn_checkbox_clicked", HOST,autologin)

class RunningScreen(QtWidgets.QDialog, Ui_Running_screen):
	"""Running Screen

	To creat a Graphical User Interface, inherit from Ui_Running_screen. And define functions
	that use for the control.

	Attributes:
		TIMEOUT, how long it time up for QTimer, using to reflash the frame 
	"""
	TIMEOUT = 50
	LEVEL1_SPEED = 40
	LEVEL5_SPEED = 100

	LEVEL2_SPEED = int((LEVEL5_SPEED - LEVEL1_SPEED) / 4 * 1 + LEVEL1_SPEED)
	LEVEL3_SPEED = int((LEVEL5_SPEED - LEVEL1_SPEED) / 4 * 2 + LEVEL1_SPEED)
	LEVEL4_SPEED = int((LEVEL5_SPEED - LEVEL1_SPEED) / 4 * 3 + LEVEL1_SPEED)

	LEVEL_SPEED = [0, LEVEL1_SPEED, LEVEL2_SPEED, LEVEL3_SPEED, LEVEL4_SPEED, LEVEL5_SPEED]


	def __init__(self):
		QtWidgets.QDialog.__init__(self)	
		Ui_Running_screen.__init__(self)
		self.setupUi(self)

		self.speed_level = 0
		# when init, no level button has been pressed, self.speed_level = 0
		self.level_btn_show(self.speed_level)
		self.setWindowTitle("Operation - SunFounder PiCar-V Client")
		self.btn_back.setStyleSheet("border-image: url(./images/back_unpressed.png);")
		self.btn_setting.setStyleSheet("border-image: url(./images/settings_unpressed.png);")
	
	def start_stream(self):
		"""Start to receive the stream

		With this function called, the QTimer start timing, while time up, call reflash_frame() function, 
		the frame will be reflashed. 

		Args:
			None
		"""
		# creat an object queryImage with the HOST  
		self.queryImage = QueryImage(HOST)
		self.timer = QTimer(timeout=self.reflash_frame)  # Qt timer, time up, run reflash_frame()
		self.timer.start(RunningScreen.TIMEOUT)  # start timer
		# init the position 
		
		run_action('camready')
	
	def stop_stream(self):
		self.timer.stop()		# stop timer, so the receive of stream also stop

	def transToPixmap(self):
		"""Convert the stream data to pixmap data

		First save the queryImage() data, and then creat an object pixmap, call built-in function 
		pixmap.loadFromData(data) to store the data

		Args:
			None

		return:
			pixmap, the object of QPixmap()
			if no data, return None
		"""
		# use the buile-in function to query image from http, and save in data
		data = self.queryImage.queryImage()
		if not data:
			return None
		pixmap = QPixmap()
		# get pixmap type data from http type data
		pixmap.loadFromData(data)
		return pixmap

	def reflash_frame(self):
		"""Reflash frame on widget label_snapshot 

		Use the return value of transToPixmap() to reflash the frame on widget label_snapshot 

		Args:
			None
		"""
		# this pixmap is the received and converted picture
		pixmap = self.transToPixmap()
		if pixmap:
			# show the pixmap on widget label_snapshot
			self.label_snapshot.setPixmap(pixmap)
		else :
			print ("frame lost")
	
	def level_btn_show(self,speed_level):
		"""Reflash the view of level_btn

		Whit this function call, all level_btns change to a unpressed status except one that be clicked recently

		Args:
			1~5, the argument speed_level  means the button be clicked recently
		"""
		# set all buttons stylesheet unpressed
		self.level1.setStyleSheet("border-image: url(./images/speed_level_1_unpressed.png);")
		self.level2.setStyleSheet("border-image: url(./images/speed_level_2_unpressed.png);")
		self.level3.setStyleSheet("border-image: url(./images/speed_level_3_unpressed.png);")
		self.level4.setStyleSheet("border-image: url(./images/speed_level_4_unpressed.png);")
		self.level5.setStyleSheet("border-image: url(./images/speed_level_5_unpressed.png);")
		if   speed_level == 1:		# level 1 button is pressed
			self.level1.setStyleSheet("border-image: url(./images/speed_level_1_pressed.png);")
		elif speed_level == 2:		# level 2 button is pressed
			self.level2.setStyleSheet("border-image: url(./images/speed_level_2_pressed.png);")
		elif speed_level == 3:		# level 3 button is pressed
			self.level3.setStyleSheet("border-image: url(./images/speed_level_3_pressed.png);")	
		elif speed_level == 4:		# level 4 button is pressed
			self.level4.setStyleSheet("border-image: url(./images/speed_level_4_pressed.png);")	
		elif speed_level == 5:		# level 5 button is pressed
			self.level5.setStyleSheet("border-image: url(./images/speed_level_5_pressed.png);")	

	def set_speed_level(self, speed):		# set speed to server 
		run_speed(speed)

	
	def on_level1_clicked(self):
		"""Slot for signal that level1 button clicked

		The level1 button clicked, this function will run. Call function level_btn_show() 
		and function set_speed_level(), level1 set argument '20' to set_speed_level()

		"""
		self.speed_level = 1
		self.level_btn_show(self.speed_level)
		self.set_speed_level(str(self.LEVEL_SPEED[self.speed_level]))				# level 1, speed 20
	
	def on_level2_clicked(self):
		self.speed_level = 2
		self.level_btn_show(self.speed_level)
		self.set_speed_level(str(self.LEVEL_SPEED[self.speed_level]))				# level 2, speed 40
	
	def on_level3_clicked(self):
		self.speed_level = 3
		self.level_btn_show(self.speed_level)	
		self.set_speed_level(str(self.LEVEL_SPEED[self.speed_level]))				# level 3, speed 60

	def on_level4_clicked(self):
		self.speed_level = 4
		self.level_btn_show(self.speed_level)			
		self.set_speed_level(str(self.LEVEL_SPEED[self.speed_level]))				# level 4, speed 80

	def on_level5_clicked(self):
		self.speed_level = 5
		self.level_btn_show(self.speed_level)
		self.set_speed_level(str(self.LEVEL_SPEED[self.speed_level]))				# level 5, speed 100

	def on_btn_back_pressed(self):
		self.btn_back.setStyleSheet("border-image: url(./images/back_pressed.png);")
	def on_btn_back_released(self):
		self.btn_back.setStyleSheet("border-image: url(./images/back_unpressed.png);")
	def on_btn_back_clicked(self):
		"""Slot for signal that back button clicked

		The back button clicked, this function will run. Close this screen and stop 
		stream receive, show login screen 

		"""
		self.close()
		# close this screen, stop receiving the stream
		self.stop_stream()
		login1.show()

	def on_btn_setting_pressed(self):
		self.btn_setting.setStyleSheet("border-image: url(./images/settings_pressed.png);")
	def on_btn_setting_released(self):
		self.btn_setting.setStyleSheet("border-image: url(./images/settings_unpressed.png);")
	def on_btn_setting_clicked(self):
		"""Slot for signal that setting button clicked

		The setting button clicked, this function will run. Close this screen and show setting screen 

		"""
		self.btn_back.setStyleSheet("border-image: url(./images/back_unpressed.png);")
		self.close()
		
		

class QueryImage:
	"""Query Image
	
	Query images form http. eg: queryImage = QueryImage(HOST)

	Attributes:
		host, port. Port default 8080, post need to set when creat a new object

	"""
	def __init__(self, host, port=8080, argv="/?action=snapshot"):
		# default port 8080, the same as mjpg-streamer server
		self.host = host
		self.port = port
		self.argv = argv
	
	def queryImage(self):
		"""Query Image

		Query images form http.eg:data = queryImage.queryImage()

		Args:
			None

		Return:
			returnmsg.read(), http response data
		"""
		http_data = http.client.HTTPConnection(self.host, self.port)
		http_data.putrequest('GET', self.argv)
		http_data.putheader('Host', self.host)
		http_data.putheader('User-agent', 'python-http.client')
		http_data.putheader('Content-type', 'image/jpeg')
		http_data.endheaders()
		returnmsg = http_data.getresponse()

		return returnmsg.read()

def connection_ok():
	"""Check whetcher connection is ok

	Post a request to server, if connection ok, server will return http response 'ok' 

	Args:
		none

	Returns:
		if connection ok, return True
		if connection not ok, return False
	
	Raises:
		none
	"""
	cmd = 'connection_test'
	url = BASE_URL + cmd + "/"
	print('url: %s'% url)
	# if server find there is 'connection_test' in request url, server will response 'Ok'
	try:
		r=requests.get(url)
		if r.text == 'OK':
			return True
	except:
		return False

def __request__(url, times=10):
	for x in range(times):
		try:
			requests.get(url)
			return 0
		except :
			print("Connection error, try again")
	print("Abort")
	return -1

def run_action(cmd):
	"""Ask server to do sth, use in running mode

	Post requests to server, server will do what client want to do according to the url.
	This function for running mode

	Args:
		# ============== Back wheels =============
		'bwready' | 'forward' | 'backward' | 'stop'

		# ============== Front wheels =============
		'fwready' | 'fwleft' | 'fwright' |  'fwstraight'

		# ================ Camera =================
		'camready' | 'camleft' | 'camright' | 'camup' | 'camdown'
	"""
	# set the url include action information
	url = BASE_URL + 'run/?action=' + cmd
	print('url: %s'% url)
	# post request with url 
	__request__(url)

def run_speed(speed):
	"""Ask server to set speed, use in running mode

	Post requests to server, server will set speed according to the url.
	This function for running mode.

	Args:
		'0'~'100'
	"""
	# Set set-speed url
	url = BASE_URL + 'run/?speed=' + speed
	print('url: %s'% url)
	# Set speed
	__request__(url)

def cali_action(cmd):
	"""Ask server to do sth, use in calibration mode

	Post requests to server, server will do what client want to do according to the url.
	This function for calibration mode

	Args:
		# ============== Back wheels =============
		'bwcali' | 'bwcalileft' | 'bwcaliright' | 'bwcaliok'

		# ============== Front wheels =============
		'fwcali' | 'fwcalileft' | 'fwcaliright' |  'fwcaliok'

		# ================ Camera =================
		'camcali' | 'camcaliup' | 'camcalidown' | 'camcalileft' | 'camright' | 'camcaliok' 

	"""
	# set the url include cali information
	url = BASE_URL + 'cali/?action=' + cmd
	print('url: %s'% url)
	# post request with url 
	__request__(url)

def main():
	app = QtWidgets.QApplication(sys.argv)
	
	# creat objects 
	login1 = LoginScreen()
	running1 = RunningScreen()	
	
	

	# Show object login1
	login1.show()

	print ("All done")
	# Wait to exit python if there is a exec_() signal
	sys.exit(app.exec_())


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	
	# creat objects 
	login1 = LoginScreen()
	running1 = RunningScreen()	
	
	

	# Show object login1
	login1.show()

	print ("All done")
	# Wait to exit python if there is a exec_() signal
	sys.exit(app.exec_())

