#!/usr/bin/env python
# Python
import sys, os
import pygame
import datetime
from collections import defaultdict

# PyGame Constants
from pygame.locals import *
from pygame.color import THECOLORS

class GameDisplay:
	def __init__(self, screen_tuple_px):
		self.width_px = screen_tuple_px[0]
		self.height_px = screen_tuple_px[1]
		self.left_m = 0.0
		self.right_m = env.m_from_px(self.width_px)
		self.top_m = 0.0
		self.bottom_m = env.m_from_px(self.height_px)
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
	def __init__(self, color=THECOLORS["white"], left_px=10, top_px=400, width_px=26, height_px=98, density=600.0, v_mps=[1,1]):

		self.color = color

		#set dimensions, weight and center
		self.height_px = height_px        
		self.top_px = top_px
		self.width_px  = width_px
		self.width_m = env.m_from_px(width_px)
		self.halfwidth_m = self.width_m/2
		self.height_m = env.m_from_px(width_px)
		self.halfheight_m = self.height_m/2
		self.density_kgpm2 = density
		self.m_kg = self.height_m * self.width_m * self.density_kgpm2
		
		# Initialize the position and speed of the car. These are affected by the
		# physics calcs in the Track.
		self.center_m = [env.m_from_px(left_px) + (self.halfwidth_m), env.m_from_px(top_px) + (self.halfheight_m)]
		self.v_mps = v_mps
		
		air_track.objCount += 1
		self.name = air_track.objCount
		# Create a rectangle object based on these dimensions
		# Left: distance from the left edge of the screen in px.
		# Top:  distance from the top  edge of the screen in px.
		self.rect = pygame.Rect(left_px, self.top_px, self.width_px, self.height_px)
		
	def draw_obj(self):
		# Update the pixel position of the car's rectangle object to match the value
		# controlled by the physics calculations.
		print(env.px_from_m(self.center_m[0]))
		self.rect.centerx = env.px_from_m( self.center_m[0])
		self.rect.centery = env.px_from_m( self.center_m[1])
		# Draw the main rectangle.
		pygame.draw.rect(game_window.surface, self.color, self.rect)
		
class AirTrack:
	def __init__(self):
		# Initialize the list of cars.
		self.objs = []
		self.objCount = 0
		self.coef_wall_bounce = 0.90
		self.g_mps2 = 9.8/20.0
		
	def update_SpeedandPosition(self, obj, dt_s):
		# Calculate the new physical car position
		obj_forces_N = (0,(obj.m_kg * self.g_mps2))
		obj_acc_mps2 = [(obj_forces_N[0] / obj.m_kg), (obj_forces_N[1] / obj.m_kg)]
		v_final_mps = [obj.v_mps[0] + (obj_acc_mps2[0] * dt_s), obj.v_mps[1] + (obj_acc_mps2[1] * dt_s)]
		v_avg_mps = [(obj.v_mps[0] + v_final_mps[0])/2.0, (obj.v_mps[1] + v_final_mps[1])/2.0]
		obj.center_m = [obj.center_m[0] + (obj.v_mps[0] * dt_s), obj.center_m[1] + (obj.v_mps[1] * dt_s)]
		obj.v_mps = v_final_mps
		
	def check_collisions(self):
		for obj in self.objs:
			if (((obj.center_m[0] - obj.halfwidth_m) < game_window.left_m) or ((obj.center_m[0] + obj.halfwidth_m) > game_window.right_m)):
				self.wall_penetrations(obj)
				obj.v_mps[0] = -obj.v_mps[0] * self.coef_wall_bounce
			elif (((obj.center_m[1] - obj.halfwidth_m) < game_window.top_m) or ((obj.center_m[1] + obj.halfwidth_m) > game_window.bottom_m)):
				self.wall_penetrations(obj)
				obj.v_mps[1] = -obj.v_mps[1] * self.coef_wall_bounce	
				
	def wall_penetrations(self, obj):
		penetration_left_x_m = game_window.left_m - (obj.center_m[0] - obj.halfwidth_m)
		penetration_right_x_m = (obj.center_m[0] + obj.halfwidth_m) - game_window.right_m
		penetration_top_y_m = game_window.top_m - (obj.center_m[1] + obj.halfheight_m)
		penetration_bottom_y_m = (obj.center_m[1] + obj.halfheight_m) - game_window.bottom_m
		if penetration_left_x_m > 0:
			obj.center_m[0] += 2 * penetration_left_x_m
		elif penetration_right_x_m > 0:
			obj.center_m[0] -= 2 * penetration_right_x_m
		elif penetration_top_y_m > 0:
			obj.center_m[1] += 2 * penetration_top_y_m
		elif penetration_bottom_y_m > 0:
			obj.center_m[1] -= 2 * penetration_bottom_y_m
			
	def make_obj(self, color, l_px, t_px, s_mps):
		self.objs.append( PhysObj(color, left_px = l_px, top_px = t_px, v_mps = s_mps))
		
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
	air_track.make_obj( THECOLORS["white"], 450, 200, [0,0])
	air_track.make_obj( THECOLORS["red"], 400, 200, [-.1,0])
	air_track.make_obj( THECOLORS["blue"], 500, 200, [.1,0])
	
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
			
		air_track.check_collisions()
		
		for obj in air_track.objs:
			obj.draw_obj()
		
		time_s += dt_s
		pygame.display.flip()
		
main()