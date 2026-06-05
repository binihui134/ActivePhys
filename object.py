import pygame
import math
from physutils import PhysUtils
pygame.init()

#object<Object> arguments:
#name: REQUIRED
#mass: REQUIRED (>0)
#location: REQUIRED [x,y]


class Box:
    def __init__(self, name : str = "Box", 
                 mass: int = 10, 
                 location: list[int] = None, 
                 velocity: list[int] = None, 
                 diameter: int = 120, 
                 angleFixed: int = 0,
                 anchored: bool = False):

        if location is None:
            location = [0, 0]

        if velocity is None:
            velocity = [2, 0]

        self.name = name

        self.type = "Box"

        self.mass = mass
        self.diameter = diameter
        self.radius = self.diameter / 2
        
        self.radii = [self.radius, self.radius]
        self.localVertices = [
            (self.radius, self.radius),
            (self.radius, -self.radius),
            (-self.radius, -self.radius),
            (-self.radius, self.radius),
        ]

        self.location = location
        self.velocity = velocity

        self.x = self.location[0]
        self.y = self.location[1]

        self.vx = self.velocity[0]
        self.vy = self.velocity[1]

        # keep angle ONLY as derived value (no physics role)
        self.angleMotion = math.atan2(self.vy, self.vx)

        self.angleFixed = angleFixed
        self.anchored = anchored
        self.worldVertices = []
        self.outlineWidth = 5

    def refreshPolygon(self):
        self.worldVertices = PhysUtils.getWorldPolygonVertices(self)
        
    def draw(self, surface):
        self.refreshPolygon()
        CornerPoints = PhysUtils.GetCornerPoints(self, surface)
        
        PhysUtils.showHitbox(self, surface)
        PhysUtils.showAngles(self, surface)
        lineList = []
        if len(self.worldVertices) >= 2:
            lineList = pygame.draw.polygon(surface, (0,0,0), self.worldVertices, width=self.outlineWidth)
        
        pygame.draw.circle(surface, (0,0,255), (self.location[0], self.location[1]), 5, width=0)

        return {"lineList": lineList, "cornerPoints":CornerPoints}
    
    def physStep(self):
        if self.anchored:
            return
        self.location = [self.location[0] + self.velocity[0], self.location[1] + self.velocity[1]]
        self.x = self.location[0]
        self.y = self.location[1]
        self.refreshPolygon()
        
class Rectangle:
    def __init__(self, 
                 name : str = "Rectangle",
                 mass: int=10, 
                 location: list[int] = None,
                 velocity: list[int] = None,
                 diameters: list[int] = None,
                 angleFixed: int = 0,
                 anchored = False):

        if location:
            self.location = location
        else:
            self.location = [0,0]
        
        if velocity:
            self.velocity = velocity
        else:
            self.velocity = [2,0]
            
        self.type = "Rectangle"
        
        self.anchored = anchored
        self.mass = mass
        self.diameters = diameters
        self.radii = [diameters[0]/2, diameters[1]/2]
        self.localVertices = [
            (self.radii[0], self.radii[1]),
            (self.radii[0], -self.radii[1]),
            (-self.radii[0], -self.radii[1]),
            (-self.radii[0], self.radii[1]),
        ]
        
        #alias
        self.x = self.location[0]
        self.y = self.location[1]
        
        self.vx = self.velocity[0]
        self.vy = self.velocity[1]

        self.angleMotion = math.atan2(self.vy, self.vx)
        
        self.angleFixed = angleFixed
        self.worldVertices = []
        self.outlineWidth = 5

    def refreshPolygon(self):
        self.worldVertices = PhysUtils.getWorldPolygonVertices(self)
        
    def draw(self, surface):
        self.refreshPolygon()
        CornerPoints = PhysUtils.GetCornerPoints(self, surface)
        
        # PhysUtils.showHitbox(self, surface)
        PhysUtils.showAngles(self, surface)
        lineList = []
        if len(self.worldVertices) >= 2:
            lineList = pygame.draw.polygon(surface, (0,0,0), self.worldVertices, width=self.outlineWidth)
        
        pygame.draw.circle(surface, (0,0,255), (self.location[0], self.location[1]), 5, width=0)

        return {"lineList": lineList, "cornerPoints":CornerPoints}
            
    def physStep(self):
        if not self.anchored:
            self.location = [self.location[0] + self.velocity[0], self.location[1] + self.velocity[1]]
            self.x = self.location[0]
            self.y = self.location[1]
            self.refreshPolygon()
        else:
            return
 
class Circle:
    def __init__(self, name : str = "Circle", 
                 mass: int = 10, 
                 location: list[int] = None, 
                 velocity: list[int] = None, 
                 diameter: int = 120, 
                 segments: int = 24,
                 anchored: bool = False):

        if location is None:
            location = [0, 0]

        if velocity is None:
            velocity = [2, 0]

        self.name = name

        self.type = "Circle"

        self.mass = mass
        self.diameter = diameter
        self.radius = self.diameter / 2
        self.radii = [self.radius, self.radius]
        self.segments = segments
        self.localVertices = PhysUtils.generateCirclePolygon((0, 0), self.radius, self.segments)

        self.location = location
        self.velocity = velocity

        self.x = self.location[0]
        self.y = self.location[1]

        self.vx = self.velocity[0]
        self.vy = self.velocity[1]

        # keep angle ONLY as derived value (no physics role)
        self.angleMotion = math.atan2(self.vy, self.vx)
        self.angleFixed = 0

        self.anchored = anchored
        self.worldVertices = []
        self.outlineWidth = 5

    def refreshPolygon(self):
        self.worldVertices = PhysUtils.getWorldPolygonVertices(self)
        
    def draw(self, surface):
        self.refreshPolygon()
        PhysUtils.showHitbox(self, surface)
        PhysUtils.showAngles(self, surface)

        circle = pygame.draw.polygon(
            surface,
            (0, 0, 0),
            self.worldVertices,
            width=self.outlineWidth
        )

        pygame.draw.circle(
            surface,
            (0, 0, 255),
            (self.location[0], self.location[1]),
            5,
            width=0
        )

        return {"circle": circle}
    
    def physStep(self):
        if self.anchored:
            return
        self.location = [self.location[0] + self.velocity[0], self.location[1] + self.velocity[1]]
        self.x = self.location[0]
        self.y = self.location[1]
        self.refreshPolygon()

class Hexagon(Circle):
    def __init__(self,
                 name: str = "Hexagon",
                 mass: int = 10,
                 location: list[int] = None,
                 velocity: list[int] = None,
                 diameter: int = 120,
                 anchored: bool = False):
        super().__init__(
            name=name,
            mass=mass,
            location=location,
            velocity=velocity,
            diameter=diameter,
            segments=6,
            anchored=anchored
        )
        self.type = "Hexagon"
        self.angleFixed = 0
        self.outlineWidth = 5
        self.localVertices = PhysUtils.generateCirclePolygon((0, 0), self.radius, 6)
