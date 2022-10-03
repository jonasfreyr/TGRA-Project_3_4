
# from OpenGL.GL import *
# from OpenGL.GLU import *
from math import *

import pygame
from pygame.locals import *

import sys
import time

from Shaders import *
from Matrices import *

class GraphicsProgram3D:
    def __init__(self):

        pygame.init() 
        pygame.display.set_mode((800,600), pygame.OPENGL|pygame.DOUBLEBUF)

        self.shader = Shader3D()
        self.shader.use()

        self.model_matrix = ModelMatrix()

        # self.projection_view_matrix = ProjectionViewMatrix()
        # self.shader.set_projection_view_matrix(self.projection_view_matrix.get_matrix())

        self.view_matrix = ViewMatrix()
        self.projection_matrix = ProjectionMatrix()

        self.projection_matrix.set_perspective(90, 16/9, 1, 100)

        self.shader.set_view_matrix(self.view_matrix.get_matrix())
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.cube = Cube()

        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.angle = 0

        self.UP_key_down = False  ## --- ADD CONTROLS FOR OTHER KEYS TO CONTROL THE CAMERA --- ##
        self.DOWN_key_down = False
        self.LEFT_key_down = False
        self.RIGHT_key_down = False

        self.W_key_down = False  ## --- ADD CONTROLS FOR OTHER KEYS TO CONTROL THE CAMERA --- ##
        self.S_key_down = False
        self.A_key_down = False
        self.D_key_down = False

        self.K_q = False
        self.K_e = False
        self.K_r = False
        self.K_f = False

        self.white_background = False

    def update(self):
        delta_time = self.clock.tick() / 1000.0

        if self.UP_key_down:
            self.view_matrix.pitch(100 * delta_time)
        elif self.DOWN_key_down:
            self.view_matrix.pitch(-100 * delta_time)
        if self.LEFT_key_down:
            self.view_matrix.yaw(-100 * delta_time)
        elif self.RIGHT_key_down:
            self.view_matrix.yaw(100 * delta_time)

        if self.W_key_down:
            self.view_matrix.slide(0, 0, -1 * delta_time)
        elif self.S_key_down:
            self.view_matrix.slide(0, 0, 1 * delta_time)
        if self.A_key_down:
            self.view_matrix.slide(-1 * delta_time, 0, 0)
        elif self.D_key_down:
            self.view_matrix.slide(1 * delta_time, 0, 0)

        if self.K_q:
            self.view_matrix.roll(100 * delta_time)
        elif self.K_e:
            self.view_matrix.roll(-100 * delta_time)

        if self.K_r:
            self.view_matrix.slide(0, 1 * delta_time, 0)
        elif self.K_f:
            self.view_matrix.slide(0, -1 * delta_time, 0)

    def testing(self):
        self.model_matrix.push_matrix()
        self.model_matrix.add_rotation(0, 45, 0)
        self.model_matrix.add_translation(0, 0, -3)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.shader.set_view_matrix(self.view_matrix.get_matrix())
        self.shader.set_solid_color(0, 0, 1)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

    def pyramid(self):
        self.shader.set_view_matrix(self.view_matrix.get_matrix())

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(0, -3, 0)
        self.model_matrix.add_scale(100, 0.1, 100)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.shader.set_solid_color(1, 0, 0)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.add_translation(0, 2, 0)

        level_colors = [(1, 1, 1),
                        (0, 1, 1),
                        (1, 0, 1),
                        (1, 1, 0),
                        (0, 0, 1)]

        cube_amount = 5
        for level in range(cube_amount):
            for cube in range(level+1):
                self.model_matrix.push_matrix()
                self.model_matrix.add_translation(cube, -level, 0)
                self.shader.set_model_matrix(self.model_matrix.matrix)
                self.shader.set_solid_color(*level_colors[level])
                self.cube.draw(self.shader)
                self.model_matrix.pop_matrix()

            self.model_matrix.add_translation(-0.5, 0, 0)

    def dæmi(self):
        self.model_matrix.push_matrix()
        self.model_matrix.add_scale(2, 2, 2)
        self.model_matrix.add_translation(9, 5, -2)
        for index, num in enumerate(self.model_matrix.matrix):
            if index % 4 == 0:
                print()

            print(f" {num} ", end="")

        self.model_matrix.pop_matrix()
        exit(-1)

    def display(self):
        glEnable(GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        if self.white_background:
            glClearColor(1.0, 1.0, 1.0, 1.0)
        else:
            glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, 800, 600)

        self.model_matrix.load_identity()
        # self.dæmi()
        self.pyramid()

        pygame.display.flip()

    def program_loop(self):
        exiting = False
        while not exiting:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True
                        
                    if event.key == K_UP:
                        self.UP_key_down = True
                    elif event.key == K_DOWN:
                        self.DOWN_key_down = True
                    elif event.key == K_LEFT:
                        self.LEFT_key_down = True
                    elif event.key == K_RIGHT:
                        self.RIGHT_key_down = True
                    elif event.key == K_w:
                        self.W_key_down = True  ## --- ADD CONTROLS FOR OTHER KEYS TO CONTROL THE CAMERA --- ##
                    elif event.key == K_s:
                        self.S_key_down = True
                    elif event.key == K_a:
                        self.A_key_down = True
                    elif event.key == K_d:
                        self.D_key_down = True
                    elif event.key == K_q:
                        self.K_q = True
                    elif event.key == K_e:
                        self.K_e = True
                    elif event.key == K_r:
                        self.K_r = True
                    elif event.key == K_f:
                        self.K_f = True

                elif event.type == pygame.KEYUP:
                    if event.key == K_UP:
                        self.UP_key_down = False
                    elif event.key == K_DOWN:
                        self.DOWN_key_down = False
                    elif event.key == K_LEFT:
                        self.LEFT_key_down = False
                    elif event.key == K_RIGHT:
                        self.RIGHT_key_down = False
                    elif event.key == K_w:
                        self.W_key_down = False  ## --- ADD CONTROLS FOR OTHER KEYS TO CONTROL THE CAMERA --- ##
                    elif event.key == K_s:
                        self.S_key_down = False
                    elif event.key == K_a:
                        self.A_key_down = False
                    elif event.key == K_d:
                        self.D_key_down = False
                    elif event.key == K_q:
                        self.K_q = False
                    elif event.key == K_e:
                        self.K_e = False
                    elif event.key == K_r:
                        self.K_r = False
                    elif event.key == K_f:
                        self.K_f = False
            
            self.update()
            self.display()

        #OUT OF GAME LOOP
        pygame.quit()

    def start(self):
        self.program_loop()

if __name__ == "__main__":
    GraphicsProgram3D().start()