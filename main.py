import pygame
import object
import math
import random
from physutils import PhysUtils as pu

pygame.init()

physWindow = pygame.display.set_mode((700,700))
pygame.display.set_caption(title="ActivePhys", icontitle="ActivePhys")

Clock = pygame.time.Clock()
WORLD_BOUND_THICKNESS = 50

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
TRect1.is_world_bound = True
TRect3.is_world_bound = True

TCirc1 = object.Circle(name="Ball1", mass=5, location=[500, 150], velocity=[-2, 0], diameter=50)
THex1 = object.Hexagon(name="Hex1", mass=8, location=[550, 320], velocity=[-1, 1], diameter=70)

Objects = [
    TBox1,
    TBox2,
    TBox3,
    TCirc1,
    THex1,
    TRect3,
    TRect1
]
TRect2 = object.Rectangle(name="TestRect", mass=2, location=[350,170], diameters=[200,50],angleFixed=45, velocity=[0,2])

WorldBounds = pu.CreateWorldBounds(physWindow, Objects, thickness=WORLD_BOUND_THICKNESS)
spawnPanel = pu.CreateSpawnPanel(
    world_window=physWindow,
    world_objects=Objects,
    world_thickness=WORLD_BOUND_THICKNESS
)

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
        elif spawnPanel.handle_event(event, Objects):
            continue
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                step(5)

    spawnPanel.update(Objects)
    step()
    render()
    spawnPanel.draw_preview(physWindow, pygame.mouse.get_pos())
    spawnPanel.draw(physWindow)

    pygame.display.flip()

    Clock.tick(60)
