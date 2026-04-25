from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from object import *

def DetectCollisionAABB(Objects : list[Box]):
    for i in range(len(Objects)):
        for j in range(i+1,len(Objects)):
                                
            o1 = Objects[i]
            o2 = Objects[j]
                
            if o1 == o2:
                continue
                
            o1Left = o1.location[0]-o1.radius
            o1Right = o1.location[0]+o1.radius
            o1Top = o1.location[1]-o1.radius
            o1Bottom = o1.location[1]+o1.radius
            
            o2Left = o2.location[0]-o2.radius
            o2Right = o2.location[0]+o2.radius
            o2Top = o2.location[1]-o2.radius
            o2Bottom = o2.location[1]+o2.radius
            
            if (o1Left > o2Right or o1Right < o2Left or o1Top > o2Bottom or o1Bottom < o2Top):
                continue

            overlapX = min(o1Right, o2Right) - max(o1Left, o2Left)
            overlapY = min(o1Bottom, o2Bottom) - max(o1Top, o2Top)
                            
                            
            m1 = o1.mass
            m2 = o2.mass
            totalMass = o1.mass + o2.mass
            
            if overlapX > overlapY:
                o1.location[1] += o1.mass/totalMass * overlapY
                o2.location[1] -= o2.mass/totalMass * overlapY
                # o1.velocity[1],o2.velocity[1] = o2.velocity[1], o1.velocity[1]
            
                vPrime1 = ((o1.velocity[1] * (m1-m2)) + 2 * m2 * o2.velocity[1])/(m1+m2)
                vPrime2 = ((o2.velocity[1] * (m2-m1)) + 2 * m2 * o1.velocity[1])/(m1+m2)
                
                o1.velocity[1] = vPrime1
                o2.velocity[1] = vPrime2
            else:
                o1.location[0] += o1.mass/totalMass * overlapX
                o2.location[0] -= o2.mass/totalMass * overlapX
                # o1.velocity[0], o2.velocity[0] = o2.velocity[0], o1.velocity[0]
                
            
                vPrime1 = ((o1.velocity[0] * (m1-m2)) + 2 * m2 * o2.velocity[0])/(m1+m2)
                vPrime2 = ((o2.velocity[0] * (m2-m1)) + 2 * m2 * o1.velocity[0])/(m1+m2)
                
                o1.velocity[0] = vPrime1
                o2.velocity[0] = vPrime2    
                
            # o1.angleMotion += 180
            # o2.angleMotion += 180
                
            
    return Objects

def GetHitboxBoundaries(Object : Box | Rectangle):
    if Object.type == "Box":
        hw,hy = Object.radius, Object.radius
    else:
        hw,hy = Object.radii[0], Object.radii[1]
        
    x = Object.location[0]
    y = Object.location[1]
    
    return {
        "Left":  x-hw,
        "Right": x+hw,
        "Top":   y-hy,
        "Bottom":y+hy
    }

def DetectCollision(Objects : list[Box | Rectangle]):
    for i in range(len(Objects)):
        for j in range(i + 1, len(Objects)):
            
            CollideInstance1 = Objects[i]
            CollideInstance2 = Objects[j]
            
            if CollideInstance1 == CollideInstance2:
                continue
            
            C1B = PhysUtils.GetHitboxBoundaries(CollideInstance1)
            C2B = PhysUtils.GetHitboxBoundaries(CollideInstance2)
                       
            if (C1B["Left"] > C2B["Right"] or 
                C1B["Right"] < C2B["Left"] or 
                C1B["Top"] > C2B["Bottom"] or 
                C1B["Bottom"] < C1B["Top"]):
                continue
            
            overlapX = min(C1B["Right"], C2B["Right"]) - max(C1B["Left"], C2B["Left"])
            overlapY = min(C1B["Bottom"], C2B["Bottom"]) - max(C1B["Top"], C2B["Top"])
            
            m1 = CollideInstance1.mass
            m2 = CollideInstance2.mass
            
            totalMass = m1+m2
            
            if overlapX > overlapY:
                CollideInstance1.location[1] += CollideInstance1.mass/totalMass * overlapY
                CollideInstance2.location[1] -= CollideInstance2.mass/totalMass * overlapY
            
                vPrime1 = ((CollideInstance1.velocity[1] * (m1-m2)) + 2 * m2 * CollideInstance2.velocity[1])/(m1+m2)
                vPrime2 = ((CollideInstance2.velocity[1] * (m2-m1)) + 2 * m2 * CollideInstance1.velocity[1])/(m1+m2)
                
                CollideInstance1.velocity[1] = vPrime1
                CollideInstance2.velocity[1] = vPrime2
            else:
                CollideInstance1.location[0] += CollideInstance1.mass/totalMass * overlapY
                CollideInstance2.location[0] -= CollideInstance2.mass/totalMass * overlapY
            
                vPrime1 = ((CollideInstance1.velocity[0] * (m1-m2)) + 2 * m2 * CollideInstance2.velocity[0])/(m1+m2)
                vPrime2 = ((CollideInstance2.velocity[0] * (m2-m1)) + 2 * m2 * CollideInstance1.velocity[0])/(m1+m2)
                
                CollideInstance1.velocity[0] = vPrime1
                CollideInstance2.velocity[0] = vPrime2            
    return Objects
            