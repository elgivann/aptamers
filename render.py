import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
from pyrr import matrix44, Vector3, vector
from mymath import * 
from camera import Camera

class Render:
    vertexSrc = """
    #version 330
    layout(location = 0) in vec3 a_pos;
    uniform mat4 a_mat;
    void main()
    {
        gl_Position = a_mat * vec4(a_pos, 1.0);
    }
    """

    fragSrc = """
    #version 330
    uniform vec4 a_color;
    out vec4 out_color;
    void main()
    {
        out_color = a_color;
    }
    """""
    
    def __init__(self, camera, fov=45, width = 800, height = 600, clearColor = Color.BLACK):
        self.VAOs = []
        self.indicesLengths = []
        self.models = [] 
        self.camera = camera
        self.fov = fov
        self.width = width
        self.height = height
        self.clearColor = clearColor

    def init(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(
            self.clearColor.red,
            self.clearColor.green,
            self.clearColor.blue, 
            self.clearColor.alpha
        )
        
        self.resize(self.width, self.height)
        self.program = compileProgram(
            compileShader(self.vertexSrc, GL_VERTEX_SHADER),
            compileShader(self.fragSrc, GL_FRAGMENT_SHADER)
        )
        self.colorLocation = glGetUniformLocation(self.program, "a_color")
        self.matrixLocation = glGetUniformLocation(self.program, "a_mat")
        glUseProgram(self.program)

        for i in range(3):
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)
            if(i == Model.cube):
                vertices, indices = Mesh.genCube()
            elif(i == Model.cylinder):
                vertices, indices = Mesh.genCylinder(5)
            elif(i == Model.sphere):
                vertices, indices = Mesh.genSphere(8)
            self.VAOs.append(vao)
            self.indicesLengths.append(len(indices))

            vertices = np.array(vertices, dtype=np.float32)
            indices = np.array(indices, dtype=np.uint32)
            glBindBuffer(GL_ARRAY_BUFFER, glGenBuffers(1))
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, glGenBuffers(1))
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0)) 
            glBindVertexArray(0)
        self.camera.update()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        view = self.camera.view
        for m in self.models:
            mvp = matrix44.multiply(m.transform, view) 
            mvp = matrix44.multiply(mvp, self.proj) 
            glUniform4fv(self.colorLocation, 1, m.color.toArray())     
            glUniformMatrix4fv(self.matrixLocation, 1, GL_FALSE, mvp)
            glBindVertexArray(self.VAOs[m.primitive])
            glDrawElements(GL_TRIANGLES, self.indicesLengths[m.primitive], GL_UNSIGNED_INT, None)
            glBindVertexArray(0)

    def resize(self, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        self.proj = matrix44.create_perspective_projection_matrix(
            self.fov, width/height, 0.1, 10000)

    def clearScene(self):
        self.models = []
        
    def scaleModels(self, scale):
        for m in self.models:
            s = matrix44.create_from_scale(Vector3([scale, scale, scale]))
            if(m.primitive == Model.cylinder):
                s = matrix44.create_from_scale(Vector3([scale, 1, scale]))
            m.transform = matrix44.multiply(s, m.transform)

class Model:
    def __init__(self, primitive=0,  pos = Vec3(), color = Color.WHITE, scale = 1.0):
        self.primitive = primitive
        self.pos = pos
        self.color = color        
        t = matrix44.create_from_translation(Vector3(pos.toArray()))
        s = matrix44.create_from_scale(Vector3([scale, scale, scale]))
        self.transform = matrix44.multiply(s, t)
    
Model.cube = 0
Model.cylinder = 1
Model.sphere = 2


