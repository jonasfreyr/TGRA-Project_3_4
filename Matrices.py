import math
from math import * # trigonometry

from Base3DObjects import *


class ModelMatrix:
    def __init__(self):
        self.matrix = [ 1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1 ]
        self.stack = []
        self.stack_count = 0
        self.stack_capacity = 0

    def load_identity(self):
        self.matrix = [ 1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1 ]

    def copy_matrix(self):
        new_matrix = [0] * 16
        for i in range(16):
            new_matrix[i] = self.matrix[i]
        return new_matrix

    def add_transformation(self, matrix2):
        counter = 0
        new_matrix = [0] * 16
        for row in range(4):
            for col in range(4):
                for i in range(4):
                    new_matrix[counter] += self.matrix[row*4 + i]*matrix2[col + 4*i]
                counter += 1
        self.matrix = new_matrix

    def add_translation(self, x, y, z):
        matrix = [1, 0, 0, x,
                  0, 1, 0, y,
                  0, 0, 1, z,
                  0, 0, 0, 1]

        self.add_transformation(matrix)

    def add_scale(self, x, y, z):
        matrix = [x, 0, 0, 0,
                  0, y, 0, 0,
                  0, 0, z, 0,
                  0, 0, 0, 1]

        self.add_transformation(matrix)

    def add_rotation(self, x, y, z):
        x = math.radians(x)
        y = math.radians(y)
        z = math.radians(z)

        matrix_x = [1, 0, 0, 0,
                    0, cos(x), -sin(x), 0,
                    0, sin(x), cos(x), 0,
                    0, 0, 0, 1]

        matrix_y = [cos(y), 0, sin(y), 0,
                    0, 1, 0, 0,
                    -sin(y), 0, cos(y), 0,
                    0, 0, 0, 1]

        matrix_z = [cos(z), -sin(z), 0, 0,
                    sin(z), cos(z), 0, 0,
                    0, 0, 1, 0,
                    0, 0, 0, 1]

        self.add_transformation(matrix_x)
        self.add_transformation(matrix_y)
        self.add_transformation(matrix_z)

    def add_nothing(self):
        other_matrix = [1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1]
        self.add_transformation(other_matrix)

    ## MAKE OPERATIONS TO ADD TRANLATIONS, SCALES AND ROTATIONS ##
    # ---

    # YOU CAN TRY TO MAKE PUSH AND POP (AND COPY) LESS DEPENDANT ON GARBAGE COLLECTION
    # THAT CAN FIX SMOOTHNESS ISSUES ON SOME COMPUTERS
    def push_matrix(self):
        self.stack.append(self.copy_matrix())

    def pop_matrix(self):
        self.matrix = self.stack.pop()

    # This operation mainly for debugging
    def __str__(self):
        ret_str = ""
        counter = 0
        for _ in range(4):
            ret_str += "["
            for _ in range(4):
                ret_str += " " + str(self.matrix[counter]) + " "
                counter += 1
            ret_str += "]\n"
        return ret_str



# The ViewMatrix class holds the camera's coordinate frame and
# set's up a transformation concerning the camera's position
# and orientation

class ViewMatrix:
    def __init__(self):
        self.eye = Point(0, 0, 0)
        self.u = Vector(1, 0, 0)
        self.v = Vector(0, 1, 0)
        self.n = Vector(0, 0, 1)

    def look(self, eye, center, up):
        self.eye = eye
        self.n = eye - center
        self.n.normalize()

        self.u = up.cross(self.n)
        self.v = self.n.cross(self.u)

    def slide(self, delU, delV, delN):
        self.eye.x += delU * self.u.x + delV * self.v.x + delN * self.n.x
        self.eye.y += delU * self.u.y + delV * self.v.y + delN * self.n.y
        self.eye.z += delU * self.u.z + delV * self.v.z + delN * self.n.z

    def roll(self, angle):
        angle = radians(angle)
        angCos = cos(angle)
        angSin = sin(angle)


        t = self.u.copy()
        self.u = (t * angCos) + (self.v * angSin)
        self.v = (t * -angSin) + (self.v * angCos)

    def yaw(self, angle):
        angle = radians(angle)
        angCos = cos(angle)
        angSin = sin(angle)

        t = self.u.copy()
        self.u = (t * angCos) + (self.n * angSin)
        self.n = (t * -angSin) + (self.n * angCos)

    def pitch(self, angle):
        angle = radians(angle)
        angCos = cos(angle)
        angSin = sin(angle)

        t = self.v.copy()
        self.v = (t * angCos) + (self.n * angSin)
        self.n = (t * -angSin) + (self.n * angCos)

    def get_matrix(self):
        minusEye = Vector(-self.eye.x, -self.eye.y, -self.eye.z)
        return [self.u.x, self.u.y, self.u.z, minusEye.dot(self.u),
                self.v.x, self.v.y, self.v.z, minusEye.dot(self.v),
                self.n.x, self.n.y, self.n.z, minusEye.dot(self.n),
                0,        0,        0,        1]


# The ProjectionMatrix class builds transformations concerning
# the camera's "lens"

class ProjectionMatrix:
    def __init__(self):
        self.left = -1
        self.right = 1
        self.bottom = -1
        self.top = 1
        self.near = -1
        self.far = 1

        self.is_orthographic = False

    ## MAKE OPERATION TO SET PERSPECTIVE PROJECTION (don't forget to set is_orthographic to False) ##
    # ---

    def set_orthographic(self, left, right, bottom, top, near, far):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.near = near
        self.far = far
        self.is_orthographic = True

    def set_perspective(self, fovy, aspect, N, F):
        fovy = radians(fovy)

        self.top = N * tan(fovy / 2)
        self.bottom = -self.top
        self.right = self.top * aspect
        self.left = -self.right
        self.near = N
        self.far = F

    def get_matrix(self):
        if self.is_orthographic:
            A = 2 / (self.right - self.left)
            B = -(self.right + self.left) / (self.right - self.left)
            C = 2 / (self.top - self.bottom)
            D = -(self.top + self.bottom) / (self.top - self.bottom)
            E = 2 / (self.near - self.far)
            F = (self.near + self.far) / (self.near - self.far)

            return [A,0,0,B,
                    0,C,0,D,
                    0,0,E,F,
                    0,0,0,1]

        else:
            # Set up a matrix for a Perspective projection
            ###  Remember that it's a non-linear transformation   ###
            ###  so the bottom row is different                   ###

            _0_0 = (2 * self.near) / (self.right - self.left)
            _0_2 = (self.right + self.left) / (self.right - self.left)
            _1_1 = (2 * self.near) / (self.top - self.bottom)
            _1_2 = (self.top + self.bottom) / (self.top - self.bottom)
            _2_2 = -(self.far + self.near) / (self.far - self.near)
            _2_3 = (-2 * self.far * self.near) / (self.far - self.near)

            return [_0_0, 0,    _0_2, 0,
                    0,    _1_1, _1_2, 0,
                    0,    0,    _2_2, _2_3,
                    0,    0,    -1,   0]



# The ProjectionViewMatrix returns a hardcoded matrix
# that is just used to get something to send to the
# shader before you properly implement the ViewMatrix
# and ProjectionMatrix classes.
# Feel free to throw it away afterwards!

class ProjectionViewMatrix:
    def __init__(self):
        pass

    def get_matrix(self):
        return [ 0.45052942369783683,  0.0,  -0.15017647456594563,  0.0,
                -0.10435451285616304,  0.5217725642808152,  -0.3130635385684891,  0.0,
                -0.2953940042189954,  -0.5907880084379908,  -0.8861820126569863,  3.082884480118567,
                -0.2672612419124244,  -0.5345224838248488,  -0.8017837257372732,  3.7416573867739413 ]


# IDEAS FOR OPERATIONS AND TESTING:
# if __name__ == "__main__":
#     matrix = ModelMatrix()
#     matrix.push_matrix()
#     print(matrix)
#     matrix.add_translation(3, 1, 2)
#     matrix.push_matrix()
#     print(matrix)
#     matrix.add_scale(2, 3, 4)
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
    
#     matrix.add_translation(5, 5, 5)
#     matrix.push_matrix()
#     print(matrix)
#     matrix.add_scale(3, 2, 3)
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
    
#     matrix.pop_matrix()
#     print(matrix)
        
#     matrix.push_matrix()
#     matrix.add_scale(2, 2, 2)
#     print(matrix)
#     matrix.push_matrix()
#     matrix.add_translation(3, 3, 3)
#     print(matrix)
#     matrix.push_matrix()
#     matrix.add_rotation_y(pi / 3)
#     print(matrix)
#     matrix.push_matrix()
#     matrix.add_translation(1, 1, 1)
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
    
