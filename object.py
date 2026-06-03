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
        
    def draw(self, surface):

        CornerPoints = PhysUtils.GetCornerPoints(self, surface)
        
        PhysUtils.showHitbox(self, surface)
        PhysUtils.showAngles(self, surface)
    
        line1 = pygame.draw.line(surface, color=(0,0,0), start_pos=(CornerPoints["CFl"]), end_pos=(CornerPoints["CBr"]), width=5)
        line2 = pygame.draw.line(surface, color=(0,0,0), start_pos=(CornerPoints["CFr"]), end_pos=(CornerPoints["CFl"]), width=5)
        line3 = pygame.draw.line(surface, color=(0,0,0), start_pos=(CornerPoints["CBr"]), end_pos=(CornerPoints["CBl"]), width=5)
        line4 = pygame.draw.line(surface, color=(0,0,0), start_pos=(CornerPoints["CBl"]), end_pos=(CornerPoints["CFr"]), width=5)

        lineList = [line1, line2, line3, line4]
        
        pygame.draw.circle(surface, (0,0,255), (self.location[0], self.location[1]), 5, width=0)

        return {"lineList": lineList, "cornerPoints":CornerPoints}
    
    def physStep(self):
        if self.anchored:
            return
        self.location = [self.location[0] + self.velocity[0], self.location[1] + self.velocity[1]]
        self.x = self.location[0]
        self.y = self.location[1]
        
class Rectangle:
    def __init__(self, 
                 name : str = "Rectangle",
                 mass: int=10, 
                 location: list[int] = None,
                 velocity: list[int] = None,
                 diameters: list[int] = None,
                 angleFixed = int,
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
        
        #alias
        self.x = location[0]
        self.y = location[1]
        
        self.vx = velocity[0]
        self.vy = velocity[1]

        self.angleMotion = math.atan2(self.vy, self.vx)
        
        self.angleFixed = angleFixed
        
    def draw(self, surface):
        
        
        CornerPoints = PhysUtils.GetCornerPoints(self, surface)
        
        # PhysUtils.showHitbox(self, surface)
        PhysUtils.showAngles(self, surface)
    
        line1 = pygame.draw.line(surface, color=(0,0,0), start_pos=(CornerPoints["CFl"]), end_pos=(CornerPoints["CBr"]), width=5)
        line2 = pygame.draw.line(surface, color=(0,0,0), start_pos=(CornerPoints["CFr"]), end_pos=(CornerPoints["CFl"]), width=5)
        line3 = pygame.draw.line(surface, color=(0,0,0), start_pos=(CornerPoints["CBr"]), end_pos=(CornerPoints["CBl"]), width=5)
        line4 = pygame.draw.line(surface, color=(0,0,0), start_pos=(CornerPoints["CBl"]), end_pos=(CornerPoints["CFr"]), width=5)

        lineList = [line1, line2, line3, line4]
        
        pygame.draw.circle(surface, (0,0,255), (self.location[0], self.location[1]), 5, width=0)

        return {"lineList": lineList, "cornerPoints":CornerPoints}
            
    def physStep(self):
        if not self.anchored:
            self.location = [self.location[0] + self.velocity[0], self.location[1] + self.velocity[1]]
            self.x = self.location[0]
            self.y = self.location[1]
        else:
            return