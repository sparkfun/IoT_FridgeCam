import RPi.GPIO as GPIO
import time
import serial
import subprocess
import gmail
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os

USERNAME = "000drycreek@gmail.com"
PASSWORD = "IHeartJeeping69"

port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=3.0)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

hi_limit = 24
lo_limit = 23

GPIO.setup(hi_limit, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(lo_limit, GPIO.IN, GPIO.PUD_UP)

def takePix():
	
	port.write("1r7\r")
	while GPIO.input(hi_limit) == True:
		x=0
	port.write("1r0\r")
	status = subprocess.call("raspistill -o top.jpg", shell=True)
	status = subprocess.call("convert top.jpg -resize 500x500 top.jpg", shell=True)
	port.write("1f5\r")
	time.sleep(3)
	port.write("1f0\r")
	status = subprocess.call("raspistill -o mid.jpg", shell=True)
	status = subprocess.call("convert mid.jpg -resize 500x500 mid.jpg", shell=True)
	port.write("1f5\r")
	while GPIO.input(lo_limit) == True:
		x=0
	port.write("1f0\r")
	status = subprocess.call("raspistill -o bot.jpg", shell=True)
	status = subprocess.call("convert bot.jpg -resize 500x500 bot.jpg", shell=True)
	port.write("1r7\r")
	while GPIO.input(hi_limit) == True:
		x=0
	port.write("1r0\r")

def sendMail(to, subject, text, files=[]):
    assert type(to)==list
    assert type(files)==list

    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    
    msg.attach( MIMEText(text) )

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % os.path.basename(file))
        msg.attach(part)

	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo_or_helo_if_needed()
	server.starttls()
	server.ehlo_or_helo_if_needed()
	server.login(USERNAME,PASSWORD)
	server.sendmail(USERNAME, to, msg.as_string())
	server.quit()
	

while True:

	g = gmail.login(USERNAME, PASSWORD)
	unread = g.inbox().mail(unread=True)
	if unread:
		unread[0].fetch()
		message = unread[0].body
		target = unread[0].fr
		print target
		print message
		if "What's in the fridge?" in message:
			takePix()
			sendMail( [target], 
				"Fridge Report",
				"Take Stock",
				["top.jpg","mid.jpg","bot.jpg"] )
		unread[0].read()
	else:
		print("No Unread Messages")
	time.sleep(30)



