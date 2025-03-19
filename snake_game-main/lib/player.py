import pygame
class Player:
    def __init__(self):
        pass

    def get_movement(last_key_pressed,keys):
        last_key_pressed = last_key_pressed
        if keys[pygame.K_DOWN]:
            last_key_pressed = pygame.K_DOWN
        elif keys[pygame.K_UP]:
            last_key_pressed = pygame.K_UP
        elif keys[pygame.K_LEFT]:
            last_key_pressed = pygame.K_LEFT
        elif keys[pygame.K_RIGHT]:
            last_key_pressed = pygame.K_RIGHT
        return last_key_pressed
