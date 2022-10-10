
from OpenGL.GL import *
from math import * # trigonometry

import sys

from Base3DObjects import *

class Shader3D:
    def __init__(self):
        vert_shader = glCreateShader(GL_VERTEX_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.vert")
        glShaderSource(vert_shader,shader_file.read())
        shader_file.close()
        glCompileShader(vert_shader)
        result = glGetShaderiv(vert_shader, GL_COMPILE_STATUS)
        if (result != 1): # shader didn't compile
            print("Couldn't compile vertex shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(vert_shader)))

        frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.frag")
        glShaderSource(frag_shader,shader_file.read())
        shader_file.close()
        glCompileShader(frag_shader)
        result = glGetShaderiv(frag_shader, GL_COMPILE_STATUS)
        if (result != 1): # shader didn't compile
            print("Couldn't compile fragment shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(frag_shader)))

        self.renderingProgramID = glCreateProgram()
        glAttachShader(self.renderingProgramID, vert_shader)
        glAttachShader(self.renderingProgramID, frag_shader)
        result = glLinkProgram(self.renderingProgramID)
        if (result != 1):
            print("Couldn't link program\nProgram link Log:\n" + str(glGetProgramInfoLog(self.renderingProgramID)))


        self.positionLoc			= glGetAttribLocation(self.renderingProgramID, "a_position")
        glEnableVertexAttribArray(self.positionLoc)

        self.normalLoc = glGetAttribLocation(self.renderingProgramID, "a_normal")
        glEnableVertexAttribArray(self.normalLoc)

        ## ADD CODE HERE ##

        self.modelMatrixLoc			= glGetUniformLocation(self.renderingProgramID, "u_model_matrix")
        # self.projectionViewMatrixLoc			= glGetUniformLocation(self.renderingProgramID, "u_projection_view_matrix")

        self.projectionMatrixLoc = glGetUniformLocation(self.renderingProgramID, "u_projection_matrix")
        self.viewMatrixLoc = glGetUniformLocation(self.renderingProgramID, "u_view_matrix")

        self.numOfLightsLoc = glGetUniformLocation(self.renderingProgramID, "u_NUM_OF_LIGHTS")

        # self.colorLoc = glGetUniformLocation(self.renderingProgramID, "u_color")

        # self.lightPosLoc = glGetUniformLocation(self.renderingProgramID, "u_light_positions")
        # self.lightDifLoc = glGetUniformLocation(self.renderingProgramID, "u_light_diffuse")
        self.matDifLoc = glGetUniformLocation(self.renderingProgramID, "u_material_diffuse")

        self.cameraPosLoc = glGetUniformLocation(self.renderingProgramID, "u_camera_position")
        # self.lightSpecLoc = glGetUniformLocation(self.renderingProgramID, "u_light_specular")
        self.matSpecLoc = glGetUniformLocation(self.renderingProgramID, "u_material_specular")
        self.shininessLoc = glGetUniformLocation(self.renderingProgramID, "u_shininess")

        # self.lightAmbientLoc = glGetUniformLocation(self.renderingProgramID, "u_light_ambient")
        self.matAmbientLoc = glGetUniformLocation(self.renderingProgramID, "u_material_ambient")

    def use(self):
        try:
            glUseProgram(self.renderingProgramID)
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.renderingProgramID))
            raise

    def set_model_matrix(self, matrix_array):
        glUniformMatrix4fv(self.modelMatrixLoc, 1, True, matrix_array)

    def set_projection_matrix(self, matrix_array):
        glUniformMatrix4fv(self.projectionMatrixLoc, 1, True, matrix_array)

    def set_view_matrix(self, matrix_array):
        glUniformMatrix4fv(self.viewMatrixLoc, 1, True, matrix_array)

    def set_position_attribute(self, vertex_array):
        glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 0, vertex_array)

    ## ADD CODE HERE ##
    def set_normal_attribute(self, vertex_array):
        glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 0, vertex_array)

    ## Diffuse
    def set_light_position(self, x, y, z, i):
        loc = glGetUniformLocation(self.renderingProgramID, f"u_light_positions[{i}]")
        glUniform4f(loc, x, y, z, 1.0)

    def set_material_diffuse(self, r, g, b):
        glUniform4f(self.matDifLoc, r, g, b, 0.0)

    def set_light_diffuse(self, r, g, b, i):
        loc = glGetUniformLocation(self.renderingProgramID, f"u_light_diffuses[{i}]")
        glUniform4f(loc, r, g, b, 0.0)

    ## Specular
    def set_camera_position(self, x, y, z):
        glUniform4f(self.cameraPosLoc, x, y, z, 1.0)

    def set_light_specular(self, r, g, b, i):
        loc = glGetUniformLocation(self.renderingProgramID, f"u_light_speculars[{i}]")
        glUniform4f(loc, r, g, b, 0.0)

    def set_material_specular(self, r, g, b):
        glUniform4f(self.matSpecLoc, r, g, b, 0.0)

    def set_shininess(self, shininess):
        glUniform1f(self.shininessLoc, shininess)

    ## Ambient
    def set_light_ambient(self, r, g, b, i):
        loc = glGetUniformLocation(self.renderingProgramID, f"u_light_ambients[{i}]")
        glUniform4f(loc, r, g, b, 0.0)

    def set_material_ambient(self, r, g, b):
        glUniform4f(self.matAmbientLoc, r, g, b, 0.0)
