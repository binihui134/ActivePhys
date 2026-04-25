from __future__ import annotations
from typing import TYPE_CHECKING
import math
import pygame
import gamecuts


if TYPE_CHECKING:
    from object import *

font = pygame.font.SysFont("Arial", 15)

cos = math.cos
rad = math.radians
rt = math.sqrt
sin = math.sin

def nTu(t):
    return (-t[0], -t[1])

class PhysUtils:
 
    # HELPER
     
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
    
    def objectOfTypeRadius(Object: Box | Rectangle):
        if Object.type == "Box":
            return Object.radius, Object.radius
        else:
            return Object.radii[0], Object.radii[1]
    
     
    def OffAdd(origin, offset):
        
        return (origin[0]+offset[0], origin[1]+offset[1])
    
    def cAdd(c1, c2):
        return (c1[0]+c2[0], c1[1]+c2[1])
    def cSub(c1, c2):
        
        return (c1[0]-c2[0], c1[1]-c2[1])
    def cMul(c1, c2):

        if type(c2) == int:
            c2 = (c2,c2)
        elif type(c2) == float:
            c2 = (c2,c2)
        return (c1[0]*c2[0], c1[1]*c2[1])
    def cDiv(c1, c2):

        
        return (c1[0]/c2[0], c1[1]/c2[1])
    
    def dot(c1, c2):
        return c1[0]*c2[0]+c1[1]*c2[1]
    
    #Get Corner Points
    
    def GetCornerPointsBox(object : Box, surface=None):
        radius = object.radius
        radAngular = object.angleFixed* math.pi/180

        fX, fY = (math.cos(radAngular), math.sin(radAngular))
        sX, SY = (-math.sin(radAngular), math.cos(radAngular))

        objCoords = object.location

        originFwdPoint = (radius * fX, radius * fY)
        originRightPoint = (radius * sX, radius * SY)

        CFl = PhysUtils.OffAdd(PhysUtils.OffAdd(objCoords, originFwdPoint), originRightPoint) #0 0 
        CFr = PhysUtils.OffAdd(PhysUtils.OffAdd(objCoords, originFwdPoint), nTu(originRightPoint)) #0 1
        CBr = PhysUtils.OffAdd(PhysUtils.OffAdd(objCoords, nTu(originFwdPoint)), originRightPoint) #1 0
        CBl = PhysUtils.OffAdd(PhysUtils.OffAdd(objCoords, nTu(originFwdPoint)), nTu(originRightPoint)) # 1 1

        # surface argument is missing if uncomment add into GetCornerPoints        
        
        if surface:
            gamecuts.displayText(surface, font, "CFr", color=(255,0,0),x=CFr[0], y=CFr[1])
            gamecuts.displayText(surface, font, "CFl", color=(255,0,0),x=CFl[0], y=CFl[1])
            gamecuts.displayText(surface, font, "CBl", color=(255,0,0),x=CBl[0], y=CBl[1])
            gamecuts.displayText(surface, font, "CBr", color=(255,0,0),x=CBr[0], y=CBr[1])     
            
        return {
            "CFl":CFl,
            "CFr":CFr,
            "CBl":CBl,
            "CBr":CBr   
        }
    
    def GetCornerPointsRect(object : Rectangle, surface=None):
        xRadi = object.radii[0]
        yRadi = object.radii[1]
        
        rad = math.radians(object.angleFixed)
        
        fX, fY = (cos(rad), sin(rad))
        sX, sY = (-sin(rad), cos(rad))
        
        origin = object.location
         
        originFwdPoint = (fX * xRadi, fY * xRadi)
        originRightPoint = (sX * yRadi, sY *  yRadi)
        
        CFl = PhysUtils.OffAdd(PhysUtils.OffAdd(origin, originFwdPoint), originRightPoint) #0 0 
        CFr = PhysUtils.OffAdd(PhysUtils.OffAdd(origin, originFwdPoint), nTu(originRightPoint)) #0 1
        CBr = PhysUtils.OffAdd(PhysUtils.OffAdd(origin, nTu(originFwdPoint)), originRightPoint) #1 0
        CBl = PhysUtils.OffAdd(PhysUtils.OffAdd(origin, nTu(originFwdPoint)), nTu(originRightPoint)) # 1 1
        
        return {
            "CFl":CFl,
            "CFr":CFr,
            "CBl":CBl,
            "CBr":CBr   
        }       
         
    def GetCornerPoints(object, surface=None):
        if object.type == "Box":
            return PhysUtils.GetCornerPointsBox(object, surface)
        elif object.type == "Rectangle":
            return PhysUtils.GetCornerPointsRect(object, surface)          
    #Debug
    
    def enableDebug(Object, Surface, ShowDegrees):
       pass 
    
     
    def showAngles(Object, Surface, deg=True):
        
        x = Object.location[0] + math.cos(Object.angleMotion) * 75
        y = Object.location[1] + -math.sin(Object.angleMotion) * 75 
         
        pygame.draw.line(Surface, (0,0,255), (Object.location[0], Object.location[1]), (x,y), 3)
        if deg:
            gamecuts.displayText(Surface, font, str(math.degrees(Object.angleMotion))+"°", color=(0,0,0), x=Object.location[0], y=Object.location[1])     
        else:
            gamecuts.displayText(Surface, font, str(Object.angleMotion)+"rad", color=(0,0,0), x=Object.location[0], y=Object.location[1])     
        
        x2 = Object.location[0] +math.cos(math.radians(Object.angleFixed)) * 75
        y2 = Object.location[1] + -math.sin(math.radians(Object.angleFixed)) * 75 
        pygame.draw.line(Surface, (255,0,0), (Object.location[0], Object.location[1]), (x2,y2), 3)
        gamecuts.displayText(Surface, font, str(Object.angleFixed)+"°", color=(255,0,0), x=Object.location[0], y=Object.location[1]-15)    
             
    def showHitbox(Object, surface):
        #assuming Box item
        oX = Object.location[0]
        oY = Object.location[1]
        
        oRBoundaries = PhysUtils.GetHitboxBoundaries(Object)
        pygame.draw.line(surface=surface, color=(0,0,255), start_pos=(oX,oY), end_pos=(oRBoundaries["Left"], oY))
        pygame.draw.line(surface=surface, color=(0,0,255), start_pos=(oX,oY), end_pos=(oRBoundaries["Right"], oY))
        pygame.draw.line(surface=surface, color=(0,0,255), start_pos=(oX,oY), end_pos=(oX, oRBoundaries["Top"]))
        pygame.draw.line(surface=surface, color=(0,0,255), start_pos=(oX,oY), end_pos=(oX, oRBoundaries["Bottom"]))
        

                
                 

    # COLLISION
    
    
    
    
    #Detects object collision
    def DetectCollision(Objects: list[Box | Rectangle]):
        return PhysUtils.DetectCollisionSAT()
    

    def DetectCollisionSAT(Objects : list[Box | Rectangle]):
        for i in range(len(Objects)):
            for j in range(i+1, len(Objects)):
                o1 = Objects[i]
                o2 = Objects[j]
                
                if o1 == o2:
                    continue        
                                
                #PhysUtils.dot(c, axis)
                                
                o1Right = (cos(o1.angleFixed), sin(o1.angleFixed))
                o1Up = (-sin(o1.angleFixed), cos(o1.angleFixed))                
                
                o2Right = (cos(o2.angleFixed), sin(o2.angleFixed))
                o2Up = (-sin(o2.angleFixed), cos(o2.angleFixed))

                collisionAxes = [o1Right, o1Up, o2Right, o2Up]
                
                collision = True
                
                smallestAxis = None
                smallestOverlap = math.inf
                                 
                for axis in collisionAxes:
                    o1C = PhysUtils.dot(o1.location, axis)
                    o2C = PhysUtils.dot(o2.location, axis)
                    
                    o1hw, o1hy = PhysUtils.objectOfTypeRadius(o1)
                    o2hw, o2hy = PhysUtils.objectOfTypeRadius(o2)
                    
                    o1Radi = abs(PhysUtils.dot(o1Right, axis)) * o1hw + abs(PhysUtils.dot(o1Up,axis)) * o1hy
                    
                    o2Radi = abs(PhysUtils.dot(o2Right, axis)) * o2hw + abs(PhysUtils.dot(o2Up,axis)) * o2hy
                    
                    o1min, o1max = o1C-o1Radi, o1C+o1Radi
                    o2min, o2max = o2C-o2Radi, o2C+o2Radi

                    overlap = min(o1max, o2max) - max(o1min, o2min)
                                        
                    if o1max < o2min or o2max < o1min:
                        
                        collision = False
                        break
                    else:
                        if overlap < smallestOverlap:
                            smallestOverlap = overlap
                            smallestAxis = axis                            
                        
                
                if not collision:
                    continue
                
                
                dirVec = PhysUtils.cSub(o2.location, o1.location)

                if PhysUtils.dot(dirVec, smallestAxis) < 0:
                    smallestAxis = PhysUtils.cMul(smallestAxis, (-1,-1))
                
                MinimumTranslationVector = PhysUtils.cMul(smallestAxis, smallestOverlap)
                 
                halfMTV = PhysUtils.cDiv(MinimumTranslationVector, (2,2))       
                        
                o1.location = PhysUtils.cSub(o1.location, halfMTV)
                o2.location = PhysUtils.cAdd(o2.location, halfMTV)
                
                RelativeVelocity = PhysUtils.cSub(o2.velocity, o1.velocity)
                
                collisionNormal = smallestAxis
                
                velocityNormal = PhysUtils.dot(RelativeVelocity, collisionNormal)
                
                if velocityNormal > 0:
                    continue
                
                m1 = o1.mass
                m2 = o2.mass
                
                e = 1
                j = -(1 + e) * velocityNormal
                j /= (1/m1 + 1/m2)
                
                
                impulse = PhysUtils.cMul(collisionNormal, j)

                o1.velocity = PhysUtils.cSub(o1.velocity, PhysUtils.cDiv(impulse, (m1, m1)))
                o2.velocity = PhysUtils.cAdd(o2.velocity, PhysUtils.cDiv(impulse, (m2, m2)))
                
        return Objects       



    #Use AABB Collision                                       
    def DetectCollisionAABB(Objects : list[Box | Rectangle]):
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
                    C1B["Bottom"] < C2B["Top"]):
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
                    CollideInstance1.location[0] += CollideInstance1.mass/totalMass * overlapX
                    CollideInstance2.location[0] -= CollideInstance2.mass/totalMass * overlapX
                
                    vPrime1 = ((CollideInstance1.velocity[0] * (m1-m2)) + 2 * m2 * CollideInstance2.velocity[0])/(m1+m2)
                    vPrime2 = ((CollideInstance2.velocity[0] * (m2-m1)) + 2 * m2 * CollideInstance1.velocity[0])/(m1+m2)
                    
                    CollideInstance1.velocity[0] = vPrime1
                    CollideInstance2.velocity[0] = vPrime2            
        return Objects

    #Extra/Past Versions
    
    def collisionResolutionImpulse(o1, o2):
        v1x = o1.speed * sin(o1.angleMotion)
        v1y = o1.speed * cos(o1.angleMotion)
                
        v2x = o2.speed * sin(o2.angleMotion)
        v2y = o2.speed * cos(o2.angleMotion)
                
        n = PhysUtils.cSub((o1.location[0], o1.location[1]), (o2.location[0], o2.location[1]))
                
        nl = math.sqrt(n[0]**2 + n[1]**2)
                
        if nl == 0:
            n = (1,0)
        else:
            n = (n[0]/nl, n[1]/nl)
                    
        v1n = v1x * n[0] + v1y * n[1]
        v2n = v2x * n[0] + v2y * n[1]
                    
        m1 = o1.mass
        m2 = o2.mass    
    
        v1n_new = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
        v2n_new = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)   
                
        dv1n = v1n_new - v1n
        dv2n = v2n_new - v2n    
                
        v1x += dv1n * n[0]
        v1y += dv1n * n[1]

        v2x += dv2n * n[0]
        v2y += dv2n * n[1]
                
                
        o1.speed = math.sqrt(v1x*v1x + v1y*v1y)
        o1.angleMotion = math.atan2(v1y, v1x)

        o2.speed = math.sqrt(v2x*v2x + v2y*v2y)
        o2.angleMotion = math.atan2(v2y, v2x)                