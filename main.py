# from OpenGL.GL import *
# from OpenGL.GLU import *
import math

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

        Cube(0, 0, 0, 0, 0, 0, WHITE_COLOR).init_openGL(self.shader, model_matrix)

    def init_objects(self):
        self.walls = []
        self.walls.append(Cube(0, -1, 0, 100, 1, 100, GREEN_COLOR))

        self.player = Player(1, 0, 1, 0.5, 0.2, self.shader)

        light_color = Color(1, 1, 1, 0, 2)
        self.light = Light(MAZE_WIDTH * CELL_SIZE, 30, MAZE_DEPTH * CELL_SIZE, light_color, self.shader)

        # self.walls.append(Cube(10, 0, 10, 20, 4, 1, (0, 1, 0)))
        # self.walls.append(Cube(10, 0, 20, 20, 4, 1, (1, 0, 0)))

        self.moving_cubes = []

        # self.moving_cubes.append(MovingCube(5, 1, 5, 1, 1, 1, (0, 0, 1), Vector(10, 2, 10), 1))
        # self.moving_cubes.append(MovingCube(10, 0, 5, 1, 1, 1, (0, 0, 1), Vector(10, 0, 10), 1))

        self.cells = [[[Cell(x, z, y) for z in range(MAZE_DEPTH)] for x in range(MAZE_WIDTH)] for y in
                      range(MAZE_LEVELS)]

        self.goal_points = set()
        self.start_point = self.cells[0][random.randint(0, MAZE_WIDTH - 1)][random.randint(0, MAZE_DEPTH - 1)]

        self.player.pos = Vector(self.start_point.pixel_X + CELL_SIZE / 2, 0, self.start_point.pixel_Z + CELL_SIZE / 2)

        last_goal = self.start_point
        for level in range(MAZE_LEVELS):
            last_goal = self.generate_map(last_goal, level)
            self.moving_cubes.append(MovingCube(last_goal.pixel_X + WALL_THICKNESS, last_goal.pixel_Y, last_goal.pixel_Z + WALL_THICKNESS, CELL_SIZE - WALL_THICKNESS, ELEVATOR_THICKNESS, CELL_SIZE - WALL_THICKNESS, BLUE_COLOR, Vector(last_goal.pixel_X + WALL_THICKNESS, last_goal.pixel_Y + WALL_HEIGHT + FLOOR_THICKNESS, last_goal.pixel_Z + WALL_THICKNESS), 0.1))

            last_goal.ceiling = None
            if last_goal.cell_Y < MAZE_LEVELS-1:
                last_goal = self.cells[level+1][last_goal.cell_X][last_goal.cell_Z]

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

    def make_maze(self, current_cell, goal_cell, cells, level):
        current_cell.visited = True

        if current_cell == goal_cell: return

        x = current_cell.cell_X
        z = current_cell.cell_Z

        neighbors = []
        if x > 0:
            neighbors.append(cells[level][x - 1][z])
        if x < MAZE_WIDTH-1:
            neighbors.append(cells[level][x + 1][z])

        if z > 0:
            neighbors.append(cells[level][x][z - 1])
        if z < MAZE_DEPTH-1:
            neighbors.append(cells[level][x][z + 1])

        random.shuffle(neighbors)

        for cell in neighbors:
            if not cell.visited:
                self._remove_wall(current_cell, cell)
                self.make_maze(cell, goal_cell, cells, level)

    def generate_map(self, start, level):
        goal_point = self.cells[level][random.randint(0, MAZE_WIDTH-1)][random.randint(0, MAZE_DEPTH-1)]
        while goal_point in self.goal_points:
            goal_point = self.cells[level][random.randint(0, MAZE_WIDTH-1)][random.randint(0, MAZE_DEPTH-1)]

        self.goal_points.add(goal_point)

        self.make_maze(start, goal_point, self.cells, level)

        self.walls.append(Cube(0, 0, MAZE_DEPTH * CELL_SIZE, MAZE_WIDTH * CELL_SIZE, WALL_HEIGHT * MAZE_LEVELS + FLOOR_THICKNESS * MAZE_LEVELS, WALL_THICKNESS, WHITE_COLOR))
        self.walls.append(Cube(MAZE_WIDTH * CELL_SIZE, 0, 0, WALL_THICKNESS, WALL_HEIGHT * MAZE_LEVELS + FLOOR_THICKNESS * MAZE_LEVELS, MAZE_DEPTH * CELL_SIZE + WALL_THICKNESS, WHITE_COLOR))

        return goal_point

    def get_walls_from_cell(self, cell):
        walls = []

        if cell.rightWall:
            walls.append(cell.rightWall)
        if cell.bottomWall:
            walls.append(cell.bottomWall)
        if cell.ceiling:
            walls.append(cell.ceiling)

        # Left
        if cell.cell_X < MAZE_WIDTH-1:
            wall = self.cells[cell.cell_Y][cell.cell_X + 1][cell.cell_Z].rightWall
            wall2 = self.cells[cell.cell_Y][cell.cell_X + 1][cell.cell_Z].bottomWall
            if wall: walls.append(wall)
            if wall2: walls.append(wall2)

        # Above
        if cell.cell_Z < MAZE_DEPTH-1:
            wall = self.cells[cell.cell_Y][cell.cell_X][cell.cell_Z + 1].bottomWall
            wall2 = self.cells[cell.cell_Y][cell.cell_X][cell.cell_Z + 1].rightWall
            if wall: walls.append(wall)
            if wall2: walls.append(wall2)

        # Above to the left
        if cell.cell_X < MAZE_WIDTH-1 and cell.cell_Z < MAZE_DEPTH-1:
            wall = self.cells[cell.cell_Y][cell.cell_X + 1][cell.cell_Z + 1].bottomWall
            wall2 = self.cells[cell.cell_Y][cell.cell_X + 1][cell.cell_Z + 1].rightWall
            if wall: walls.append(wall)
            if wall2: walls.append(wall2)

        # Bottom
        if cell.cell_Z > 0:
            wall = self.cells[cell.cell_Y][cell.cell_X][cell.cell_Z - 1].rightWall
            if wall: walls.append(wall)

        # Bottom to the left
        if cell.cell_Z > 0 and cell.cell_X < MAZE_WIDTH-1:
            wall = self.cells[cell.cell_Y][cell.cell_X + 1][cell.cell_Z - 1].rightWall
            if wall: walls.append(wall)

        # Right
        if cell.cell_X > 0:
            wall = self.cells[cell.cell_Y][cell.cell_X-1][cell.cell_Z].bottomWall
            if wall: walls.append(wall)

        # Above to the right
        if cell.cell_X > 0 and cell.cell_Z < MAZE_DEPTH-1:
            wall = self.cells[cell.cell_Y][cell.cell_X-1][cell.cell_Z+1].bottomWall
            if wall: walls.append(wall)

        # Ceiling from lower cell
        if cell.cell_Y > 0:
            wall = self.cells[cell.cell_Y-1][cell.cell_X][cell.cell_Z].ceiling
            if wall: walls.append(wall)

        return walls

    def update(self):
        delta_time = self.clock.tick() / 1000.0

        for cube in self.moving_cubes:
            cube.update(delta_time)

        colliders = [*self.walls, *self.moving_cubes]

        player_cell_x = math.floor(self.player.pos.x / CELL_SIZE)
        player_cell_z = math.floor(self.player.pos.z / CELL_SIZE)
        player_cell_y = math.floor(self.player.pos.y / WALL_HEIGHT)

        if 0 <= player_cell_x < MAZE_WIDTH and 0 <= player_cell_z < MAZE_DEPTH:
            if 0 <= player_cell_y < MAZE_LEVELS:
                player_cell = self.cells[player_cell_y][player_cell_x][player_cell_z]
                colliders.extend(self.get_walls_from_cell(player_cell))
            elif player_cell_y >= MAZE_LEVELS:
                player_cell = self.cells[MAZE_LEVELS-1][player_cell_x][player_cell_z]
                colliders.extend(self.get_walls_from_cell(player_cell))

        self.player.update(self.keys, colliders, delta_time)
        # print(self.player.pos)

    def draw_walls(self):
        for wall in self.walls:
            wall.draw()

        for level in self.cells:
            for column in level:
                for cell in column:
                    if cell.bottomWall: cell.bottomWall.draw()
                    if cell.rightWall: cell.rightWall.draw()
                    if cell.ceiling: cell.ceiling.draw()

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

        self.light.draw()

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