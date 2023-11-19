import pygame
import random
from time import sleep

from fontcontroller import FontController
from rendertext import RenderText

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

def check_wall_collision(puck_pos_vec, winx, winy):
	puckx, pucky = puck_pos_vec.x, puck_pos_vec.y

	did_collide_left = (puckx <= winx//2) and (puckx <= 0 or pucky <= 0 or pucky >= winy)
	did_collide_right = (puckx > winx//2) and (puckx > winx or pucky <= 0 or pucky >= winy)

	did_collide = did_collide_left or did_collide_right

	direction = -1
	if did_collide:
		direction = 0 if did_collide_left else did_collide_right

	return [did_collide, direction]

def check_player_collision(player_pos_vec, puck_pos_vec, player_width, player_height):
	global puck_size

	puckx, pucky = puck_pos_vec.x, puck_pos_vec.y
	playerx, playery = player_pos_vec.x, player_pos_vec.y

	return ((puckx + puck_size) >= playerx and puckx <= (playerx + player_width)) and (pucky >= playery and pucky <= (playery + player_height))

def reset_puck(right_player_pos, puck_pos, puck_velocity, winx, winy):
	puck_pos = pygame.Vector2(winx//2, winy//2)

	puck_velocity = right_player_pos - puck_pos
	puck_velocity.normalize_ip()

	# Starting puck speed, going towards the right player
	puck_velocity.scale_to_length(1)

	return [puck_pos, puck_velocity]

def main(winx=800, winy=600):
	global black
	global white

	pygame.display.init()

	screen = pygame.display.set_mode((winx, winy))

	font_controller = FontController()

	clock = pygame.time.Clock()

	done = False
	
	player1_score = 0
	player2_score = 0
	player1_score_rendertext = RenderText(font_controller, white, black)
	player2_score_rendertext = RenderText(font_controller, white, black)

	player_width = 10
	player_height = 50

	quart_screen = winx//4

	make_left_player_pos = lambda: pygame.Vector2(quart_screen, random.randrange(player_height, winy-player_height))
	make_right_player_pos = lambda: pygame.Vector2(winx-quart_screen, random.randrange(player_height, winy-player_height))

	left_player_pos = make_left_player_pos()
	right_player_pos = make_right_player_pos()

	# Make the puck vectors
	puck_pos = pygame.Vector2(winx//2, winy//2)
	puck_velocity = pygame.Vector2(0, 0)
	puck_pos, puck_velocity = reset_puck(right_player_pos, puck_pos, puck_velocity, winx, winy)

	while not done:
		puck_pos.x += puck_velocity.x
		puck_pos.y += puck_velocity.y

		left_player_did_collide = check_player_collision(left_player_pos, puck_pos, player_width, player_height)
		right_player_did_collide = check_player_collision(right_player_pos, puck_pos, player_width, player_height)

		if left_player_did_collide:
			print("left_player_did_collide")
			puck_velocity.reflect_ip(pygame.Vector2(1,0))

		if right_player_did_collide:
			print("right_player_did_collide")
			puck_velocity.reflect_ip(pygame.Vector2(1,0))

		cws = check_wall_collision(puck_pos, winx, winy)
		if cws[0]:
			if cws[1] == 0:
				player2_score += 1
			elif cws[1] == 1:
				player1_score += 1
			puck_pos, puck_velocity = reset_puck(right_player_pos, puck_pos, puck_velocity, winx, winy)

		events = pygame.event.get()
		for e in events:
			if e.type == pygame.KEYDOWN:
				if e.key == pygame.K_UP:
					left_player_pos.y -= 10
				if e.key == pygame.K_DOWN:
					left_player_pos.y += 10
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
