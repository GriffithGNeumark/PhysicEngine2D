#!/usr/bin/env python
# Python
import sys, os
import pygame
import datetime

# PyGame Constants
from pygame.locals import *
from pygame.color import THECOLORS

class GameDisplay:
	def __init__(self, screen_tuple_px):
		self.width_px = screen_tuple_px[0]
		self.height_px = screen_tuple_px[1]
		self.surface = pygame.display.set_mode(screen_tuple_px)
		self.erase_and_update()
		
	def update_caption(self, title):
		pygame.display.set_caption(title)
		self.caption = title
		
	def erase_and_update(self):
		self.surface.fill(THECOLORS["black"])
		pygame.display.flip()
		
class Environment:
	def __init__(self, length_px, length_m):
		self.px_to_m = length_m/float(length_px)
		self.m_to_px = (float(length_px)/length_m)

	# Convert from meters to pixels
	def px_from_m(self, dx_m):
		return int(round(dx_m * self.m_to_px))

	# Convert from pixels to meters
	def m_from_px(self, dx_px):
		return float(dx_px) * self.px_to_m
			
class PhysObj:
	def __init__(self, color=THECOLORS["white"], left_px=10, top_px=400, width_px=26, height_px=98, speed_mps=(1,1)):

		self.color = color

		self.height_px = height_px        
		self.top_px = top_px
		self.width_px  = width_px
		self.width_m = env.m_from_px(width_px)
		self.height_m = env.m_from_px(width_px)
		
		# Initialize the position and speed of the car. These are affected by the
		# physics calcs in the Track.
		self.center_m = (env.m_from_px(left_px) + (self.width_m/2), env.m_from_px(top_px) + (self.height_m/2))
		self.speed_mps = speed_mps

		# Create a rectangle object based on these dimensions
		# Left: distance from the left edge of the screen in px.
		# Top:  distance from the top  edge of the screen in px.
		self.rect = pygame.Rect(left_px, self.top_px, self.width_px, self.height_px)

	def draw_obj(self):
		# Update the pixel position of the car's rectangle object to match the value
		# controlled by the physics calculations.
		self.rect.centerx = env.px_from_m( self.center_m[0])
		self.rect.centery = env.px_from_m( self.center_m[1])
		# Draw the main rectangle.
		pygame.draw.rect(game_window.surface, self.color, self.rect)
		
class AirTrack:
	def __init__(self):
		# Initialize the list of cars.
		self.objs = []

	def update_SpeedandPosition(self, obj, dt_s):
		# Calculate the new physical car position
		obj.center_m = (obj.center_m[0] + (obj.speed_mps[0] * dt_s), obj.center_m[1] + (obj.speed_mps[1] * dt_s))
		
	def make_obj(self, color, l_px, t_px, s_mps):
		self.objs.append( PhysObj(color, left_px = l_px, top_px = t_px, speed_mps = s_mps))
		
def main():
	#some globals
	global env, game_window, air_track
	
	#Initialize pygame and instance environment and window
	pygame.init()
	window_size_px = window_width_px, window_height_px = (1280, 720)
	env = Environment(window_width_px, 1.5)
	game_window = GameDisplay(window_size_px)

	# Instantiate an air track and add obj
	air_track = AirTrack()
	air_track.make_obj( THECOLORS["white"], 450, 200, (0.1,0.1))
	
	myclock = pygame.time.Clock()
	framerate_limit = 400
	time_s = 0.0
	
	user_done = False
#	for event in pygame.event.get():
#		if (event.type == pygame.QUIT): 
#			return 'quit'
	while not user_done:
		game_window.surface.fill(THECOLORS["black"])
		dt_s = float(myclock.tick(framerate_limit) * 1e-3)
		
		for obj in air_track.objs:
			air_track.update_SpeedandPosition(obj, dt_s)
			
		for obj in air_track.objs:
			obj.draw_obj()
		
		time_s += dt_s
		pygame.display.flip()
		
main()