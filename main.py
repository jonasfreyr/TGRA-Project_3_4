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

        Cube(0, 0, 0, 0, 0, 0, WALL_COLOR).init_openGL(self.shader, model_matrix)

    def init_objects(self):
        self.walls = []

        self.player = Player(1, 0, 1, 0.5, 0.2, self.shader)

        self.lights = []

        # self.lights.append(Light(MAZE_WIDTH * CELL_SIZE, 30, MAZE_DEPTH * CELL_SIZE, light_color, self.shader))
        # self.lights.append(Light(MAZE_WIDTH * CELL_SIZE, 30, MAZE_DEPTH * CELL_SIZE, Color(0.5, 0, 0, 0, 2), self.shader))

        # self.walls.append(Cube(10, 0, 10, 20, 4, 1, (0, 1, 0)))
        # self.walls.append(Cube(10, 0, 20, 20, 4, 1, (1, 0, 0)))

        self.moving_cubes = []

        # self.moving_cubes.append(MovingCube(5, 1, 5, 1, 1, 1, (0, 0, 1), Vector(10, 2, 10), 1))
        # self.moving_cubes.append(MovingCube(10, 0, 5, 1, 1, 1, (0, 0, 1), Vector(10, 0, 10), 1))

        self.cells = [[[Cell(x, z, y) for z in range(MAZE_DEPTH)] for x in range(MAZE_WIDTH)] for y in
                      range(MAZE_LEVELS)]

        self.start_point = self.cells[0][random.randint(0, MAZE_WIDTH - 1)][random.randint(0, MAZE_DEPTH - 1)]
        self.goal_points = {self.start_point}

        self.player.pos = Vector(self.start_point.pixel_X + CELL_SIZE / 2, 0, self.start_point.pixel_Z + CELL_SIZE / 2)

        # self.player.pos.y = MAZE_LEVELS * WALL_HEIGHT + 0.5

        # self.player.pos.x = 50
        # self.player.pos.z = 50
        # self.base_cube = BaseCube

        last_goal = self.start_point
        for level in range(MAZE_LEVELS):
            last_goal = self.generate_map(last_goal, level)

            posx, posz, sizex, sizez = self._remove_ceiling(last_goal)

            # print("After:", elevator.pos)

            elevator = MovingCube(posx, last_goal.pixel_Y, posz,
                       sizex, ELEVATOR_THICKNESS, sizez, ELEVATOR_COLOR,
                       Vector(posx, last_goal.pixel_Y + WALL_HEIGHT + FLOOR_THICKNESS,
                              posz), 0.1)

            self.moving_cubes.append(elevator)

            self.lights.append(Light(posx + CELL_SIZE / 2, last_goal.pixel_Y + WALL_HEIGHT / 2, posz + CELL_SIZE / 2, ELEVATOR_COLOR, self.shader))

            if last_goal.cell_Y < MAZE_LEVELS-1:
                last_goal = self.cells[level+1][last_goal.cell_X][last_goal.cell_Z]
                self.goal_points.add(last_goal)

        for left in range(MAZE_DEPTH):
            for level in range(MAZE_LEVELS):
                self.walls.append(Cube(left * CELL_SIZE, (level * WALL_HEIGHT) + (FLOOR_THICKNESS * level), MAZE_DEPTH * CELL_SIZE, CELL_SIZE, WALL_HEIGHT + FLOOR_THICKNESS, WALL_THICKNESS, WALL_COLOR))

        for top in range(MAZE_WIDTH):
            for level in range(MAZE_LEVELS):
                self.walls.append(Cube(MAZE_WIDTH * CELL_SIZE, (level * WALL_HEIGHT) + (FLOOR_THICKNESS * level), top * CELL_SIZE, WALL_THICKNESS, WALL_HEIGHT + FLOOR_THICKNESS,  CELL_SIZE, WALL_COLOR))

        for x in range(MAZE_WIDTH):
            for z in range(MAZE_DEPTH):
                self.walls.append(Cube(x * CELL_SIZE, -1, z * CELL_SIZE, CELL_SIZE, 1, CELL_SIZE, FLOOR_COLOR))

        x = random.randint(0, MAZE_WIDTH * CELL_SIZE)
        z = random.randint(0, MAZE_DEPTH * CELL_SIZE)
        y = MAZE_LEVELS * WALL_HEIGHT + FLOOR_THICKNESS + WALL_HEIGHT / 2

        self.reward = Reward(x, y, z, 0.3, REWARD_COLOR, 0.1)
        self.moving_cubes.append(self.reward)

    def _remove_ceiling(self, cell):
        posx = cell.pixel_X + WALL_THICKNESS
        posz = cell.pixel_Z + WALL_THICKNESS

        sizex = CELL_SIZE - WALL_THICKNESS
        sizez = CELL_SIZE - WALL_THICKNESS

        if cell.rightWall is not None:
            cell.rightWall.size.y += FLOOR_THICKNESS
            cell.rightWall.calculate_initial_matrix()

        else:
            posx -= WALL_THICKNESS
            sizex += WALL_THICKNESS

        if cell.bottomWall is not None:
            cell.bottomWall.size.y += FLOOR_THICKNESS
            cell.bottomWall.calculate_initial_matrix()

        else:
            posz -= WALL_THICKNESS
            sizez += WALL_THICKNESS

        cell.ceiling = None

        return posx, posz, sizex, sizez

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
        # self.walls.append(Cube(50, 1, 50, 1, 1, 1, WHITE_COLOR))

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

                # Walls from the lower cell
                if player_cell_y > 0:
                    lower_cell = self.cells[player_cell_y-1][player_cell_x][player_cell_z]
                    colliders.extend(self.get_walls_from_cell(lower_cell))

                # Walls from the above cell
                if player_cell_y < MAZE_LEVELS-1:
                    higher_cell = self.cells[player_cell_y+1][player_cell_x][player_cell_z]
                    colliders.extend(self.get_walls_from_cell(higher_cell))

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

        # self.lights[0].pos = self.player.top_pos

        lights = []

        pos = self.player.top_pos
        c = Color(0.2, 0.2, 0.2, 0, 2)

        c.mat_specular = Vector(1, 1, 1)

        lights.append(Light(pos.x, pos.y, pos.z, c, self.shader))

        if self.player.top_pos.y // WALL_HEIGHT >= MAZE_LEVELS and not self.reward.collected: lights.append(self.reward.light)

        for light in self.lights:
            if light.pos.y // WALL_HEIGHT == self.player.top_pos.y // WALL_HEIGHT:
                lights.append(light)

        Light(0, 0, 0, Color(0, 0, 0, 0, 1), self.shader).reset()
        for i, light in enumerate(lights):
            light.draw(i)

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