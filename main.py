import pygame
import object
import math
import random
from physutils import PhysUtils as pu

pygame.init()

physWindow = pygame.display.set_mode((700,700))
pygame.display.set_caption(title="ActivePhys", icontitle="ActivePhys")

Clock = pygame.time.Clock()

TBox1 = object.Box(
    name="HeavyBox",
    mass=100,
    location=[150, 150],
    velocity=[3, 0]
)

TBox2 = object.Box(
    name="MediumBox",
    mass=10,
    location=[350, 250],
    velocity=[0, 2]
)

TBox3 = object.Box(
    name="LightBox",
    mass=1,
    location=[250, 450],
    velocity=[1, 0]
)
TRect1 = object.Rectangle(name="Ground", mass=math.inf, location=[0,700], diameters=[1000,50],angleFixed=0, velocity=[0,0], anchored=True)
TRect3 = object.Rectangle(name="Ground", mass=math.inf, location=[350,700], diameters=[1000,50],angleFixed=0, velocity=[0,0], anchored=True)

TCirc1 = object.Circle(name="Ball1", mass=5, location=[500, 150], velocity=[-2, 0], diameter=50)

Objects = [
    TBox1,
    TBox2,
    TBox3,
    TCirc1,
    TRect3,
    TRect1
]
TRect2 = object.Rectangle(name="TestRect", mass=2, location=[350,170], diameters=[200,50],angleFixed=45, velocity=[0,2])

pu.CreateWorldBounds(physWindow, Objects, thickness=50)

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