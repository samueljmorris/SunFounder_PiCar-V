#!/usr/bin/env python
'''
**********************************************************************
* Filename    : camera.py
* Description : A module to move the camera's up, down, left, right.
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-13    New release
**********************************************************************
'''

from picar.SunFounder_PCA9685 import Servo
import time
from picar import filedb

class Camera(object):
	'''Camera movement control class'''
	pan_channel = 2			# Pan servo channel
	tilt_channel = 1		# Tilt servo channel

	READY_PAN = 90			# Ready position angle
	READY_TILT = 90			# Ready position angle
	CALI_PAN = 90			# Calibration position angle
	CALI_TILT = 90			# Calibration position angle

	CAMERA_DELAY = 0.05 # Pan/Tilt speed. Acceptable range: 0.01 - 0.05
	PAN_STEP = 15				# Pan step = 5 degree
	TILT_STEP = 10			# Tilt step = 5 degree

	TILT_MAX = 100 # Maximum safe tilt angle
	TILT_MIN = 50 # Minimum safe tilt angle

	PAN_MAX = 170 # Maximum safe pan angle
	PAN_MIN = 10 # Minimum safe pan angle

	keep_tilting = True # Class attribute to continue camera tilt loop
	keep_panning = True # Class attribute to continue camera pan loop

	_DEBUG = False
	_DEBUG_INFO = 'DEBUG "camera.py":'

	def __init__(self, debug=False, bus_number=1, db="config"):
		''' Init the servo channel '''
		self.db = filedb.fileDB(db=db)
		self.pan_offset = int(self.db.get('pan_offset', default_value=0))
		self.tilt_offset = int(self.db.get('tilt_offset', default_value=0))

		self.pan_servo = Servo.Servo(self.pan_channel, bus_number=bus_number, offset=self.pan_offset)
		self.tilt_servo = Servo.Servo(self.tilt_channel, bus_number=bus_number, offset=self.tilt_offset)
		self.debug = debug
		if self._DEBUG:
			print self._DEBUG_INFO, 'Pan servo channel:', self.pan_channel
			print self._DEBUG_INFO, 'Tilt servo channel:', self.tilt_channel
			print self._DEBUG_INFO, 'Pan offset value:', self.pan_offset
			print self._DEBUG_INFO, 'Tilt offset value:', self.tilt_offset

		self.current_pan = 0
		self.current_tilt = 0
		self.ready()

	def safe_plus(self, variable, plus_value):
		''' Plus angle safely with no over ranges '''
		variable += plus_value
		if variable > 180:
			variable = 180
		if variable < 0:
			variable = 0
		return variable

	def turn_left(self, step=PAN_STEP):
		''' Control the pan servo to make the camera turning left '''
		if self._DEBUG:
			print self._DEBUG_INFO, 'Turn left at step:', step
		self.current_pan = self.safe_plus(self.current_pan, step)
		self.pan_servo.write(self.current_pan)

	def turn_right(self, step=PAN_STEP):
		''' Control the pan servo to make the camera turning right '''
		if self._DEBUG:
			print self._DEBUG_INFO, 'Turn right at step:', step
		self.current_pan = self.safe_plus(self.current_pan, -step)
		self.pan_servo.write(self.current_pan)

	def turn_up(self, step=TILT_STEP):
		''' Control the tilt servo to make the camera turning up '''
		if self._DEBUG:
			print self._DEBUG_INFO, 'Turn up at step:', step
		self.current_tilt = self.safe_plus(self.current_tilt, step)
		self.tilt_servo.write(self.current_tilt)

	def turn_down(self, step=TILT_STEP):
		'''Control the tilt servo to make the camera turning down'''
		if self._DEBUG:
			print self._DEBUG_INFO, 'Turn down at step:', step
		self.current_tilt = self.safe_plus(self.current_tilt, -step)
		self.tilt_servo.write(self.current_tilt)

	def stop_tilting(self):
		self.keep_tilting = False
	
	def stop_panning(self):
		self.keep_panning = False

	def smooth_tilt(self, tilt_direction, delay=CAMERA_DELAY):
		'''Control tilt servo to write the camera to ready position'''
		print self._DEBUG_INFO, 'TILT_MAX:', self.TILT_MAX
		print self._DEBUG_INFO, 'TILT_MIN:', self.TILT_MIN
		if tilt_direction == "right":
			tilt_diff = self.current_tilt - self.TILT_MAX
			print self._DEBUG_INFO, 'tilt_diff:', tilt_diff
		else:
			tilt_diff = self.current_tilt - self.TILT_MIN
			print self._DEBUG_INFO, 'tilt_diff:', tilt_diff
		while self.keep_tiltning: #check class attribute to continue or not
			if tilt_diff != 0:
				if tilt_direction == "up":
					print self._DEBUG_INFO, 'Tilting up.'
					tilt_diff = self.current_tilt - self.TILT_MAX
					print self._DEBUG_INFO, 'tilt_diff:', tilt_diff
					if tilt_diff < 0:
						self.current_tilt = self.safe_plus(self.current_tilt, 1)
						print self._DEBUG_INFO, 'current_tilt:', self.current_tilt
					else:
						self.current_tilt = self.TILT_MAX
						print self._DEBUG_INFO, 'current_tilt:', self.current_tilt

					self.tilt_servo.write(self.current_tilt)
					time.sleep(delay)
				else:
					print self._DEBUG_INFO, 'Tilting down.'
					tilt_diff = self.current_tilt - self.TILT_MIN
					print self._DEBUG_INFO, 'tilt_diff:', tilt_diff
					if tilt_diff > 0:
						self.current_tilt = self.safe_plus(self.current_tilt, -1)
						print self._DEBUG_INFO, 'current_tilt:', self.current_tilt
					else:
						self.current_tilt = self.TILT_MIN
						print self._DEBUG_INFO, 'current_tilt:', self.current_tilt

					self.tilt_servo.write(self.current_tilt)
					time.sleep(delay)
			else:
				print self._DEBUG_INFO, 'Smooth tilting completed.'
				break


	def smooth_pan(self, pan_direction, delay=CAMERA_DELAY):
		'''Control pan servo to write the camera to ready position'''
		print self._DEBUG_INFO, 'PAN_MAX:', self.PAN_MAX
		print self._DEBUG_INFO, 'PAN_MIN:', self.PAN_MIN
		if pan_direction == "right":
			pan_diff = self.current_pan - self.PAN_MAX
			print self._DEBUG_INFO, 'pan_diff:', pan_diff
		else:
			pan_diff = self.current_pan - self.PAN_MIN
			print self._DEBUG_INFO, 'pan_diff:', pan_diff
		while self.keep_panning: #check class attribute to continue or not
			if pan_diff != 0:
				if pan_direction == "right":
					print self._DEBUG_INFO, 'Panning right.'
					pan_diff = self.current_pan - self.PAN_MAX
					print self._DEBUG_INFO, 'pan_diff:', pan_diff
					if pan_diff < 0:
						self.current_pan = self.safe_plus(self.current_pan, 1)
						print self._DEBUG_INFO, 'current_pan:', self.current_pan
					else:
						self.current_pan = self.PAN_MAX
						print self._DEBUG_INFO, 'current_pan:', self.current_pan

					self.pan_servo.write(self.current_pan)
					time.sleep(delay)
				else:
					print self._DEBUG_INFO, 'Panning left.'
					pan_diff = self.current_pan - self.PAN_MIN
					print self._DEBUG_INFO, 'pan_diff:', pan_diff
					if pan_diff > 0:
						self.current_pan = self.safe_plus(self.current_pan, -1)
						print self._DEBUG_INFO, 'current_pan:', self.current_pan
					else:
						self.current_pan = self.PAN_MIN
						print self._DEBUG_INFO, 'current_pan:', self.current_pan

					self.pan_servo.write(self.current_pan)
					time.sleep(delay)
			else:
				print self._DEBUG_INFO, 'Smooth panning completed.'
				break

	def ready(self):
		''' Set the camera to ready position '''
		if self._DEBUG:
			print self._DEBUG_INFO, 'Turn to "Ready" position'
		self.pan_servo.offset = self.pan_offset
		self.tilt_servo.offset = self.tilt_offset
		self.current_pan = self.READY_PAN
		self.current_tilt = self.READY_TILT
		self.pan_servo.write(self.current_pan)
		self.tilt_servo.write(self.current_tilt)

	def calibration(self):
		''' Control two servo to write the camera to calibration position '''
		if self._DEBUG:
			print self._DEBUG_INFO, 'Turn to "Calibration" position'
		self.pan_servo.write(self.CALI_PAN)
		self.tilt_servo.write(self.CALI_TILT)
		self.cali_pan_offset = self.pan_offset
		self.cali_tilt_offset = self.tilt_offset

	def cali_up(self):
		''' Calibrate the camera to up '''
		self.cali_tilt_offset += 1
		self.tilt_servo.offset = self.cali_tilt_offset
		self.tilt_servo.write(self.CALI_TILT)

	def cali_down(self):
		''' Calibrate the camera to down '''
		self.cali_tilt_offset -= 1
		self.tilt_servo.offset = self.cali_tilt_offset
		self.tilt_servo.write(self.CALI_TILT)

	def cali_left(self):
		''' Calibrate the camera to left '''
		self.cali_pan_offset += 1
		self.pan_servo.offset = self.cali_pan_offset
		self.pan_servo.write(self.CALI_PAN)

	def cali_right(self):
		''' Calibrate the camera to right '''
		self.cali_pan_offset -= 1
		self.pan_servo.offset = self.cali_pan_offset
		self.pan_servo.write(self.CALI_PAN)

	def cali_ok(self):
		''' Save the calibration value '''
		self.pan_offset = self.cali_pan_offset
		self.tilt_offset = self.cali_tilt_offset
		self.db.set('pan_offset', self.pan_offset)
		self.db.set('tilt_offset', self.tilt_offset)

	@property
	def debug(self):
		return self._DEBUG

	@debug.setter
	def debug(self, debug):
		''' Set if debug information shows '''
		if debug in (True, False):
			self._DEBUG = debug
		else:
			raise ValueError('debug must be "True" (Set debug on) or "False" (Set debug off), not "{0}"'.format(debug))

		if self._DEBUG:
			print self._DEBUG_INFO, "Set debug on"
			print self._DEBUG_INFO, "Set pan servo and tilt servo debug on"
			self.pan_servo.debug = True
			self.tilt_servo.debug = True
		else:
			print self._DEBUG_INFO, "Set debug off"
			print self._DEBUG_INFO, "Set pan servo and tilt servo debug off"
			self.pan_servo.debug = False
			self.tilt_servo.debug = False

if __name__ == '__main__':
	camera = Camera()
	try:
		for i in range(0, 36):
			print "pan moving left     ", i
			camera.pan_left()
			time.sleep(camera.CAMERA_DELAY*camera.PAN_STEP)
		for i in range(0, 36):
			print "pan moving right    ", i
			camera.pan_right()
			time.sleep(camera.CAMERA_DELAY*camera.PAN_STEP)
		for i in range(0, 36):
			print "tilt moving up      ", i
			camera.tilt_up()
			time.sleep(camera.CAMERA_DELAY*camera.TILT_STEP)
		for i in range(0, 36):
			print "tilt moving right   ", i
			camera.tilt_down()
			time.sleep(camera.CAMERA_DELAY*camera.TILT_STEP)
		
		print "Camera move to ready position"
		camera.ready()

		print "Camera move to position (0, 0)"
		camera.to_posision(0, 0)
		print "Camera move to position (180, 180)"
		camera.to_posision(180, 180)

		print "Camera move to ready position"
		camera.ready()
	except KeyboardInterrupt:
		camera.ready()
