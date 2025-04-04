import pygame
from lib.snake import Player, Snake, Table, Apple
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
sky_img = pygame.image.load('lib/river.png')

# Variables para la puntuación
score = 0
points_per_apple = 10  
MAX_BOARD_SIZE = 81 

normal_font = pygame.font.Font('lib/PressStart2P-Regular.ttf', 15)
font_dead = pygame.font.Font('lib/Creepster-Regular.ttf', 56)
HIGH_SCORE_FILE = "high_scores.txt"

# Cargar música de fondo
pygame.mixer.init()
pygame.mixer.music.load("music/pokemon_music.mp3")
pygame.mixer.music.set_volume(0.3) 
pygame.mixer.music.play(-1) 

# Cargar el efecto de sonido para comer una manzana
eat_sound = pygame.mixer.Sound("music/apple_effect.mp3") 
eat_sound.set_volume(0.2)  

# Cargar sonido de muerte 
dead_sound = pygame.mixer.Sound("music/death_sound.mp3")
dead_sound.set_volume(0.2)

# Variables para el botón de mute
is_muted = False
mute_button_rect = pygame.Rect(230, 10, 65, 25)
mute_font = pygame.font.Font('lib/PressStart2P-Regular.ttf', 7)

# Variables para clic en el tablero
clicked_pos = None
snake_length_at_end = 0


screen = pygame.display.set_mode((px_of_square,px_of_square + ORIGIN_Y))
pygame.display.set_caption('Snake Game')

# Nuevas variables para el menú y usuario
MENU, PLAYING, GAME_OVER, HIGH_SCORES, ENTER_NAME = 0, 1, 2, 3, 4
game_state = ENTER_NAME
menu_font = pygame.font.Font('lib/PressStart2P-Regular.ttf', 15)
NORMAL_SPEED, HARD_SPEED = 300, 125
username = ""
game_over_time = 0
game_over_delay = 2000  # Tiempo antes de mostrar "SPACE para menú"
game_over_display_time = 3000  # Tiempo que "Game over!" y la puntuación se muestran solos (3 segundos)

def load_high_scores():
    default_scores = [["Jugador1", "0"], ["Jugador2", "0"], ["Jugador3", "0"]]
    try:
        with open(HIGH_SCORE_FILE, 'r') as file:
            scores = []
            for line in file.readlines():
                parts = line.strip().split(":")
                if len(parts) == 2 and parts[1].isdigit():
                    scores.append([parts[0], parts[1]])
                else:
                    return default_scores
            return scores if scores else default_scores
    except Exception as e:
        print(f"Error al cargar puntuaciones: {e}")
        return default_scores

def save_high_score(username, score):
    scores = load_high_scores()
    scores.append([username, str(score)])
    scores.sort(key=lambda x: int(x[1]), reverse=True)
    scores = scores[:3]
    try:
        with open(HIGH_SCORE_FILE, 'w') as file:
            for name, s in scores:
                file.write(f"{name}:{s}\n")
    except Exception as e:
        print(f"Error al guardar puntuaciones: {e}")

def reset_game(selected_speed):
    global snake, apples, table, score, keep_game, last_key_pressed, last_time_moved, last_eaten_time, snake_speed
    snake.empty()
    apples.empty()
    snake.add(Snake())
    table = Table()
    table.insert_at(0, 0, 1)
    score = 0
    keep_game = True
    last_key_pressed = pygame.K_DOWN
    last_time_moved = 0
    last_eaten_time = 0
    snake_speed = selected_speed
    snake_length_at_end = 0
    pygame.mixer.music.play(-1)

def draw_menu():
    screen.blit(sky_img, (0, 0))
    screen.blit(terrain_img, (0, ORIGIN_Y))
    title = menu_font.render("Snake Game", True, (0))
    normal = menu_font.render("1. Normal", True, (0))
    hard = menu_font.render("2. Difícil", True, (0))
    scores = menu_font.render("3. Puntuaciones", True, (0))
    screen.blit(title, (50, 100))
    screen.blit(normal, (50, 150))
    screen.blit(hard, (50, 180))
    screen.blit(scores, (50, 210))

def draw_high_scores():
    screen.blit(sky_img, (0, 0))
    screen.blit(terrain_img, (0, ORIGIN_Y))
    high_scores = load_high_scores()
    title = menu_font.render("Puntuaciones", True, (0))
    screen.blit(title, (50, 100))
    for i, (name, score) in enumerate(high_scores):
        score_text = normal_font.render(f"{i+1}. {name}: {score}", True, (0))
        screen.blit(score_text, (50, 150 + i * 30))
    back = normal_font.render("ESC para volver", True, (0))
    screen.blit(back, (50, 250))

def draw_enter_name():
    screen.blit(sky_img, (0, 0))
    screen.blit(terrain_img, (0, ORIGIN_Y))
    prompt = menu_font.render("Ingresa tu nombre:", True, (0))
    name_text = normal_font.render(username, True, (0))
    enter_text = normal_font.render("Presiona ENTER", True, (0))
    screen.blit(prompt, (30, 120))
    screen.blit(name_text, (80, 160))
    screen.blit(enter_text, (60, 200))

def toggle_mute():
    global is_muted
    is_muted = not is_muted
    if is_muted:
        pygame.mixer.music.set_volume(0)
        eat_sound.set_volume(0)
        dead_sound.set_volume(0)
    else:
        pygame.mixer.music.set_volume(0.3)
        eat_sound.set_volume(0.2)
        dead_sound.set_volume(0.2)

def move_toward_clicked_pos():
    global last_key_pressed, clicked_pos
    if clicked_pos and snake.sprite:
        head_x, head_y = snake.sprite.positions['head']
        click_x, click_y = clicked_pos
        if head_x == click_x and head_y == click_y:
            clicked_pos = None
        elif abs(head_x - click_x) > abs(head_y - click_y):
            if head_x < click_x:
                last_key_pressed = pygame.K_RIGHT
            elif head_x > click_x:
                last_key_pressed = pygame.K_LEFT
        else:
            if head_y < click_y:
                last_key_pressed = pygame.K_DOWN
            elif head_y > click_y:
                last_key_pressed = pygame.K_UP

while True:

    screen.blit(sky_img, (0,0))  # Grey panel background
    current_time = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()
    screen.blit(terrain_img,(0, ORIGIN_Y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if game_state == ENTER_NAME:
                if event.key == pygame.K_RETURN and username:
                    game_state = MENU
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 10 and event.key != pygame.K_RETURN:
                    username += event.unicode
            elif game_state == MENU:
                if event.key == pygame.K_1:
                    reset_game(NORMAL_SPEED)
                    game_state = PLAYING
                elif event.key == pygame.K_2:
                    reset_game(HARD_SPEED)
                    game_state = PLAYING
                elif event.key == pygame.K_3:
                    game_state = HIGH_SCORES
            elif game_state == HIGH_SCORES and event.key == pygame.K_ESCAPE:
                game_state = MENU
            elif game_state == GAME_OVER and event.key == pygame.K_SPACE:
                if current_time - game_over_time >= game_over_delay:
                    save_high_score(username, score)
                    game_state = MENU
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == PLAYING:
            mouse_pos = pygame.mouse.get_pos()
            if mute_button_rect.collidepoint(mouse_pos):
                toggle_mute()
            elif mouse_pos[1] >= ORIGIN_Y and mouse_pos[1] < ORIGIN_Y + px_of_square and mouse_pos[0] < px_of_square:
                clicked_x = mouse_pos[0] // 34
                clicked_y = (mouse_pos[1] - ORIGIN_Y) // 34
                if clicked_pos == (clicked_x, clicked_y):
                    clicked_pos = None
                else:
                    clicked_pos = (clicked_x, clicked_y)


    # Mostrar la puntuación
    if game_state == ENTER_NAME:
        draw_enter_name()
    elif game_state == MENU:
        draw_menu()
    elif game_state == HIGH_SCORES:
        draw_high_scores()
    elif game_state == PLAYING:
        score_text = normal_font.render(f"Puntuación:{score}", True, (0))
        screen.blit(score_text, (15, 15))
        mute_text = mute_font.render("Silenciar" if not is_muted else "Desmutear", True, (0))
        pygame.draw.rect(screen, (200, 200, 200), mute_button_rect)
        screen.blit(mute_text, (mute_button_rect.x + 5, mute_button_rect.y + 8))


        if keep_game:
            if clicked_pos:
                move_toward_clicked_pos()
            else:    
                last_key_pressed = Player.get_movement(last_key_pressed ,keys)
            move_toward_clicked_pos()
            snake.sprite.update_direction(last_key_pressed)
            snake_body = snake.sprite.body_sprites
            snake_body.draw(screen)
            snake.draw(screen)
            apples.draw(screen)
            if clicked_pos:
                highlight_rect = pygame.Rect(clicked_pos[0] * 34, clicked_pos[1] * 34 + ORIGIN_Y, 34, 34)
                pygame.draw.rect(screen, (255, 255, 0), highlight_rect, 2)

        else:
            if snake.sprite:
                snake_length_at_end = len(snake.sprite.body_sprites) + 1
            game_over_text = font_dead.render("Game over!", True, (235, 0, 0))
            screen.blit(game_over_text, (50, px_of_square / 2))
            snake.empty()
            pygame.mixer.music.stop()
            game_state = GAME_OVER
            game_over_time = current_time

        if current_time - last_time_moved > snake_speed and snake.sprite != None:
            last_time_moved = current_time
            snake.sprite.move(table)
            x = snake.sprite.positions['head'][0] * 34
            y = snake.sprite.positions['head'][1] * 34 + ORIGIN_Y
            snake.sprite.rect.topleft = (x, y)
            
            if table.collision:
                keep_game = False
                dead_sound.play()  

            if apples.sprite and pygame.Rect.colliderect(apples.sprite.rect, snake.sprite.rect):
                apples.sprite.kill()
                snake.sprite.new_body()
                last_eaten_time = current_time
                score += points_per_apple  # Incrementar la puntuación
                eat_sound.play()
                table.insert_apple()
                apple_pos = table.get_element_position(2)
                if apple_pos:
                    apple_x = apple_pos[0][0] * 34
                    apple_y = apple_pos[0][1] * 34 + ORIGIN_Y
                    apples.add(Apple(apple_x, apple_y))
                
                # Cambio: Verificar victoria cuando la serpiente llena el tablero 9x9 (81 casillas)
                if len(snake.sprite.body_sprites) + 1 >= MAX_BOARD_SIZE:
                    keep_game = False
                    pygame.mixer.music.stop()
                    game_state = GAME_OVER
                    game_over_time = current_time
                
            if pygame.sprite.spritecollide(snake.sprite,snake_body, True):
                 keep_game = False
                 dead_sound.play()

        if current_time - last_eaten_time > spawn_apple_speed and table.get_element_position(2) == []:
                table.insert_apple()
                apple_x = table.get_element_position(2)[0][0] * 34
                apple_y = table.get_element_position(2)[0][1] * 34 + ORIGIN_Y
                apples.add(Apple(apple_x, apple_y))
  
    elif game_state == GAME_OVER:
        # Mostrar "Game over!" junto con la puntuación por un tiempo definido
        if current_time - game_over_time <= game_over_display_time:
            # Cambio: Mostrar "¡Ganaste!" si la serpiente llena el tablero 9x9
            if snake_length_at_end >= MAX_BOARD_SIZE:
                win_text = font_dead.render("¡Ganaste!", True, (0, 255, 0))
                screen.blit(win_text, (50, px_of_square / 2 - 50))
                final_score = normal_font.render(f"Puntuación: {score}", True, (0))
                high_score = load_high_scores()[0][1]
                high_score_text = normal_font.render(f"Récord anterior: {high_score}", True, (0))
                screen.blit(final_score, (50, px_of_square / 2 + 10))
                screen.blit(high_score_text, (50, px_of_square / 2 + 40))
            else:
                game_over_text = font_dead.render("Game over!", True, (255, 0, 0))
            final_score = normal_font.render(f"Puntuación: {score}", True, (0))
            final_score_rect = final_score.get_rect(center=(px_of_square // 2, px_of_square // 2 + 30))
            screen.blit(game_over_text, (35, px_of_square / 2 - 50))
            screen.blit(final_score, final_score_rect)
            
        # Después de game_over_delay, mostrar la opción de volver al menú
        if current_time - game_over_time >= game_over_delay:
            restart_text = normal_font.render("SPACE para menú", True, (0))
            screen.blit(restart_text, (40, px_of_square / 2 + 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()