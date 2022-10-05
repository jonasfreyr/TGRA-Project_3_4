from pygame.locals import *

from Matrices import *
from constants import *


class Cell:
    def __init__(self, x, z):
        self.cell_X = x
        self.cell_Z = z

        self.pixel_X = x * CELL_SIZE
        self.pixel_Z = z * CELL_SIZE

        self.bottomWall = Cube(self.pixel_X, 0, self.pixel_Z, CELL_SIZE, WALL_HEIGHT, WALL_THICKNESS, (1, 1, 1))
        self.rightWall = Cube(self.pixel_X, 0, self.pixel_Z, WALL_THICKNESS, WALL_HEIGHT, CELL_SIZE, (1, 1, 1))

        self.visited = False


class Collider:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size

    def __str__(self):
        return f"MinX {self.minX} - MaxX {self.maxX}\nMinY {self.minY} - MaxY {self.maxY}\nMinZ {self.minZ} - MaxZ {self.maxZ}"

    @property
    def minX(self):
        return self.pos.x

    @property
    def maxX(self):
        return self.pos.x + self.size.x

    @property
    def minY(self):
        return self.pos.y

    @property
    def maxY(self):
        return self.pos.y + self.size.y

    @property
    def minZ(self):
        return self.pos.z

    @property
    def maxZ(self):
        return self.pos.z + self.size.z

    def points(self):
        return [
            self.pos,
            Vector(self.pos.x + self.size.x, self.pos.y,  self.pos.z),
            Vector(self.pos.x, self.pos.y + self.size.y,  self.pos.z),
            Vector(self.pos.x + self.size.x, self.pos.y + self.size.y, self.pos.z),

            Vector(self.pos.x, self.pos.y, self.pos.z + self.size.z),
            Vector(self.pos.x + self.size.x, self.pos.y, self.pos.z + self.size.z),
            Vector(self.pos.x, self.pos.y + self.size.y, self.pos.z + self.size.z),
            Vector(self.pos.x + self.size.x, self.pos.y + self.size.y, self.pos.z + self.size.z),
        ]

    def collision(self, point: "Vector"):
        return point.x > self.minX and \
               point.x < self.maxX and \
               point.y > self.minY and \
               point.y < self.maxY and \
               point.z > self.minZ and \
               point.z < self.maxZ


class Player:
    def __init__(self, x, y, z, height, radius, shader):
        self.pos = Vector(x, y, z)
        self.shader = shader
        self.rotation = 180
        self.radius = radius
        self.height = height

        self.view_matrix = ViewMatrix()
        self.projection_matrix = ProjectionMatrix()

        self.view_matrix.slide(self.pos.x, self.pos.y + height, self.pos.z)
        self.projection_matrix.set_perspective(75, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100)

        self.shader.set_view_matrix(self.view_matrix.get_matrix())
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.__last_pos = self.pos.copy()
        self.__last_rotation = 0

        self.__landed = True

        self.vel = Vector(0, 0, 0)

    def collision(self, cubes, pos):
        for box in cubes:
            cube = box.collider
            x = max(cube.minX, min(pos.x, cube.maxX))
            y = max(cube.minY, min(pos.y, cube.maxY))
            z = max(cube.minZ, min(pos.z, cube.maxZ))

            distance = math.sqrt(
                (x - pos.x) * (x - pos.x) +
                (y - pos.y) * (y - pos.y) +
                (z - pos.z) * (z - pos.z)
            )

            if distance < self.radius:
                vec = pos - Vector(x, y, z)
                try:
                    vec.normalize()
                except ZeroDivisionError:
                    pass

                vec.mul(self.radius)

                if vec.y > 0:
                    self.__landed = True
                    self.vel.y = 0

                pos = Vector(x, y, z) + vec

        return pos

    def update(self, keys, colliders, delta_time):
        if keys[K_LEFT]:    self.rotation -= PLAYER_LOOK_SPEED * delta_time
        elif keys[K_RIGHT]: self.rotation += PLAYER_LOOK_SPEED * delta_time

        move_vec = Vector(0, 0, 0)

        if keys[K_w]:   move_vec.z += -PLAYER_MOVEMENT_SPEED * delta_time
        elif keys[K_s]: move_vec.z +=  PLAYER_MOVEMENT_SPEED * delta_time

        if keys[K_a]:   move_vec.x += -PLAYER_MOVEMENT_SPEED * delta_time
        elif keys[K_d]: move_vec.x +=  PLAYER_MOVEMENT_SPEED * delta_time

        if keys[K_SPACE] and self.__landed:
            move_vec.y += PLAYER_JUMP_FORCE * delta_time
            self.__landed = False

        self.vel += move_vec.rotate2dReturn(self.rotation)

        self.vel.y -= GRAVITY * delta_time

        self.pos += self.vel
        self.vel.x = 0
        self.vel.z = 0

        temp_pos = self.pos.copy()
        temp_pos.y += self.radius

        bottom_pos = self.collision(colliders, temp_pos)
        bottom_pos.y -= self.radius

        self.pos = bottom_pos

        temp_pos = self.pos.copy()
        temp_pos.y += self.height
        top_pos = self.collision(colliders, temp_pos)
        top_pos.y -= self.height
        self.pos = top_pos

        self.update_player_camera()

    def update_player_camera(self):
        move_pos = self.pos.rotate2dReturn(-self.rotation) - self.__last_pos.rotate2dReturn(-self.rotation)
        move_rotate = self.rotation - self.__last_rotation

        self.view_matrix.slide(move_pos.x, move_pos.y, move_pos.z)

        self.view_matrix.yaw(move_rotate)

        self.__last_pos = self.pos.copy()
        self.__last_rotation = self.rotation

    def draw(self):
        self.shader.set_view_matrix(self.view_matrix.get_matrix())


class Cube(BaseCube):
    def __init__(self, x, y, z, width, height, depth, color):
        super(Cube, self).__init__()

        self.pos = Vector(x, y, z)
        self.rotation = Vector(0, 0, 0)
        self.size = Vector(width, height, depth)
        self.color = color
        self.collider = Collider(self.pos, self.size)

    def update(self, delta_time):
        pass

    def draw(self):
        shader = BaseCube.SHADER

        BaseCube.MODEL.push_matrix()
        BaseCube.MODEL.load_identity()
        BaseCube.MODEL.add_translation(self.pos.x + self.size.x / 2, self.pos.y + self.size.y / 2,
                                       self.pos.z + self.size.z / 2)
        BaseCube.MODEL.add_scale(self.size.x, self.size.y, self.size.z)
        shader.set_model_matrix(BaseCube.MODEL.matrix)
        shader.set_solid_color(*self.color)
        BaseCube.MODEL.pop_matrix()

        super(Cube, self).draw()


class MovingCube(Cube):
    def __init__(self, x, y, z, width, height, depth, color, end, speed):
        super(MovingCube, self).__init__(x, y, z, width, height, depth, color)

        self.start_point = Vector(x, y, z)
        self.end_point = end
        self.speed = speed

        self.moving_to_end = True

    def update(self, delta_time):
        going_to_point = self.start_point

        if self.moving_to_end:
            going_to_point = self.end_point

        dist_vec = going_to_point - self.pos

        if dist_vec.__len__() <= 0.1:
            self.moving_to_end = not self.moving_to_end

        else:
            dist_vec.normalize()

            self.pos += dist_vec * self.speed * delta_time
            self.collider.pos = self.pos

            # print(self.collider.pos)