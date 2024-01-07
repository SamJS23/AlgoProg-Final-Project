#importing all the libraries and modules
import pygame, sys
from pygame.locals import *
import random
#initialize all the pygame modules
pygame.init()
#setting the fps 
clock = pygame.time.Clock()
fps = 80
#screen size
screen_width = 864
screen_height = 936
#setting screen size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Soar')
#scroll
ground_scroll = 0
scroll_speed = 4
#setting intial value of flying and game_over
flying = False
game_over = False
#pipe values
pipe_gap = 150
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0 
pass_pipe = False
#powerups
shroom_activated = False
speedboost_activated = False
double_activated = False
shroom_activation_time = 0
shroom_duration = 5000
double_activion_time = 0 
double_duration = 5000
speedboost_activion_time = 0 
speedboost_duration = 5000
#intialize main menu
main_menu = True
#define font 
font1 = pygame.font.SysFont('Verdana', 60)
font2 = pygame.font.SysFont('Verdana', 20)
#define color
white = (255, 255, 255)
#load images
bg = pygame.image.load('bg.png')
#adjusting background in main menu  
if main_menu == True:
    bg = pygame.transform.scale(bg, (864, 936))
else:
    bg = bg
ground_img = pygame.image.load('ground.png')
button_img = pygame.image.load('restart.png')
start_img = pygame.image.load('start_btn.png')
start_img = pygame.transform.scale(start_img,(120,63))
exit_img = pygame.image.load('exit_btn.png')
exit_img1 = pygame.transform.scale(exit_img,(120,63))
exit_img2 = pygame.transform.scale(exit_img,(80,42))
logo_img = pygame.image.load('logo.png')
logo_img = pygame.transform.scale(logo_img,(500,500))
def draw_score(text,font1,text_col,x,y):
    img = font1.render(text,True,text_col)
    screen.blit(img,(x,y))
def draw_duration(text,font2,text_col,x,y):
    img = font2.render(text,True,text_col)
    screen.blit(img,(x,y))

def reset_game():
    pipe_group.empty()
    shroom_group.empty()
    double_group.empty()
    speed_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0 
    shroom_activated = False
    shroom_activation_time = 0
    speedboost_activated = False
    speedboost_activation_time = 0
    double_activated = False
    double_activation_time = 0

    return score, shroom_activated, shroom_activation_time, speedboost_activated, speedboost_activation_time, double_activated, double_activation_time
#powerups
class Speed(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('speed boost.png')
        self.image = pygame.transform.scale(self.image, (100,100))
        self.rect = self.image.get_rect()
        self.rect.topleft = [x - 13,y]
    def update(self):
        if speedboost_activated:
            self.rect.x -= scroll_speed + 1
        else:
            self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()
class Shroom(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('mini shroom.png')
        self.image = pygame.transform.scale(self.image, (100,100))
        self.rect = self.image.get_rect()
        self.rect.topleft = [x - 13,y]
    def update(self):
        if speedboost_activated:
            self.rect.x -= scroll_speed + 1
        else:
            self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()
class Double(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('2x.png')
        self.image = pygame.transform.scale(self.image, (100,100))
        self.rect = self.image.get_rect()
        self.rect.topleft = [x - 13,y]
    def update(self):
        if speedboost_activated:
            self.rect.x -= scroll_speed + 1
        else:
            self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()
class Bird(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0 
        for num in range(1,4):
            img = pygame.image.load(f'bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.topleft = [x,y]
        self.vel = 0 
        self.clicked = False
    def update(self):
        if flying == True:
            #gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)
        if game_over == False:
            #jump
            if (pygame.mouse.get_pressed()[0] == 1 or pygame.key.get_pressed()[pygame.K_SPACE]) and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0 and pygame.key.get_pressed()[pygame.K_SPACE] == False:
                self.clicked = False
            #handle the animation
            self.counter += 1
            flap_cooldown = 15

            if self.counter > flap_cooldown:
                self.counter = 0 
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0 
            self.image = self.images[self.index]  

            #rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)
        #make bird smaller when shroom active
        if shroom_activated:
            current_center = self.rect.center  
            self.image = pygame.transform.scale(self.images[self.index], (30, 25))
            self.rect = self.image.get_rect()
            self.rect.center = current_center 

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()
        #position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image,False, True)
            self.rect.bottomleft = [x,y - int(pipe_gap/2)]
        if position == -1:
            self.rect.topleft = [x,y + int(pipe_gap/2)]
    def update(self):
        if speedboost_activated:
            self.rect.x -= scroll_speed + 1
        else:
            self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()
class Button():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    def draw(self):
        action = False
        #get mouse position 
        pos = pygame.mouse.get_pos()
        #check if mouse is over the button 
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action
    
shroom_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
double_group = pygame.sprite.Group()
speed_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height/2))

bird_group.add(flappy)
#create restart button instance 
button = Button(screen_width // 2 - 100, screen_height // 2, button_img)
startbtn = Button(screen_width // 2 - 50, screen_height // 2, start_img)
exitbtn1 = Button(screen_width // 2 - 50, screen_height // 2 + 100, exit_img1)
exitbtn2 = Button(screen_width // 2 + 50, screen_height // 2, exit_img2)
run = True
while run: 

    
    #draw background
    screen.blit(bg,(0,0))
    if main_menu == True:
        screen.blit(logo_img, (200,125))
        if startbtn.draw():
            main_menu = False
            flying = False
        if exitbtn1.draw():
            run = False
    else:
        bird_group.draw(screen)
        bird_group.update()
        shroom_group.draw(screen)
        double_group.draw(screen)
        pipe_group.draw(screen)
        speed_group.draw(screen)


        #draw the ground
        screen.blit(ground_img,(ground_scroll, 768))

        #check the score
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and pass_pipe == False:
                pass_pipe = True 
            if pass_pipe == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    if double_activated == False:
                        score += 1
                    elif double_activated == True:
                        score += 2 
                    pass_pipe = False
        draw_score(str(score),font1,white,int(screen_width/2),100)
        #look for collision
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
        
        if pygame.sprite.groupcollide(bird_group, shroom_group, False, True):
            shroom_activated = True
            shroom_activation_time = pygame.time.get_ticks()
        if pygame.sprite.groupcollide(bird_group, double_group, False, True):
            double_activated = True
            double_activation_time = pygame.time.get_ticks()
        if pygame.sprite.groupcollide(bird_group, speed_group, False, True):
            speedboost_activated = True
            speedboost_activation_time = pygame.time.get_ticks()
        
        #checking shroom activation 
        if shroom_activated:
            current_time = pygame.time.get_ticks()
            remaining_duration = max(0, shroom_duration - (current_time - shroom_activation_time))
            draw_duration(f'Remaining mini shroom duration: {remaining_duration // 1000} seconds', font2, white, screen_width // 2 - 200, screen_height // 2 - 200)
            if current_time - shroom_activation_time >= shroom_duration or game_over == True:
                shroom_activated = False
        #checking double activation
        if double_activated:
            current_time = pygame.time.get_ticks()
            remaining_duration = max(0, double_duration - (current_time - double_activation_time))
            draw_duration(f'Remaining double duration: {remaining_duration // 1000} seconds', font2, white, screen_width // 2 - 200, screen_height // 2 - 170)
            if current_time - double_activation_time >= double_duration or game_over == True:
                double_activated = False
        if speedboost_activated:
            current_time = pygame.time.get_ticks()
            remaining_duration = max(0, speedboost_duration - (current_time - speedboost_activation_time))
            draw_duration(f'Remaining speedboost duration: {remaining_duration // 1000} seconds', font2, white, screen_width // 2 - 200, screen_height // 2 - 140)
            if current_time - speedboost_activation_time >= speedboost_duration or game_over == True:
                speedboost_activated = False

        # Check if bird has hit the ground
        if flappy.rect.bottom >= 768:
            game_over = True
            flying = False

        # Draw and scroll the ground
        if not game_over and flying:
            time_now = pygame.time.get_ticks()

            # Generate new pipes
            if speedboost_activated:
                pipe_frequency = 1000
            else:
                pipe_frequency = 1500
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                random_powerup = random.randint(1, 10)
                btm_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

                if random_powerup == 8:
                    speed = Speed(screen_width, int(screen_height/2) + pipe_height)
                    speed.rect.centery = (btm_pipe.rect.centery + top_pipe.rect.centery) / 2
                    speed_group.add(speed)

                if random_powerup == 9:
                    double = Double(screen_width, int(screen_height/2) + pipe_height)
                    double.rect.centery = (btm_pipe.rect.centery + top_pipe.rect.centery) / 2
                    double_group.add(double)

                if random_powerup == 10:
                    shroom = Shroom(screen_width, int(screen_height/2) + pipe_height)
                    shroom.rect.centery = (btm_pipe.rect.centery + top_pipe.rect.centery) / 2
                    shroom_group.add(shroom)
            if speedboost_activated:
                ground_scroll -= scroll_speed + 1
            else:
                ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

            pipe_group.update()
            shroom_group.update()
            double_group.update()
            speed_group.update()
        #check for game over and reset 
        if game_over == True:
            draw_score(f'Final Score:{str(score)}',font1, white, screen_width // 2 - 175, screen_height // 2 - 100)
            if button.draw() == True:
                game_over = False
                score, shroom_activated,shroom_activation_time, speedboost_activated, speedboost_activation_time, double_activated, double_activation_time  = reset_game()
            if exitbtn2.draw():
                run = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True 
        if event.type == pygame.KEYDOWN and flying == False and game_over == False:
            flying = True 
    
    pygame.display.update()
    clock.tick(fps)
            