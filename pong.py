import pygame
import random
from time import sleep

from fontcontroller import FontController
from rendertext import RenderText
from AiController import AiController

black = (0,0,0)
white = (255,255,255)
puck_size = 5

def draw_text(screen, rendertext, x, y, text):
	"""
	Draw text to the screen. 'screen' should be a valid pygame surface.
	"""
	rendertext.update_x(x)
	rendertext.update_y(y)
	rendertext.update_text(text)
	rendertext.draw(screen)

def draw_median(screen, winx, winy):
	global white

	midpoint = int(winx//2)
	for i in range(0,winy,20):
		pygame.draw.rect(screen, white, (midpoint, i+10, 5, 10))

def draw_puck(screen, x, y):
	global white
	global puck_size

	pygame.draw.rect(screen, white, (x, y, puck_size, puck_size))

def draw_player(screen, pos_vec, player_width, player_height):
	global white
	pygame.draw.rect(screen, white, (pos_vec.x, pos_vec.y, player_width, player_height))

def check_puck_wall_collision(puck_pos_vec, winx, winy):
	puckx, pucky = puck_pos_vec.x, puck_pos_vec.y

	doreflect = pucky <= 0 or pucky >= winy

	did_collide_left = (puckx <= winx//2) and (puckx <= 0 or doreflect)
	did_collide_right = (puckx > winx//2) and (puckx > winx or doreflect)

	did_collide = did_collide_left or did_collide_right

	direction = -1
	if did_collide:
		direction = 0 if did_collide_left else did_collide_right

	return [did_collide, direction, doreflect]

def check_player_collision(player_pos_vec, puck_pos_vec, player_width, player_height):
	global puck_size

	puckx, pucky = puck_pos_vec.x, puck_pos_vec.y
	playerx, playery = player_pos_vec.x, player_pos_vec.y

	puckx_collide = ((puckx + puck_size) >= playerx and puckx <= (playerx + player_width))
	pucky_collide = ((pucky + puck_size) >= playery and pucky <= (playery + player_height))

	return puckx_collide and pucky_collide

def reset_puck(player_pos, puck_pos, puck_velocity, winx, winy):
	puck_pos = pygame.Vector2(winx//2, winy//2)

	puck_velocity = player_pos - puck_pos
	puck_velocity.normalize_ip()

	# Starting puck speed, going towards the right player
	puck_velocity.scale_to_length(2)

	return [puck_pos, puck_velocity]

def main(winx=400, winy=600):
	global black
	global white

	pygame.display.init()

	screen = pygame.display.set_mode((winx, winy))

	player_width = 10
	player_height = 50

	font_controller = FontController()
	ai_controller = AiController(winx, winy, player_width, player_height)

	clock = pygame.time.Clock()

	done = False
	
	player1_score = 0
	player2_score = 0
	player1_score_rendertext = RenderText(font_controller, white, black)
	player2_score_rendertext = RenderText(font_controller, white, black)

	quart_screen = winx//4

	make_left_player_pos = lambda: pygame.Vector2(quart_screen, random.randrange(player_height, winy-player_height))
	make_right_player_pos = lambda: pygame.Vector2(winx-quart_screen, random.randrange(player_height, winy-player_height))

	left_player_pos = make_left_player_pos()
	right_player_pos = make_right_player_pos()

	# Make the puck vectors
	puck_pos = pygame.Vector2(winx//2, winy//2)
	puck_velocity = pygame.Vector2(0, 0)
	puck_pos, puck_velocity = reset_puck(right_player_pos, puck_pos, puck_velocity, winx, winy)

	puck_dir = 1
	player_speed = 15

	while not done:
		puck_pos.x += puck_velocity.x
		puck_pos.y += puck_velocity.y

		ai_controller.run(puck_pos, puck_dir, right_player_pos)

		left_player_did_collide = check_player_collision(left_player_pos, puck_pos, player_width, player_height)
		right_player_did_collide = check_player_collision(right_player_pos, puck_pos, player_width, player_height)

		if left_player_did_collide:
			# print("left_player_did_collide")
			puck_velocity.reflect_ip(pygame.Vector2(1,0))

			pvl = int(puck_velocity.length())
			puck_velocity.normalize_ip()
			puck_velocity.scale_to_length(max(pvl, random.randint(pvl, pvl + 1)))

			# Get rid of jank collision bug, by hand
			puck_pos.x = left_player_pos.x
			puck_pos.x += 10

			puck_dir = 1

		if right_player_did_collide:
			# print("right_player_did_collide")
			puck_velocity.reflect_ip(pygame.Vector2(1,0))
			
			pvl = int(puck_velocity.length())
			puck_velocity.normalize_ip()
			puck_velocity.scale_to_length(max(pvl, random.randint(pvl, pvl + 1)))

			# Get rid of jank collision bug, by hand
			puck_pos.x = right_player_pos.x
			puck_pos.x -= 10

			puck_dir = -1

		cws = check_puck_wall_collision(puck_pos, winx, winy)
		if cws[0]:
			doreflect = cws[2]

			# Bounce the puck of the top/bottom wall
			if doreflect:
				puck_velocity.reflect_ip(pygame.Vector2(0,1))
			else: # we hit a back wall of a player
				if cws[1] == 0:
					player2_score += 1
				elif cws[1] == 1:
					player1_score += 1
				pd = left_player_pos if puck_dir == -1 else right_player_pos
				puck_pos, puck_velocity = reset_puck(pd, puck_pos, puck_velocity, winx, winy)

		events = pygame.event.get()
		for e in events:
			if e.type == pygame.MOUSEBUTTONDOWN:
				if e.button == 4:
					if left_player_pos.y >= 10:
						left_player_pos.y -= player_speed
				if e.button == 5:
					if (left_player_pos.y + player_height) <= (winy - 10):
						left_player_pos.y += player_speed
			if e.type == pygame.KEYDOWN:
				if e.key == pygame.K_ESCAPE:
					done = True

		screen.fill(black)

		draw_text(screen, player1_score_rendertext, quart_screen, 50, str(player1_score))
		draw_text(screen, player2_score_rendertext, winx-quart_screen, 50, str(player2_score))

		draw_median(screen, winx, winy)

		draw_player(screen, left_player_pos, player_width, player_height)
		draw_player(screen, right_player_pos, player_width, player_height)

		draw_puck(screen, puck_pos.x, puck_pos.y)

		pygame.display.flip()
		clock.tick(60)

	pygame.display.quit()

if __name__ == "__main__":
	main()
