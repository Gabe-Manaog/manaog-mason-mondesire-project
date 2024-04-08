"""
author: Faisal Qureshi
email: faisal.qureshi@uoit.ca
website: http://www.vclab.ca
license: BSD
"""


import pygame, sys
import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import ode

use_rk4 = True
# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# clock object that ensure that animation has the same
# on all machines, regardless of the actual machine speed.
clock = pygame.time.Clock()

def load_image(name):
    image = pygame.image.load(name)
    return image

class MyCircle(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        self.image.fill(WHITE)
        cx = self.rect.centerx
        cy = self.rect.centery
        pygame.draw.circle(self.image, color, (width//2, height//2), cx, cy)
        self.rect = self.image.get_rect()

    def update(self):
        pass

class Simulation:
    def __init__(self,speed,angle_degrees):
            # TODO
        self.t = 0
        self.dt = 0.1
        self.vx = speed * np.cos(np.radians(angle_degrees))
        self.vy = speed * np.sin(np.radians(angle_degrees))
        self.pos = np.array([60.0, 270.0, self.vx, self.vy])
        self.trace_x = [self.pos[0]]
        self.trace_y = [self.pos[1]]
        self.gamma = 0.0001
        self.tol_distance = 0.001
        self.gravity = 9.8
        self.mass = 1
        self.paused = True # starting in paused mode

        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.solver.set_f_params(self.gamma, self.gravity)
        self.solver.set_initial_value(self.pos, self.t)

    def f(self, t, state, arg1, arg2):
        # TO DO
        vx = state[2]
        vy = state[3]
        ax = (-arg1 * state[2])/self.mass
        ay = (-arg2)/self.mass
        return [vx, vy, ax, ay]
        pass
    def is_collision(self, state):
        return state[1]<=200 or (state[0] >= 455 and state[1]<=570) or ((state[0]>=400 and state[0]<=410) and state[1]<=455)

    def step(self):
        new_state = self.solver.integrate(self.t + self.dt)
        # Collision detection
        if not self.is_collision(new_state):
            self.pos = new_state
            self.t += self.dt
            self.trace_x.append(self.pos[0])
            self.trace_y.append(self.pos[1])
        else:
            if  (new_state[0] >= 455 and new_state[1]<=570):
                angle_at_impact = math.atan(self.pos[2]/self.pos[3])
                new_velocity = math.sqrt(self.pos[2] ** 2 +self.pos[3]**2)
                new_velocity_x = 0.2 * new_velocity*math.cos(np.radians(angle_at_impact)+2.355)
                state_after_collision = [self.pos[0],self.pos[1],new_velocity_x,self.pos[3]]
            elif((new_state[0]>=400 and new_state[0]<=410) and new_state[1]<=455):
                angle_at_impact = math.atan(self.pos[2]/self.pos[3])
                new_velocity = math.sqrt(self.pos[2] ** 2 +self.pos[3]**2)
                new_velocity_y = 0.2 * new_velocity*math.sin(np.radians(angle_at_impact)+0.785)
                state_after_collision = [self.pos[0],self.pos[1],self.pos[2],new_velocity_y]
            elif(new_state[1]<=200):
                angle_at_impact = math.atan(self.pos[2]/self.pos[3])
                new_velocity = math.sqrt(self.pos[2] ** 2 +self.pos[3]**2)
                new_velocity_y = 0.2 * new_velocity*math.sin(np.radians(angle_at_impact)+0.785)
                state_after_collision = [self.pos[0],self.pos[1],self.pos[2],new_velocity_y]
            
            self.pos = state_after_collision
            self.solver.set_initial_value(self.pos, self.t)
        # TODO
    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

def sim_to_screen(win_height, x, y):
    '''flipping y, since we want our y to increase as we move up'''
    x += 10
    y += 10

    return x, win_height - y

def main():
    # initializing pygame
    pygame.init()

    # setting up the window
    win_width = 640
    win_height = 640
    screen = pygame.display.set_mode((win_width, win_height))
    background_image = pygame.image.load('basketball-court.jpg') 
    background_image = pygame.transform.scale(background_image, (win_width, win_height))
    pygame.display.set_caption('2D projectile motion')

    # setting up a sprite group for the circle
    my_sprite = MyCircle(RED, 15,15)
    my_group = pygame.sprite.Group(my_sprite)

    # setting up simulation
    sim = Simulation(81,70)

    # rectangle properties

    # main loop
    while True:
        clock.tick(30)  # 30 fps

        # update circle position
        my_sprite.rect.x, my_sprite.rect.y = sim_to_screen(win_height, sim.pos[0], sim.pos[1])

        # handling events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    sim.pause()
                    print(sim.pos[0])
                    print(sim.pos[1])
                elif event.key == pygame.K_r:
                    sim.resume()
                elif sim.paused and event.key == pygame.K_SPACE:
                    sim.step()
        screen.blit(background_image, (0, 0))
        
        # draw rectangle

        # update and draw circle
        my_group.update()
        my_group.draw(screen)

        # update display
        pygame.display.flip()

        # update simulation
        if not sim.paused:
            sim.step()


    # print the range and plot trajectory
    print('Range: ',sim.trace_x[-1])
    plt.figure(1)
    plt.plot(sim.trace_x, sim.trace_y)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.axis('equal')
    plt.title('2D projectile trajectory')
    plt.show()

if __name__ == '__main__':
    main()


    # initializing pygame
    pygame.init()

    # top left corner is (0,0)
    win_width = 640
    win_height = 640
    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption('2D projectile motion')
    pygame.draw.rect(screen, GREEN, win_width,win_height)

    # setting up a sprite group, which will be drawn on the
    # screen
    my_sprite = MyCircle(RED, 5, 5)
    my_group = pygame.sprite.Group(my_sprite)

    # setting up simulation
    sim = Simulation()
    print('--------------------------------')
    print('Usage:')
    print('Press (r) to start/resume simulation')
    print('Press (p) to pause simulation')
    print('Press (space) to step forward simulation when paused')
    print('--------------------------------')

    while True:
        # 30 fps
        clock.tick(30)

        # update sprite x, y position using valuesx
        # returned from the simulation
        my_sprite.rect.x, my_sprite.rect.y = sim_to_screen(win_height, sim.pos[0], sim.pos[1])

        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            sim.pause()
            continue
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            sim.resume()
            continue
        else:
            pass

        # clear the background, and draw the sprites
        screen.fill(WHITE)
        my_group.update()
        my_group.draw(screen)
        pygame.display.flip()


        # update simulation
        if not sim.paused:
            sim.step()
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                sim.step()
    print('Range: ',sim.trace_x[-1])
    plt.figure(1)
    plt.plot(sim.trace_x, sim.trace_y)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.axis('equal')
    plt.title('2D projectile trajectory')
    plt.show()


if __name__ == '__main__':
    main()
