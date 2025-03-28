import pygame
import random
class Table:
    def __init__(self):
        self.table = [[0 for _ in range(9)] for _ in range(9)]
        self.collision = False

    #Dado un elemento y las posiciones x y y de la coordenada (x,y) del elemento, se introduce en el tablero
    # si (x,y) esta fuera del tablero se pone como actualiza la variable que detecta si hubo una colision con el borde
    def insert_at(self, row, col, element):
        row = int(row)
        col = int(col)
        if self.valid_position(col,row):
            self.table[row][col] = element
        else:
            self.collision = True
    
    def delete_at(self, row, col):
        self.table[row][col] = 0
 

    def valid_position(self, row, col):
        return 0 <= int(col) <= 8 and 0 <= int(row) <= 8
    
    # dado un elemento, busca todas las casillas donde se encuentre dicho elemento
    def get_element_position(self, element):
        positions = []
        for i in range(9):
            for k in range(9):
                if self.table[i][k] == element:
                    positions.append([i,k])
        return positions
    
    #Genera una coordenada (x,y) aleatoria dentro del tablero
    def random_position(self):
        x = random.randint(0, 8)
        y = random.randint(0, 8)
        while self.table[x][y] != 0:
            x = random.randint(0, 8)
            y = random.randint(0, 8) 
        return x, y

    #introduce un elemento manzana (representado con 2) en el tablero en una posicion aleatoria
    def insert_apple(self):
        x, y = self.random_position()
        self.insert_at(x , y , 2)

    #se limpia el tablero de todas las instancias de elementos que no sean manzanas
    def clear(self):
        apple_position = self.get_element_position(2)
        if apple_position:
            x , y = apple_position[0]
            self.table = [[0 for _ in range(9)] for _ in range(9)]
            self.table[x][y] = 2
        else:
            self.table = [[0 for _ in range(9)] for _ in range(9)]

    # Se actualiza el tablero con las nuevas posiciones de la serpiente
    def update_table(self, positions):
        self.clear()

        for key in positions:
            if key == 'head':
                self.insert_at(*positions[key], 1)
            else:
                for position in positions['body']:
                    self.insert_at(*position, 3)





class Snake(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load('lib/snake_head.png')
        self.rect = self.image.get_rect()

        self.direction = [0,1]
        self.positions = { 'head': [0,0],
                            'body': []
        }

        self.body_sprites = pygame.sprite.Group()
        self.body_image = pygame.image.load('lib/pixel_body_test.png')

    #se actualiza la instance variable direction con el input del keyboard del usuario, al final se llama a la funcion
    #rotate_head() que actualiza la imagen de la cabeza de la serpiente
    def update_direction(self, key_pressed):

        if key_pressed == pygame.K_UP:
            self.direction[1] = -1
            self.direction[0] = 0
        elif key_pressed == pygame.K_DOWN:
            self.direction[1] = 1
            self.direction[0] = 0
        elif key_pressed == pygame.K_LEFT:
            self.direction[1] = 0
            self.direction[0] = -1
        elif key_pressed == pygame.K_RIGHT:
            self.direction[1] = 0
            self.direction[0] = 1

        self.rotate_head()


    #Dado el tablero, se mueve la serpiente una casilla segun su direccion, la parte del cuerpo inmediatemente despues de la cabeza
    #toma su posicion, y el resto toma la posicion de su sucesor.
    def move(self, table):
        old_head_position_x, old_head_position_y = self.positions['head'][0], self.positions['head'][1]
        old_body_position_x, old_body_position_y = self.positions['head'][0], self.positions['head'][1]
        if self.direction == [0,1]:
            self.positions['head'] = [old_head_position_x, old_head_position_y + 1]
        if self.direction == [0,-1]:
            self.positions['head'] = [old_head_position_x, old_head_position_y - 1]
        if self.direction == [1,0]:
            self.positions['head'] = [old_head_position_x + 1, old_head_position_y]
        if self.direction== [-1,0]:
            self.positions['head'] = [old_head_position_x - 1, old_head_position_y]

        new_head_position_x, new_head_position_y = self.positions['head']
        if table.valid_position(new_head_position_x, new_head_position_y) and table.table[new_head_position_x][new_head_position_y] == 3:
            table.collision = True

        for i in range(len(self.positions['body'])):
            temp_x, temp_y = self.positions['body'][i]
            self.positions['body'][i] = [old_body_position_x, old_body_position_y]
            old_body_position_x, old_body_position_y = temp_x, temp_y
        
        self.update_body_sprites()
        table.update_table(self.positions)


    #introduce una nueva parte al cuerpo de la serpiente
    def new_body(self):
        if self.positions['body'] == []:
            x, y = [x + y for x, y in zip(self.direction, self.positions['head'])]
            self.positions['body'].append([x,y])
        else:
            x, y = [x + y for x, y in zip(self.direction, self.positions['body'][-1])]
            self.positions['body'].append([x,y])


    #se actualiza la instance variable body_sprites con cada parte del cuerpo nueva, para facilitar la deteccion de colisiones del cuerpo
    def update_body_sprites(self):
        self.body_sprites.empty()
        for part_of_body in self.positions['body']:
            sprite = pygame.sprite.Sprite()
            sprite.image = self.body_image
            sprite.rect = self.body_image.get_rect(topleft=(part_of_body[0] * 34, part_of_body[1] * 34 + 50))
            self.body_sprites.add(sprite)
    
    #actualiza la imagen de la cabeza de la serpiente segun su direccion
    def rotate_head(self):
        if self.direction == [1,0]:
            self.image = pygame.transform.rotate(pygame.image.load('lib/snake_head.png'), 90)
        elif self.direction == [0,-1]:
            self.image = pygame.transform.rotate(pygame.image.load('lib/snake_head.png'), 180)
        elif self.direction == [-1, 0]:
            self.image = pygame.transform.rotate(pygame.image.load('lib/snake_head.png'), 270)
        else:
            self.image = pygame.transform.rotate(pygame.image.load('lib/snake_head.png'), 0)


#clase tipo Sprite de la manzana para facilitar la deteccion de la colision y su apartado visual
class Apple(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('lib/apple.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.position = [[x/34, y/34]]

#clase Player que se encarga de obtener el input del usuario y actualizar la variable last_key_pressed
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

