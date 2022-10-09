from pygame.locals import *

from Matrices import *
from constants import *


class Cell:
    def __init__(self, x, z, y):
        self.cell_X = x
        self.cell_Z = z
        self.cell_Y = y

        self.pixel_X = x * CELL_SIZE
        self.pixel_Z = z * CELL_SIZE
        self.pixel_Y = (y * WALL_HEIGHT) + (FLOOR_THICKNESS * y)

        self.bottomWall = Cube(self.pixel_X, self.pixel_Y, self.pixel_Z, CELL_SIZE,
                               WALL_HEIGHT, WALL_THICKNESS, WHITE_COLOR)
        self.rightWall = Cube(self.pixel_X, self.pixel_Y, self.pixel_Z, WALL_THICKNESS,
                              WALL_HEIGHT, CELL_SIZE, WHITE_COLOR)
        self.ceiling = Cube(self.pixel_X, self.pixel_Y + WALL_HEIGHT, self.pixel_Z, CELL_SIZE,
                            FLOOR_THICKNESS, CELL_SIZE, GREEN_COLOR)

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
            Vector(self.pos.x + self.size.x, self.pos.y, self.pos.z),
            Vector(self.pos.x, self.pos.y + self.size.y, self.pos.z),
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
        self.rotation = 0
        self.y_rotation = 0
        self.radius = radius
        self.height = height

        self.view_matrix = ViewMatrix()
        self.projection_matrix = ProjectionMatrix()

        self.view_matrix.slide(self.pos.x, self.pos.y + height, self.pos.z)
        self.projection_matrix.set_perspective(75, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 50)

        self.shader.set_view_matrix(self.view_matrix.get_matrix())
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.__landed = True

        self.vel = Vector(0, 0, 0)

    @property
    def top_pos(self):
        temp = self.pos.copy()
        temp.y += self.height

        return temp

    def collision(self, cubes, pos):
        for box in cubes:
            closest_pos, move_vec = box.collide(pos, self.radius)

            if move_vec.y > 0:
                self.__landed = True
                self.vel.y = 0

            elif move_vec.y < 0:
                self.vel.y = 0

            pos = closest_pos + move_vec

        return pos

    def update(self, keys, colliders, delta_time):
        if keys[K_LEFT]:
            self.rotation -= PLAYER_LOOK_SPEED * delta_time
            # self.look_pos.x -= PLAYER_LOOK_SPEED * delta_time
        elif keys[K_RIGHT]:
            self.rotation += PLAYER_LOOK_SPEED * delta_time
            # self.look_pos.x += PLAYER_LOOK_SPEED * delta_time

        if keys[K_UP]:
            self.y_rotation += PLAYER_LOOK_SPEED * delta_time
            if self.y_rotation >= 45: self.y_rotation = 45

        elif keys[K_DOWN]:
            self.y_rotation -= PLAYER_LOOK_SPEED * delta_time
            if self.y_rotation <= -45: self.y_rotation = -45

        move_vec = Vector(0, 0, 0)

        if keys[K_w]:
            move_vec.z += -PLAYER_MOVEMENT_SPEED * delta_time
        elif keys[K_s]:
            move_vec.z += PLAYER_MOVEMENT_SPEED * delta_time

        if keys[K_a]:
            move_vec.x += -PLAYER_MOVEMENT_SPEED * delta_time
        elif keys[K_d]:
            move_vec.x += PLAYER_MOVEMENT_SPEED * delta_time

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

        # temp_pos = self.pos.copy()
        # temp_pos.y += self.height
        temp_pos = self.top_pos
        top_pos = self.collision(colliders, temp_pos)
        top_pos.y -= self.height
        self.pos = top_pos

        self.update_player_camera()

    def update_player_camera(self):
        # move_pos = self.pos.rotate2dReturn(-self.rotation) - self.__last_pos.rotate2dReturn(-self.rotation)
        # move_rotate = self.rotation - self.__last_rotation

        # self.view_matrix.slide(move_pos.x, move_pos.y, move_pos.z)

        temp = self.pos.copy()
        temp.y += self.height
        # self.view_matrix.eye = temp

        look_pos = Vector(0, 0, -1)

        look_pos.rotate2dXAxis(self.y_rotation)
        look_pos.rotate2d(self.rotation)

        self.view_matrix.look(temp, temp + look_pos, Vector(0, 1, 0))

        # self.view_matrix.yaw(move_rotate)

        # self.__last_rotation = self.rotation

    def draw(self):
        self.shader.set_camera_position(self.pos.x, self.pos.y, self.pos.z)
        self.shader.set_view_matrix(self.view_matrix.get_matrix())


class Light:
    def __init__(self, x, y, z, color, shader):
        self.pos = Vector(x, y, z)
        self.color = color
        self.shader = shader

    @property
    def pos_array(self):
        return self.pos.x, self.pos.y, self.pos.z

    def draw(self):
        self.shader.set_light_position(*self.pos_array)
        self.shader.set_light_diffuse(*self.color.diffuse)
        self.shader.set_light_specular(*self.color.specular)
        self.shader.set_light_ambient(*self.color.ambient)


class Color:
    def __init__(self, r, g, b, s, ambient_factor):
        self.mat_diffuse = Vector(r, g, b)
        self.mat_specular = Vector(1, 1, 1)
        self.mat_ambient = Vector(r / ambient_factor, g / ambient_factor, b / ambient_factor)
        self.shininess = s

    @property
    def diffuse(self):
        return self.mat_diffuse.x, self.mat_diffuse.y, self.mat_diffuse.z

    @property
    def specular(self):
        return self.mat_specular.x, self.mat_specular.y, self.mat_specular.z

    @property
    def ambient(self):
        return self.mat_ambient.x, self.mat_ambient.y, self.mat_ambient.z


class Cube(BaseCube):
    def __init__(self, x, y, z, width, height, depth, color):
        super(Cube, self).__init__()

        self.pos = Vector(x, y, z)
        self.rotation = Vector(0, 0, 0)
        self.size = Vector(width, height, depth)
        self.color = color
        self.collider = Collider(self.pos, self.size)

        self.calculate_initial_matrix()

    def calculate_initial_matrix(self):
        if BaseCube.MODEL:
            BaseCube.MODEL.push_matrix()
            BaseCube.MODEL.load_identity()
            BaseCube.MODEL.add_translation(self.pos.x + self.size.x / 2, self.pos.y + self.size.y / 2,
                                           self.pos.z + self.size.z / 2)
            BaseCube.MODEL.add_scale(self.size.x, self.size.y, self.size.z)
            BaseCube.MODEL.add_rotation(self.rotation.x, self.rotation.y, self.rotation.z)
            self.matrix = BaseCube.MODEL.matrix
            BaseCube.MODEL.pop_matrix()

    def collide(self, pos, radius):
        cube = self.collider
        x = max(cube.minX, min(pos.x, cube.maxX))
        y = max(cube.minY, min(pos.y, cube.maxY))
        z = max(cube.minZ, min(pos.z, cube.maxZ))

        distance = math.sqrt(
            (x - pos.x) * (x - pos.x) +
            (y - pos.y) * (y - pos.y) +
            (z - pos.z) * (z - pos.z)
        )

        if distance < radius:
            vec = pos - Vector(x, y, z)
            try:
                vec.normalize()
            except ZeroDivisionError:
                pass

            vec.mul(radius)

            return Vector(x, y, z), vec
        return pos, Vector(0, 0, 0)

    def update(self, delta_time):
        pass

    def draw(self):
        shader = BaseCube.SHADER
        shader.set_model_matrix(self.matrix)
        # shader.set_solid_color(*self.color)

        shader.set_material_diffuse(*self.color.diffuse)
        shader.set_material_specular(*self.color.specular)
        shader.set_material_ambient(*self.color.ambient)
        shader.set_shininess(self.color.shininess)

        super(Cube, self).draw()


class MovingCube(Cube):
    def __init__(self, x, y, z, width, height, depth, color, end, speed):
        super(MovingCube, self).__init__(x, y, z, width, height, depth, color)

        self.start_point = Vector(x, y - height, z)
        end.y -= height
        self.end_point = end
        self.speed = speed

        self.moving_to_end = True

    def update(self, delta_time):
        going_to_point = self.start_point

        if self.moving_to_end:
            going_to_point = self.end_point

        dist_vec = going_to_point - self.pos

        if dist_vec.__len__() <= 0.01:
            self.moving_to_end = not self.moving_to_end

        else:
            dist_vec.normalize()

            self.pos += dist_vec * self.speed * delta_time
            self.collider.pos = self.pos

            # print(self.collider.pos)

    def draw(self):
        self.calculate_initial_matrix()

        super(MovingCube, self).draw()


class Reward(MovingCube):
    def __init__(self, x, y, z, size, color, bobbing_speed):
        end_point = Vector(x, y + size, z)
        super(Reward, self).__init__(x, y, z, size / 2, size, size / 2, color, end_point, bobbing_speed)

        self.rotation = Vector(90, 45, 45)

        self.collected = False

    def update(self, delta_time):
        self.rotation.z += REWARD_ROTATION_SPEED * delta_time
        self.rotation.x += REWARD_ROTATION_SPEED * delta_time
        self.rotation.y += REWARD_ROTATION_SPEED * delta_time
        super(Reward, self).update(delta_time)

    def collide(self, pos, radius):
        _, move_vec = super(Reward, self).collide(pos, radius)

        if move_vec.__len__() > 0: self.collected = True

        return pos, Vector(0, 0, 0)

    def draw(self):
        if not self.collected:
            super(Reward, self).draw()

WHITE_COLOR = Color(1, 1, 1, 100, 10)
GREEN_COLOR = Color(0, 0.5, 0, 100, 10)
BLUE_COLOR = Color(0, 0, 1, 100, 10)
RED_COLOR = Color(1, 0, 0, 100, 10)
GOLD_COLOR = Color(4, 4, 0, 2, 10)
