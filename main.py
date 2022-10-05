# from OpenGL.GL import *
# from OpenGL.GLU import *

import pygame, random

from Shaders import *
from objects import *


class GraphicsProgram3D:
    def __init__(self):

        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)

        # self.projection_view_matrix = ProjectionViewMatrix()
        # self.shader.set_projection_view_matrix(self.projection_view_matrix.get_matrix())

        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.angle = 0

        self.keys = {
            K_UP: False,
            K_DOWN: False,
            K_LEFT: False,
            K_RIGHT: False,
            K_SPACE: False,
            K_w: False,
            K_s: False,
            K_a: False,
            K_d: False
        }

        self.white_background = False

        self.init_openGL()
        self.init_objects()

    def init_openGL(self):
        self.shader = Shader3D()
        self.shader.use()

        model_matrix = ModelMatrix()

        Cube(0, 0, 0, 0, 0, 0, (0, 0, 0)).init_openGL(self.shader, model_matrix)

    def init_objects(self):
        self.walls = [Cube(0, -1, 0, 100, 1, 100, (0.5, 0.5, 0.5))]

        self.player = Player(1, 0, 1, 0.5, 0.3, self.shader)

        # self.walls.append(Cube(10, 0, 10, 20, 4, 1, (0, 1, 0)))
        # self.walls.append(Cube(10, 0, 20, 20, 4, 1, (1, 0, 0)))

        self.moving_cubes = []

        # self.moving_cubes.append(MovingCube(5, 1, 5, 1, 1, 1, (0, 0, 1), Vector(10, 2, 10), 1))
        # self.moving_cubes.append(MovingCube(10, 0, 5, 1, 1, 1, (0, 0, 1), Vector(10, 0, 10), 1))

        self.generate_map()

    def _remove_wall(self, from_cell, to_cell):
        from_x = from_cell.cell_X
        from_z = from_cell.cell_Z

        to_x = to_cell.cell_X
        to_z = to_cell.cell_Z

        if from_x > to_x:
            from_cell.rightWall = None
        elif from_x < to_x:
            to_cell.rightWall = None
        elif from_z < to_z:
            to_cell.bottomWall = None
        elif from_z > to_z:
            from_cell.bottomWall = None

    def make_maze(self, current_cell, goal_cell, cells):
        current_cell.visited = True

        if current_cell == goal_cell: return

        x = current_cell.cell_X
        z = current_cell.cell_Z

        neighbors = []
        if x > 0:
            neighbors.append(cells[x - 1][z])
        if x < MAZE_WIDTH-1:
            neighbors.append(cells[x + 1][z])

        if z > 0:
            neighbors.append(cells[x][z - 1])
        if z < MAZE_DEPTH-1:
            neighbors.append(cells[x][z + 1])

        random.shuffle(neighbors)

        for cell in neighbors:
            if not cell.visited:
                self._remove_wall(current_cell, cell)
                self.make_maze(cell, goal_cell, cells)

    def generate_map(self):
        self.cells = [[Cell(x, z) for z in range(MAZE_DEPTH)] for x in range(MAZE_WIDTH)]

        start_point = self.cells[random.randint(0, MAZE_WIDTH-1)][random.randint(0, MAZE_DEPTH-1)]
        goal_point = self.cells[random.randint(0, MAZE_WIDTH-1)][random.randint(0, MAZE_DEPTH-1)]

        self.make_maze(start_point, goal_point, self.cells)

        self.walls.append(Cube(0, 0, MAZE_DEPTH * CELL_SIZE, MAZE_WIDTH * CELL_SIZE, WALL_HEIGHT * 2, WALL_THICKNESS, (1, 1, 1)))
        self.walls.append(Cube(MAZE_WIDTH * CELL_SIZE, 0, 0, WALL_THICKNESS, WALL_HEIGHT * 2, MAZE_DEPTH * CELL_SIZE + WALL_THICKNESS, (1, 1, 1)))

        # self.cells = []

    def update(self):
        delta_time = self.clock.tick() / 1000.0

        for cube in self.moving_cubes:
            cube.update(delta_time)

        colliders = [*self.walls, *self.moving_cubes]

        self.player.update(self.keys, colliders, delta_time)
        # print(self.player.pos)

    def draw_walls(self):
        for wall in self.walls:
            wall.draw()

        for column in self.cells:
            for cell in column:
                if cell.bottomWall: cell.bottomWall.draw()
                if cell.rightWall: cell.rightWall.draw()

    def draw_moving(self):
        for cube in self.moving_cubes:
            cube.draw()

    def display(self):
        glEnable(
            GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        if self.white_background:
            glClearColor(1.0, 1.0, 1.0, 1.0)
        else:
            glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(
            GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.player.draw()

        self.draw_walls()

        self.draw_moving()

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

                    self.keys[event.key] = True

                elif event.type == pygame.KEYUP:
                    self.keys[event.key] = False

            self.update()
            self.display()

        # OUT OF GAME LOOP
        pygame.quit()

    def start(self):
        self.program_loop()


if __name__ == "__main__":
    GraphicsProgram3D().start()