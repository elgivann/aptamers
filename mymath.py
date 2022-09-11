from math import sqrt, pi, cos, sin, floor

def sign(a):
    if(a > 0):
        return 1.0
    elif(a == 0):
        return 0.0
    else:
        return -1.0

def clamp(a, min, max):
    if(a < min):
        return min
    elif(a > max):
        return max
    return a

class Color:
    def __init__(self, r=0.0, g=0.0, b=0.0, a = 1.0):
        self.red = r
        self.green = g
        self.blue = b
        self.alpha = a
    def toArray(self):
        return [self.red, self.green, self.blue, self.alpha]

    def __str__(self):
        return "(" + str(self.red) + ", " + str(self.green) + ", " + str(self.blue) + ")";
    
Color.WHITE = Color(1.0,1.0,1.0)
Color.DARKWHITE = Color(0.7,0.7,0.7)
Color.BLACK = Color(0.0,0.0,0.0)
Color.DARKRED = Color(0.8)
Color.DARKGREEN = Color(0.0, 0.8)
Color.DARKBLUE = Color(0.0, 0.0, 0.8)
Color.DARKYELLOW = Color(0.8, 0.8)
Color.DARKPURPLE = Color(0.8, 0.0, 0.8)
Color.RED = Color(1.0,0.0,0.0)
Color.GREEN = Color(0.0,1.0,0.0)
Color.BLUE = Color(0.0,0.0,1.0)
Color.YELLOW = Color(1.0,1.0,0.0)
Color.PURPLE = Color(1.0,0.0,1.0)

class Mesh:
    def genQuad(s=1):
        vertices = [
             1.0*s,  1.0*s, 0.0*s,
             1.0*s, -1.0*s, 0.0*s, 
            -1.0*s, -1.0*s, 0.0*s, 
            -1.0*s,  1.0*s, 0.0*s, 
        ];     
        indices  = [
            0, 1, 2, 2, 3, 0
        ]
        return vertices, indices

    def genCube(s = 1):
        vertices = [
             1.0*s, 1.0*s, 1.0*s,
             1.0*s,-1.0*s, 1.0*s,
            -1.0*s,-1.0*s, 1.0*s,
            -1.0*s, 1.0*s, 1.0*s,
             1.0*s, 1.0*s,-1.0*s,
             1.0*s,-1.0*s,-1.0*s,
            -1.0*s,-1.0*s,-1.0*s,
            -1.0*s, 1.0*s,-1.0*s,
        ] 
        indices = [
            0, 1, 2, 2, 3, 0,
            4, 5, 6, 6, 7, 4, 
            4, 5, 1, 1, 0, 4,
            7, 6, 2, 2, 3, 7,
            4, 0, 3, 3, 7, 4,
            5, 1, 2, 2, 6, 5

        ]
        return vertices, indices

    #TODO change the for n-1 to n to calcurate the full raduis
    def genCylinder(n=9, r=1, h=1, cap=False):
        vertices = []
        indices = []
        s = (2 * pi) / n
        v = 2*n
        index = 0
        for i in range(n):
            x = r * cos(i * s)
            z = r * sin(i * s)
            vertices.extend([x, h, z, x, -h, z])
            indices.extend([
                index % v, (index + 1) % v, (index + 2) % v,
                (index + 1) % v, (index + 2) % v, (index + 3) % v])
            index += 2

        if(not cap):
            return vertices, indices

        vertices.extend([0, h, 0, 0, -h, 0])
        for i in range(0, v, 2):
            indices.extend([
                v, i % v, (i + 2) % v,
                v+1, (i + 1) % v, (i + 3) % v])
        return vertices, indices
    
    def genSphere(n = 16, r = 1.0):
        vertices = []
        indices = []
        stepPitch = pi / n 
        stepYaw = 2*pi / n
        pitch = -pi/2 + stepPitch
        index = 0
        south = n * (n-1) 
        north = n * (n-1) + 1 
        for i in range(1, n):
            yaw = 0
            for j in range(n):
                v = Vec3.fromEuler(pitch, yaw) * r
                vertices.extend([v.x, v.y, v.z])
                yaw += stepYaw
                
                nextIndex = (index + 1)  
                if(i == n - 1):
                    if( j != n - 1):
                        indices.extend([index, nextIndex, north])
                    else:
                        indices.extend([index, index - n + 1, north])
                    index +=1
                    continue

                upIndex = index + n
                if(j == n-1):
                    nextIndex = index - n + 1 
                nextUpIndex = nextIndex + n
                indices.extend([
                    index, nextIndex, upIndex,
                    nextIndex, nextUpIndex, upIndex, 
                ])
                index += 1
            pitch += stepPitch
        vertices.extend([0.0, -r, 0.0])
        vertices.extend([0.0, r, 0.0])
        
        for i in range(n):
            if(i != n-1):
                indices.extend([i, i+1, south])
            else:
                indices.extend([i, i - n + 1, south])
        return vertices, indices


class Vec3:
    def __init__(self, x=0.0, y=0.0 , z=0.0):
        self.x = x
        self.y = y
        self.z = z   

    
    def __add__(self, o): 
        return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)
    
    
    def __sub__(self, o): 
        return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, s):
        return Vec3(self.x * s, self.y * s, self.z * s) 
    
    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def __iadd__(self,o):
        self.x += o.x
        self.y += o.y
        self.z += o.z
        return self

    def __isub__(self,o):
        self.x -= o.x
        self.y -= o.y
        self.z -= o.z
        return self

    def __imul__(self,s):
        self.x *= s
        self.y *= s
        self.z *= s
        return self
    
    def length(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def lengthSqrt(self):
        return self.x * self.x + self.y * self.y + self.z * self.z 
    
    def toNormal(self):
        m = sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        if(m != 0):
            self.x /= m
            self.y /= m
            self.z /= m
        return self
 
    def normalize(v):
        m = sqrt(v.x * v.x + v.y * v.y + v.z * v.z)
        if(m != 0):
            return Vec3(v.x / m, v.y / m, v.z / m)
        return Vec3(0.0,0.0,0.0)

    def fromEuler(pitch = 0, yaw = 0):
        return Vec3(
            cos(yaw)*cos(pitch),
            sin(pitch),
            sin(yaw)*cos(pitch)
        )   
 
    def lookAt(self, o):
        x = o.x - self.x
        y = o.y - self.y
        z = o.z - self.z
        m = sqrt(x * x + y * y + z * z)
        if(m != 0):
            return Vec3(x/m,y/m,z/m)
        return Vec3(0.0,0.0,0.0)
    

    def dot(self, o):
        return self.x * o.x + self.y * o.y + self.z * o.z
    
    def cross(self, o):
        return Vec3(
            self.y * o.z - self.z * o.y, 
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x
        )
    
    def toArray(self):
        return [self.x, self.y, self.z]

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"
    

