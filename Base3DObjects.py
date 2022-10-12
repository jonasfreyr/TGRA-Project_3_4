import math
from math import *

from OpenGL.GL import *


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)


class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __len__(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def __str__(self):
        return f"Vec(x: {self.x}, y: {self.y}, z: {self.z})"

    def mul(self, scalar):
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar

    def normalize(self):
        length = self.__len__()

        self.x /= length
        self.y /= length
        self.z /= length

    def length2D(self):
        return sqrt(self.x * self.x + self.z * self.z)

    def normalize2D(self):
        length = self.length2D()
        self.x /= length
        self.z /= length

    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(self.y*other.z - self.z*other.y, self.z*other.x - self.x*other.z, self.x*other.y - self.y*other.x)

    def copy(self):
        return Vector(self.x, self.y, self.z)

    def rotate2d(self, angle):
        rad = math.radians(angle)

        cs = math.cos(rad)
        sn = math.sin(rad)

        px = self.x * cs - self.z * sn
        pz = self.x * sn + self.z * cs

        self.x = px
        self.z = pz

    def rotate2dXAxis(self, angle):
        rad = math.radians(angle)

        cs = math.cos(rad)
        sn = math.sin(rad)

        py = self.y * cs - self.z * sn
        pz = self.y * sn + self.z * cs

        self.y = py
        self.z = pz

    def rotate2dReturn(self, angle):
        rad = math.radians(angle)

        cs = math.cos(rad)
        sn = math.sin(rad)

        px = self.x * cs - self.z * sn
        pz = self.x * sn + self.z * cs

        return Vector(px, self.y, pz)


class BaseCube:
    SHADER = None
    MODEL = None

    def __init__(self):
        self.position_array = [-0.5, -0.5, -0.5,
                            -0.5, 0.5, -0.5,
                            0.5, 0.5, -0.5,
                            0.5, -0.5, -0.5,
                            -0.5, -0.5, 0.5,
                            -0.5, 0.5, 0.5,
                            0.5, 0.5, 0.5,
                            0.5, -0.5, 0.5,
                            -0.5, -0.5, -0.5,
                            0.5, -0.5, -0.5,
                            0.5, -0.5, 0.5,
                            -0.5, -0.5, 0.5,
                            -0.5, 0.5, -0.5,
                            0.5, 0.5, -0.5,
                            0.5, 0.5, 0.5,
                            -0.5, 0.5, 0.5,
                            -0.5, -0.5, -0.5,
                            -0.5, -0.5, 0.5,
                            -0.5, 0.5, 0.5,
                            -0.5, 0.5, -0.5,
                            0.5, -0.5, -0.5,
                            0.5, -0.5, 0.5,
                            0.5, 0.5, 0.5,
                            0.5, 0.5, -0.5]
        self.normal_array = [0.0, 0.0, -1.0,
                            0.0, 0.0, -1.0,
                            0.0, 0.0, -1.0,
                            0.0, 0.0, -1.0,
                            0.0, 0.0, 1.0,
                            0.0, 0.0, 1.0,
                            0.0, 0.0, 1.0,
                            0.0, 0.0, 1.0,
                            0.0, -1.0, 0.0,
                            0.0, -1.0, 0.0,
                            0.0, -1.0, 0.0,
                            0.0, -1.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 1.0, 0.0,
                            -1.0, 0.0, 0.0,
                            -1.0, 0.0, 0.0,
                            -1.0, 0.0, 0.0,
                            -1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0]

    def init_openGL(self, shader, model):
        if BaseCube.SHADER is None:
            BaseCube.SHADER = shader

        if BaseCube.MODEL is None:
            model.load_identity()
            BaseCube.MODEL = model

    def set_vertices(self):
        if BaseCube.SHADER is None:
            raise Exception("Not initialized")

        BaseCube.SHADER.set_position_attribute(self.position_array)
        BaseCube.SHADER.set_normal_attribute(self.normal_array)

    def draw(self):
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 4, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 8, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 12, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 16, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 20, 4)


class BaseSphere:
    SHADER = None
    MODEL = None
    def __init__(self, stacks=12, slices=24):
        self.vertex_array = []
        self.slices = slices
        stack_interval = pi / stacks
        slice_interval = 2.0 * pi / slices
        self.vertex_count = 0

        for stack_count in range(stacks):
            stack_angle = stack_count * stack_interval
            for slice_count in range(slices + 1):
                slice_angle = slice_count * slice_interval
                self.vertex_array.append(sin(stack_angle) * cos(slice_angle))
                self.vertex_array.append(cos(stack_angle))
                self.vertex_array.append(sin(stack_angle) * sin(slice_angle))

                self.vertex_array.append(sin(stack_angle + stack_interval) * cos(slice_angle))
                self.vertex_array.append(cos(stack_angle + stack_interval))
                self.vertex_array.append(sin(stack_angle + stack_interval) * sin(slice_angle))
                self.vertex_count += 2

    def init_openGL(self, shader, model):
        if BaseSphere.SHADER is None:
            BaseSphere.SHADER = shader

        if BaseSphere.MODEL is None:
            model.load_identity()
            BaseSphere.MODEL = model

    def set_vertices(self):
        if BaseSphere.SHADER is None:
            raise Exception("Not initialized")
        BaseSphere.SHADER.set_position_attribute(self.vertex_array)
        BaseSphere.SHADER.set_normal_attribute(self.vertex_array)

    def draw(self):
        for i in range(0, self.vertex_count, (self.slices + 1) * 2):
            glDrawArrays(GL_TRIANGLE_STRIP, i, (self.slices + 1) * 2)
