import pygame
import object
import math
import random
from physutils import PhysUtils as pu

pygame.init()

physWindow = pygame.display.set_mode((700,700))
pygame.display.set_caption(title="ActivePhys", icontitle="ActivePhys")

Clock = pygame.time.Clock()

TBox = object.Box(name="TestBox", mass=2, location=[300, 300], velocity=[2,0])
TBox2 = object.Box(name="TestBox2", mass=3, location=[500, 300], velocity=[0,2])

# TRect2 = object.Rectangle(name="TestRect", mass=2, location=[350,170], diameters=[200,50],angleFixed=45, velocity=[0,2])
TRect3 = object.Rectangle(name="Ground", mass=math.inf, location=[350,700], diameters=[1000,50],angleFixed=0, velocity=[0,0], anchored=True)

Objects = [TBox, TBox2, TRect3]

running = True

def step(steps = 1):
    for i in range(steps):
        for Object in Objects:

            Object.physStep()
        
        pu.DetectCollision(Objects)
    
def render():
    for Object in Objects:
        Object.draw(physWindow)

while running:
    physWindow.fill(color=(255,255,255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                step(5)

    step()
    render()

    pygame.display.flip()

    Clock.tick(60)