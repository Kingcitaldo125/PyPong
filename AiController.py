import math
import random

from enum import Enum

class AiStates(Enum):
	IDLE = 1
	MOVING_UP = 2
	MOVING_DOWN = 3

class AiController:
	def __init__(self, winx, winy, playerw, playerh):
		self.state = AiStates.IDLE
		self.playerw = playerw
		self.playerh = playerh
		self.winx = winx
		self.winy = winy

	def move_aimless(self, right_player_pos):
		ran_point = random.randrange(0, self.winy)
		y_distance = abs(right_player_pos.y - ran_point)

		if ran_point < right_player_pos.y:
			right_player_pos.y -= (0.01 * (y_distance//2))
		else:
			right_player_pos.y += (0.01 * (y_distance//2))

	def move_up(self, ballpos, right_player_pos):
		while ballpos.y < (right_player_pos.y + (self.playerh//2)): # midpoint of the right player
			y_distance = abs(right_player_pos.y - ballpos.y)

			if y_distance <= 10:
				break

			if right_player_pos.y <= 0:
				break

			right_player_pos.y -= (0.01 * (y_distance//2))

	def move_down(self, ballpos, right_player_pos):
		while ballpos.y >= (right_player_pos.y + (self.playerh//2)): # midpoint of the right player
			y_distance = abs(right_player_pos.y - ballpos.y)

			if y_distance <= 10:
				break

			if (right_player_pos.y) >= self.winy:
				break

			right_player_pos.y += (0.01 * (y_distance//2))

	def run(self, ballpos, ball_dir, right_player_pos):
		if ball_dir == -1:
			self.move_aimless(right_player_pos)
			return

		if ballpos.y < (right_player_pos.y + self.playerh//2): # midpoint of the right player
			self.move_up(ballpos, right_player_pos)
		elif ballpos.y >= (right_player_pos.y + self.playerh//2): # midpoint of the right player
			self.move_down(ballpos, right_player_pos)
