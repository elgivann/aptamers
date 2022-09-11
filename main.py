import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import sys
import numpy as np
from pyrr import matrix44, Vector3, vector, Matrix44
from math import radians, cos, sin, pi, inf
from mymath import * 
from camera import Camera
from render import Render, Model


class Mouse:
    x = 0
    y = 0
    dx = 0
    dy = 0
    sensitivity = 0.1
    invertedY = False
    mouseFirst = True
    leftClick = False
    rightClick = False
    lastScroll = 0
    scroll = 0
    def __init__(self, sensitivity = 0.1, invertedY = False):
        self.sensitivity = sensitivity
        self.invertedY = invertedY  

    def update(self, window):
        p = glfw.get_cursor_pos(window)
        self.leftClick = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT)
        self.rightClick = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT)

        if(self.mouseFirst):
            lastX = p[0] 
            lastY = p[1] 
            self.mouseFirst = False
        else:
            lastX = self.x
            lastY = self.y
        self.x = p[0]
        self.y = p[1]
        self.dx = (lastX - self.x) * self.sensitivity
        self.dy = (lastY - self.y) * self.sensitivity
        if(self.invertedY):
            self.dy *= -1

    def __str__(self):
        return str(self.dx) + ", " + str(self.dy)

worldUp = Vec3(0,1,0)
cam = Camera(Vec3(), 10, 0, 0) 
cam.rotSpeed = 3
cam.zoomSpeed = 2000
cam.minDistance = 2
cam.worldUp = worldUp
render = Render(cam, 45, 1280, 720, Color(0.15,0.15,0.15))
mouse = Mouse(0.6, True)    
hasLoadedKinFile = False
animated = False

def loadKinFile(path):
    try:
        file = open(path)
        lines = file.readlines()
    except FileNotFoundError:
        raise Exception("Failure to load file " + path)
    
    points = {}
    polygons = []    
    polygon = []
    basepairs = []
    isBasePair = False

    for line in lines:
        if(line.startswith("@vectorlist {basepairs}")):
            isBasePair = True
        if(line.startswith("@vectorlist {RNA backbone}")):
            isBasePair = False
        if(line[0] != '{'):
            continue
        s = ""
        index = 0
        p = Vec3()
        id = -1
        startPoint = False
        flag = False
        for char in line:
            if(char == 'P'):
                startPoint = True
            if((char >= '0' and char <= '9') or char == '-' or char == '.'):
                flag = True
                s += char
            elif(flag):
                flag = False
                if(index == 0):
                    id = int(s)
                elif(index == 1):
                    p.x = float(s)    
                elif(index == 2):
                    p.y = float(s)
                elif(index == 3):
                    p.z = float(s)
                s = ""
                index += 1
        if not id in points.keys():
            points[id] = p    
        if startPoint:
            polygons.append(polygon)         
            polygon = []
            basepairs.append(isBasePair)
        polygon.append(id)
    polygons.append(polygon)         
    del polygons[0]         
    return points, polygons, basepairs

def loadCtFile(path):
    try:
        file = open(path)
        lines = file.readlines()
    except FileNotFoundError:
        raise Exception("Failure to load file " + path)
    bases = {}
    del lines[0] 
    for line in lines:
        s = ""
        for char in line:
            if(char >= "0" and char <= "9"):
                s += char   
            elif(char == 'A' or char == 'C' or char == 'U' or char == 'G' or char == 'T'):
                index = int(s)
                bases[index] = char        
                break
                
    return bases

def makeLink(p1, p2, s):
    c = Model(Model.cylinder, Vec3(), Color.DARKWHITE)
    d = p1 - p2
    m = d * 0.5
    f = d.normalize()
    r = worldUp.cross(d).toNormal()
    u = d.cross(r).toNormal()

    l = d.length()/2
    c.transform = Matrix44([
        s*r.x,s*r.y,s*r.z,0, 
        l*f.x,l*f.y,l*f.z,0, 
        s*u.x,s*u.y,s*u.z,0,  
        p2.x + m.x, p2.y + m.y, p2.z + m.z,1
    ])  
    return c

def createScene(path):
    global baseModels, hasLoadedKinFile 
    hasLoadedKinFile = True
    baseModels = {}
    render.clearScene()
    points, polygons, basepairs = loadKinFile(path)
    #Create Points in space for k,v in points.items():
    for k,v in points.items():
        m = Model(Model.sphere, v, Color.DARKRED, 40)
        baseModels[k] = m
        render.models.append(m)
   
    #Link Points  
    for i in range(len(polygons)):
        polygon = polygons[i]
        if(basepairs[i]):
            scaler = 4
        else:
            scaler = 10
        lastPoint = points[polygon[0]]
        for j in range(1, len(polygon)):
            p = points[polygon[j]]
            linkModel = makeLink(lastPoint, p, scaler)
            render.models.append(linkModel)
            lastPoint = p 
    cam.distance = 1000
    cam.pitch = 0
    cam.yaw = -pi/2

def colorBases(path):
    bases = loadCtFile(path)
    for k,v in bases.items():
        color = Color.DARKRED
        if v == 'A':
            color = Color.DARKBLUE 
        elif v == 'C':
            color = Color.DARKYELLOW
        elif v == 'G':
            color = Color.DARKGREEN
        elif v == 'U':
            color = Color.DARKRED
        elif v == 'T':
            color = Color.DARKPURPLE
        baseModels[k].color = color

def loadFiles(paths):
    kinPath = ""
    ctPath = ""
    for p in paths:
        if p.endswith(".kin"):
            kinPath = p
        elif p.endswith(".ct") or p.endswith(".ct.txt"):
            ctPath = p
        else:
            print("Failed to load " + p + "[.kin, .ct, .ct.txt] files only")
    if(kinPath != ""):
        createScene(kinPath)    
    if(ctPath != ""):
        if(hasLoadedKinFile):
            colorBases(ctPath)    
        else:
            print("Failed to load " + ctPath + " needs .kin file first")

def init():
    #Debug
    #glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    if(len(sys.argv) > 1):
        paths = sys.argv
        del paths[0]
        loadFiles(paths)
    
def update(dt):
    global animated
    mouse.update(window)
    if(mouse.leftClick):
        cam.rotateAroundPivot(mouse.dx, mouse.dy, dt)
        cam.update()
    elif(mouse.scroll != 0):
        cam.zoom(-mouse.scroll,dt)
        mouse.scroll = 0.0
        cam.update()

    if(animated):
        cam.rotateAroundPivot(0.3, 0, dt)
        cam.update()
    render.draw()
    
def resize(window, w, h):
    render.resize(w, h)

def keyboard(window, key, scancode, action, mode):
    if action == glfw.PRESS and key == glfw.KEY_ESCAPE:    
        glfw.set_window_should_close(window, glfw.TRUE)
    if action == glfw.PRESS and key == glfw.KEY_UP:    
        render.scaleModels(1.1)
    elif action == glfw.PRESS and key == glfw.KEY_DOWN:    
        render.scaleModels(0.9)

def scrollMouse(window, xoffset, yoffset):
    mouse.scroll =  yoffset

def mouseClick(window, button, action, mods):
    global animated
    if(button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS):
        if(animated):
            animated = False
        else:
            animated = True

def dropFile(window, paths):
    loadFiles(paths)

def main():
    if not glfw.init():
        raise Exception("GLFW failed to be initialized")
    global window
    window = glfw.create_window(render.width, render.height, "OpenGL Demo 2", None, None)
    if not window:
        glfw.terminate()
        raise Exception("Window failed to be created")
    glfw.set_window_pos(window, 400, 200)
    glfw.make_context_current(window)   
    glfw.set_key_callback(window, keyboard)
    glfw.set_window_size_callback(window, resize)         
    glfw.set_scroll_callback(window, scrollMouse)         
    glfw.set_drop_callback(window, dropFile)
    glfw.set_mouse_button_callback(window, mouseClick)
    init()
    render.init()
    time = glfw.get_time()
    while not glfw.window_should_close(window):
        glfw.poll_events()
        newtime = glfw.get_time()
        update(newtime - time) 
        time = newtime
        glfw.swap_buffers(window) 

if __name__ == "__main__":
    main()

