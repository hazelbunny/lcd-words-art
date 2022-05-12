import RPi.GPIO
import sys
from PIL import Image
import random as r
sys.path.append("../../")
from gfxlcd.driver.ili9486.spi import SPI
from gfxlcd.driver.ili9486.ili9486 import ILI9486
RPi.GPIO.setwarnings(False)
RPi.GPIO.setmode(RPi.GPIO.BCM)
from time import sleep
from math import sqrt

from colorsys import hls_to_rgb

def htr(h,s,v):
	return(tuple(round(i*255) for i in hls_to_rgb(h/360,s/100,v/100)))


drv = SPI()
lcd_tft = ILI9486(320, 480, drv)
buffer = (35,480,15,310)
lcd_tft.rotation = 270
lcd_tft.init()

def print_image(image, lcd):
	size_x,size_y=image.size
	x=r.randint(buffer[0],buffer[1]-size_x)
	y=r.randint(buffer[2],buffer[3]-size_y)
	lcd.draw_image(x, y, image)

def print_words(phrase, lcd):
	HLS=r.randint(0,360),28+counter*6,52+counter*4
	wordlist = phrase_to_array(phrase)
	x = r.randint(buffer[0],buffer[1]-200)
	y = r.randint(buffer[2],buffer[3]-40)
	xmod,ymod=r.randint(0,20),0
	for word in wordlist:
		drop_shadow(x+xmod,y+ymod,word,lcd,HLS)
		if xmod+9*len(word)+1>200:
			xmod=r.randint(0,20)
			ymod+=9
		else:
			xmod+=9*(len(word)+1)

def drop_shadow(x,y,word,lcd,HLS):
	HLS_dark=(HLS[0],HLS[1]-28,HLS[2])
	xc=x
	for letter in word:
		lcd.color=htr(*HLS_dark)
		lcd_tft.draw_text(xc,y,letter)
		lcd.color=htr(*HLS)
		lcd_tft.draw_text(xc-1,y-1,letter)
		xc+=9
		glitch_area(lcd,counter,counter*2)

def phrase_to_array(phrase):
	array = []
	current_word = ""
	for letter in phrase:
		if letter == " " or letter == "\n":
			array.append(current_word)
			current_word=""
		else:
			current_word+=letter
	return array

def glitch_area(lcd,density,probability=100):
	o=False
	if r.randint(0,100)>=probability:
		return
	if density == 5000:
		o=True
		max=100
	if density > 500:
		max = 200
	if density > 50:
		max = 100
	else:
		max = 20
	size_x,size_y=r.randint(10,max),r.randint(10,max)
	x=r.randint(buffer[0],buffer[1]-size_x)
	y=r.randint(buffer[2],buffer[3]-size_y)
	if o:
		x,size_x,y,size_y=buffer[0],buffer[1]-buffer[0],buffer[2],buffer[3]-buffer[2]
	for i in range(0,density):
		if not o:
			lcd.color=(r.randint(170,255),r.randint(170,255),r.randint(170,255))
			lcd.draw_pixel(x+r.randint(0,size_x),y+r.randint(0,size_y))
			return
		if o:
			R,G,B=htr(r.randint(0,360),r.randint(5,25),r.randint(70,100))
			lcd.background_color=(R,G,B)
			rx=x+r.randint(0,size_x)
			ry=y+r.randint(0,size_y)
			ry2=ry+r.randint(0,9)
			lcd.fill_rect(rx,ry,rx,ry2)
#for i in range(0,10):
#	glitch_area(lcd_tft,r.randint(50,100))
words_array = []
with open("musings.txt") as source:
	for line in source:
		words_array.append(line)


global counter
counter = 0
meta_counter=0
_LIVE = True
while True:
	if _LIVE:
		_old_source=words_array
		words_array=[]
		try:
			with open("musings.txt") as source:
				for line in source:
					words_array.append(line)
		except:
			words=_old_source
	word = r.choice(words_array)
	if word[0]=="#":
		pass
	elif word[0]=="!":
		image_file = Image.open(line.strip("!"))
		print_image(image_file,lcd_tft)
		counter -=1
	else:
		print_words(word,lcd_tft)
		counter+= 1
	if counter == 12:
		glitch_area(lcd_tft,5000)
		counter=0
		meta_counter+=1
	if meta_counter==3:
		lcd_tft.init()
		meta_counter=0
