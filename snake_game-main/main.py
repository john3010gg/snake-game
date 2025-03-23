import pygame
from lib.player import Player
from lib.snake import Snake
from lib.snake import Table
from lib.snake import Apple
from sys import exit

pygame.init()

#Variables tipo group
snake = pygame.sprite.GroupSingle()
apples = pygame.sprite.GroupSingle()
snake.add(Snake())
table = Table()
ORIGIN_X, ORIGIN_Y = 0, 50
apple_x, apple_y = 0, 0
table.insert_at(0, 0, 1)
px_of_square = 306
keep_game = True
last_key_pressed = pygame.K_DOWN # movimiento predeterminado de la serpiente
clock = pygame.time.Clock()
last_time_moved = 0
snake_speed = 300 #medido en ms
spawn_apple_speed = 3000
last_eaten_time = 0
terrain_img = pygame.image.load('lib/terrain.png')

# Variables para la puntuación
score = 0
points_per_apple = 10   # Puntos por cada manzana comida
normal_font = pygame.font.Font('lib/PressStart2P-Regular.ttf', 16)
font_dead = pygame.font.Font('lib/Creepster-Regular.ttf', 56)
HIGH_SCORE_FILE = "high_scores.txt"

# Cargar música de fondo
pygame.mixer.init()
pygame.mixer.music.load("music/Pokemon Red and Blue OST- Complete Soundtrack.mp3")
pygame.mixer.music.set_volume(0.3)  # Volumen (0.0 a 1.0)
pygame.mixer.music.play(-1)  # Reproduce en bucle (-1)


# Cargar el efecto de sonido para comer una manzana

eat_sound = pygame.mixer.Sound("music/apple_effect.mp3")  # Reemplaza con la ruta a tu archivo de sonido
eat_sound.set_volume(0.2)  # Volumen del efecto de sonido (0.0 a 1.0)


screen = pygame.display.set_mode((px_of_square,px_of_square + ORIGIN_Y))
pygame.display.set_caption('Snake Game')

while True:

    pygame.draw.rect(screen, (50, 50, 50), (0, 0, px_of_square, ORIGIN_Y))  # Grey panel background
    current_time = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()
    screen.blit(terrain_img,(0, ORIGIN_Y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Mostrar la puntuación
    score_text = normal_font.render(f"Puntuación: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    if keep_game:
        last_key_pressed = Player.get_movement(last_key_pressed ,keys)
        snake.sprite.update_direction(last_key_pressed)
        snake_body = snake.sprite.body_sprites
        snake_body.draw(screen)
        snake.draw(screen)
        apples.draw(screen)
    else:
        # Mostrar mensaje de fin de juego
        game_over_text = font_dead.render("Game over!", True, (255, 0, 0))
        screen.blit(game_over_text, (50, px_of_square / 2))
        snake.empty()
        pygame.mixer.music.stop()



    if current_time - last_time_moved > snake_speed and snake.sprite != None:
        last_time_moved = current_time
        snake.sprite.move(table)

        x = snake.sprite.positions['head'][0] * 34
        y = snake.sprite.positions['head'][1] * 34 + ORIGIN_Y
        snake.sprite.rect.topleft = (x, y)
        
        if table.collision:
            keep_game = False  

        if apples.sprite and pygame.Rect.colliderect(apples.sprite.rect, snake.sprite.rect):
            apples.sprite.kill()
            snake.sprite.new_body()
            last_eaten_time = current_time
            score += points_per_apple  # Incrementar la puntuación
             # Reproducir el sonido al comer una manzana
            eat_sound.play()
            # Generar una nueva manzana inmediatamente
            table.insert_apple()
            apple_pos = table.get_element_position(2)
            if apple_pos:
                apple_x = apple_pos[0][0] * 34
                apple_y = apple_pos[0][1] * 34 + ORIGIN_Y
                apples.add(Apple(apple_x, apple_y))
            
            
        if pygame.sprite.spritecollide(snake.sprite,snake_body, True):
             keep_game = False

    if current_time - last_eaten_time > spawn_apple_speed and table.get_element_position(2) == []:
            table.insert_apple()
            apple_x = table.get_element_position(2)[0][0] * 34
            apple_y = table.get_element_position(2)[0][1] * 34 + ORIGIN_Y
            apples.add(Apple(apple_x, apple_y))
    

    pygame.display.flip()
    clock.tick(60)

pygame.quit()