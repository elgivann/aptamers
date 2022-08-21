from math import sin, cos, pi 
from mymath import Vec3, clamp
from pyrr import matrix44, Vector3 
 
class Camera:
    rotSpeed = 1
    zoomSpeed = 1
    worldUp = Vec3(0.0,1.0,0.0)
    minDistance = 1

    def __init__(self, pivot=Vec3(), distance=1, pitch=0, yaw=0):
        self.pivot = pivot
        self.distance = distance
        self.pitch = pitch
        self.yaw = yaw
        self.update()

    def zoom(self, d, dt):
        self.distance += d * self.zoomSpeed * dt
        if(self.distance < self.minDistance):
            self.distance = self.minDistance
                   
    def rotateAroundPivot(self, dx, dy, dt):
        self.yaw += dx * self.rotSpeed * dt 
        self.pitch += dy * self.rotSpeed * dt
        
    def update(self):
        self.pitch = clamp(self.pitch, -pi/2, pi/2)
        self.yaw %= 2*pi
        d = Vec3.fromEuler(self.pitch, self.yaw)
        self.pos = self.pivot + d * self.distance 
        self.front = -d  
        self.right = self.worldUp.cross(self.front).toNormal()
        self.up = self.front.cross(self.right)
        self.view = matrix44.create_look_at(
            Vector3(self.pos.toArray()), 
            Vector3((self.pos + self.front).toArray()), 
            Vector3(self.up.toArray())
        )
