from __future__ import annotations
import math
import pygame
import gamecuts
import object

font = pygame.font.SysFont("Arial", 15)

cos = math.cos
rad = math.radians
rt = math.sqrt
sin = math.sin

def nTu(t):
    return (-t[0], -t[1])


class SpawnPanel:
    def __init__(
        self,
        toggle_key=pygame.K_TAB,
        position=(16, 16),
        width=260,
        spawn_size=100,
        world_window=None,
        world_objects=None,
        world_thickness=50,
    ):
        self.toggle_key = toggle_key
        self.position = position
        self.width = width
        self.spawn_size = spawn_size
        self.visible = False
        self.selected_shape = "Box"
        self.font = pygame.font.SysFont("Arial", 16)
        self.small_font = pygame.font.SysFont("Arial", 13)
        self.button_font = pygame.font.SysFont("Arial", 12)

        self.mass = 10
        self.anchored = False
        self.delete_mode = False
        self.direction_mode = False
        self.angle_fixed = 0
        self.velocity_speed = 2
        self.velocity_angle = 0
        self.circle_segments = 24
        self.outline_width = 5
        self.min_size = 20
        self.max_size = 240
        self.min_mass = 1
        self.max_mass = 200
        self.min_speed = 0
        self.max_speed = 12
        self.min_segments = 6
        self.max_segments = 48
        self.button_gap = 6
        self.button_height = 24
        self.button_width = 72
        self.button_repeat_delay_ms = 1000
        self.button_repeat_interval_ms = 75
        self._active_button_action = None
        self._active_button_started_at = 0
        self._active_button_next_repeat_at = 0
        self._active_button_rect = None
        self.world_window = world_window
        self.world_objects = world_objects
        self.world_thickness = world_thickness

        self.shape_keys = {
            pygame.K_1: "Box",
            pygame.K_2: "Rectangle",
            pygame.K_3: "Circle",
            pygame.K_4: "Hexagon",
        }

    def _build_velocity(self):
        vx = math.cos(math.radians(self.velocity_angle)) * self.velocity_speed
        vy = -math.sin(math.radians(self.velocity_angle)) * self.velocity_speed
        return [vx, vy]

    def _shape_size_values(self):
        if self.selected_shape == "Rectangle":
            return [int(self.spawn_size * 1.5), int(self.spawn_size * 0.75)]
        return self.spawn_size

    def _clamp(self, value, minimum, maximum):
        return max(minimum, min(maximum, value))

    def _cycle_shape(self, step):
        shapes = ["Box", "Rectangle", "Circle", "Hexagon"]
        index = shapes.index(self.selected_shape)
        self.selected_shape = shapes[(index + step) % len(shapes)]

    def _adjust_size(self, delta):
        self.spawn_size = self._clamp(self.spawn_size + delta, self.min_size, self.max_size)

    def _adjust_mass(self, delta):
        self.mass = self._clamp(self.mass + delta, self.min_mass, self.max_mass)

    def _adjust_speed(self, delta):
        self.velocity_speed = self._clamp(self.velocity_speed + delta, self.min_speed, self.max_speed)

    def _adjust_angle(self, delta):
        if self.direction_mode:
            self.velocity_angle = (self.velocity_angle + delta) % 360
        else:
            self.angle_fixed = (self.angle_fixed + delta) % 360

    def _adjust_segments(self, delta):
        self.circle_segments = self._clamp(self.circle_segments + delta, self.min_segments, self.max_segments)
        if self.circle_segments % 2 == 1:
            self.circle_segments += 1

    def _button(self, panel, x, y, w, h, label, active=False):
        rect = pygame.Rect(x, y, w, h)
        fill = (52, 62, 84) if active else (34, 38, 48)
        border = (120, 220, 255) if active else (95, 100, 118)
        pygame.draw.rect(panel, fill, rect, border_radius=6)
        pygame.draw.rect(panel, border, rect, width=1, border_radius=6)
        text = self.button_font.render(label, True, (245, 245, 245))
        panel.blit(text, text.get_rect(center=rect.center))
        return rect

    def _shape_button_label(self, name):
        return {
            "Box": "Box",
            "Rectangle": "Rect",
            "Circle": "Circle",
            "Hexagon": "Hex",
        }[name]

    def _spawn_box(self, location):
        return object.Box(
            name="SpawnBox",
            mass=self.mass,
            location=list(location),
            velocity=self._build_velocity(),
            diameter=self.spawn_size,
            angleFixed=self.angle_fixed,
            anchored=self.anchored
        )

    def _spawn_rectangle(self, location):
        return object.Rectangle(
            name="SpawnRectangle",
            mass=self.mass,
            location=list(location),
            velocity=self._build_velocity(),
            diameters=self._shape_size_values(),
            angleFixed=self.angle_fixed,
            anchored=self.anchored
        )

    def _spawn_circle(self, location):
        return object.Circle(
            name="SpawnCircle",
            mass=self.mass,
            location=list(location),
            velocity=self._build_velocity(),
            diameter=self.spawn_size,
            segments=self.circle_segments,
            anchored=self.anchored
        )

    def _spawn_hexagon(self, location):
        return object.Hexagon(
            name="SpawnHexagon",
            mass=self.mass,
            location=list(location),
            velocity=self._build_velocity(),
            diameter=self.spawn_size,
            anchored=self.anchored
        )

    def _is_world_bound(self, candidate):
        if getattr(candidate, "is_world_bound", False):
            return True
        return (
            getattr(candidate, "anchored", False)
            and getattr(candidate, "type", "") == "Rectangle"
            and getattr(candidate, "name", "") in {"Floor", "Ceiling", "LeftWall", "RightWall"}
        )

    def _delete_all_objects(self, objects):
        objects[:] = [obj for obj in objects if self._is_world_bound(obj)]
        return True

    def _remove_world_bounds(self, objects):
        objects[:] = [obj for obj in objects if not self._is_world_bound(obj)]
        return True

    def _recreate_world_bounds(self, objects):
        if self.world_window is None:
            return False
        self._remove_world_bounds(objects)
        PhysUtils.CreateWorldBounds(self.world_window, objects, thickness=self.world_thickness)
        return True

    def _repeatable_action(self, action):
        return action in {
            "size_minus",
            "size_plus",
            "mass_minus",
            "mass_plus",
            "speed_minus",
            "speed_plus",
            "angle_minus",
            "angle_plus",
            "segments_minus",
            "segments_plus",
        }

    def _apply_button_action(self, action, objects):
        if action == "shape_box":
            self.selected_shape = "Box"
        elif action == "shape_rectangle":
            self.selected_shape = "Rectangle"
        elif action == "shape_circle":
            self.selected_shape = "Circle"
        elif action == "shape_hexagon":
            self.selected_shape = "Hexagon"
        elif action == "size_minus":
            self._adjust_size(-5)
        elif action == "size_plus":
            self._adjust_size(5)
        elif action == "mass_minus":
            self._adjust_mass(-1)
        elif action == "mass_plus":
            self._adjust_mass(1)
        elif action == "speed_minus":
            self._adjust_speed(-1)
        elif action == "speed_plus":
            self._adjust_speed(1)
        elif action == "angle_minus":
            self._adjust_angle(-5)
        elif action == "angle_plus":
            self._adjust_angle(5)
        elif action == "anchor_toggle":
            self.anchored = not self.anchored
        elif action == "delete_toggle":
            self.delete_mode = not self.delete_mode
        elif action == "direction_toggle":
            self.direction_mode = not self.direction_mode
        elif action == "delete_all":
            self._delete_boundaries_and_keep_world(objects)
        elif action == "remove_bounds":
            self._remove_world_bounds(objects)
        elif action == "recreate_bounds":
            self._recreate_world_bounds(objects)
        elif action == "segments_minus":
            self._adjust_segments(-2)
        elif action == "segments_plus":
            self._adjust_segments(2)
        elif action == "reset":
            self.spawn_size = 100
            self.mass = 10
            self.anchored = False
            self.angle_fixed = 0
            self.velocity_speed = 2
            self.velocity_angle = 0
            self.circle_segments = 24
            self.delete_mode = False
            self.direction_mode = False
        else:
            return False
        return True

    def _set_active_button(self, action, rect):
        self._active_button_action = action
        self._active_button_rect = rect
        now = pygame.time.get_ticks()
        self._active_button_started_at = now
        self._active_button_next_repeat_at = now + self.button_repeat_delay_ms

    def _clear_active_button(self):
        self._active_button_action = None
        self._active_button_rect = None
        self._active_button_started_at = 0
        self._active_button_next_repeat_at = 0

    def update(self, objects):
        if self._active_button_action is None:
            return

        if not pygame.mouse.get_pressed()[0]:
            self._clear_active_button()
            return

        if self._active_button_rect is not None and not self._active_button_rect.collidepoint(pygame.mouse.get_pos()):
            self._clear_active_button()
            return

        if not self._repeatable_action(self._active_button_action):
            return

        now = pygame.time.get_ticks()
        if now < self._active_button_next_repeat_at:
            return

        self._apply_button_action(self._active_button_action, objects)
        self._active_button_next_repeat_at = now + self.button_repeat_interval_ms

    def spawn_selected(self, location):
        builders = {
            "Box": self._spawn_box,
            "Rectangle": self._spawn_rectangle,
            "Circle": self._spawn_circle,
            "Hexagon": self._spawn_hexagon,
        }
        builder = builders.get(self.selected_shape, self._spawn_box)
        return builder(location)

    def handle_event(self, event, objects):
        if event.type == pygame.KEYDOWN and event.key == self.toggle_key:
            self.visible = not self.visible
            return True

        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN and event.key in self.shape_keys:
            self.selected_shape = self.shape_keys[event.key]
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFTBRACKET:
            self._cycle_shape(-1)
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHTBRACKET:
            self._cycle_shape(1)
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            self.anchored = not self.anchored
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            self.delete_mode = not getattr(self, "delete_mode", False)
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_v:
            self.direction_mode = not getattr(self, "direction_mode", False)
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.angle_fixed = 0
            self.velocity_angle = 0
            self.velocity_speed = 2
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_EQUALS:
            self._adjust_size(5)
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_MINUS:
            self._adjust_size(-5)
            return True

        if event.type == pygame.MOUSEWHEEL:
            if self.direction_mode:
                self._adjust_angle(event.y * 5)
            else:
                self._adjust_size(event.y * 5)
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            objects.append(self.spawn_selected(pygame.mouse.get_pos()))
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._handle_button_click(event.pos, objects):
                return True
            if getattr(self, "delete_mode", False):
                return self._delete_object_at(event.pos, objects)
            objects.append(self.spawn_selected(event.pos))
            return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._clear_active_button()
            return False

        return False

    def _delete_object_at(self, pos, objects):
        for index in range(len(objects) - 1, -1, -1):
            candidate = objects[index]
            if candidate.anchored and candidate.type == "Rectangle" and getattr(candidate, "name", "") in {"Floor", "Ceiling", "LeftWall", "RightWall"}:
                continue
            points = PhysUtils.getWorldPolygonVertices(candidate)
            if len(points) < 3:
                continue
            if PhysUtils.pointInConvexPolygon(pos, points):
                del objects[index]
                return True
        return False

    def _delete_boundaries_and_keep_world(self, objects):
        return self._delete_all_objects(objects)

    def _handle_button_click(self, pos, objects):
        for button in getattr(self, "_buttons", []):
            if button["rect"].collidepoint(pos):
                action = button["action"]
                self._apply_button_action(action, objects)
                if self._repeatable_action(action):
                    self._set_active_button(action, button["rect"])
                else:
                    self._clear_active_button()
                return True
        return False

    def _preview_shape(self, location):
        center = location
        if self.selected_shape == "Box":
            return object.Box(location=list(center), diameter=self.spawn_size, angleFixed=self.angle_fixed)
        if self.selected_shape == "Rectangle":
            return object.Rectangle(location=list(center), diameters=self._shape_size_values(), angleFixed=self.angle_fixed)
        if self.selected_shape == "Circle":
            return object.Circle(location=list(center), diameter=self.spawn_size, segments=self.circle_segments)
        if self.selected_shape == "Hexagon":
            return object.Hexagon(location=list(center), diameter=self.spawn_size)
        return object.Box(location=list(center), diameter=self.spawn_size, angleFixed=self.angle_fixed)

    def _preview_points(self, shape):
        if hasattr(shape, "refreshPolygon"):
            shape.refreshPolygon()
        return getattr(shape, "worldVertices", [])

    def draw(self, surface):
        if not self.visible:
            return

        lines = [
            "Spawn Panel",
            f"Selected: {self.selected_shape}",
            f"Size: {self.spawn_size}",
            f"Mass: {self.mass}",
            f"Speed: {self.velocity_speed}",
            f"Angle: {self.velocity_angle if self.direction_mode else self.angle_fixed}",
            f"Anchored: {self.anchored}",
            f"Segments: {self.circle_segments}",
            f"Delete: {getattr(self, 'delete_mode', False)}",
            f"Direction: {self.direction_mode}",
            f"Held: {self._active_button_action or 'None'}",
        ]

        height = 480
        panel = pygame.Surface((self.width, height), pygame.SRCALPHA)
        panel.fill((18, 18, 24, 220))
        pygame.draw.rect(panel, (235, 235, 245), panel.get_rect(), width=2, border_radius=8)

        for index, text in enumerate(lines):
            color = (240, 240, 240)
            if text.startswith("Selected:"):
                color = (255, 220, 120)
            rendered = self.small_font.render(text, True, color)
            panel.blit(rendered, (12, 10 + index * 20))

        self._buttons = []
        start_x = 12
        start_y = 200
        button_rows = [
            [
                ("Box", "shape_box"),
                ("Rect", "shape_rectangle"),
                ("Circle", "shape_circle"),
            ],
            [
                ("Hex", "shape_hexagon"),
                ("Reset", "reset"),
                ("DelAll", "delete_all"),
            ],
            [
                ("RmBnd", "remove_bounds"),
                ("ReBnd", "recreate_bounds"),
                ("Mass-", "mass_minus"),
            ],
            [
                ("Mass+", "mass_plus"),
                ("Spd-", "speed_minus"),
                ("Spd+", "speed_plus"),
            ],
            [
                ("Size-", "size_minus"),
                ("Size+", "size_plus"),
                ("Anchor", "anchor_toggle"),
            ],
            [
                ("Ang-", "angle_minus"),
                ("Ang+", "angle_plus"),
                ("Aim", "direction_toggle"),
            ],
            [
                ("Seg-", "segments_minus"),
                ("Seg+", "segments_plus"),
            ],
        ]

        for row_index, row in enumerate(button_rows):
            y = start_y + row_index * (self.button_height + self.button_gap)
            for col_index, (label, action) in enumerate(row):
                x = start_x + col_index * (self.button_width + self.button_gap)
                rect = self._button(
                    panel,
                    x,
                    y,
                    self.button_width,
                    self.button_height,
                    label,
                    active=(
                        (action == "anchor_toggle" and self.anchored) or
                        (action == f"shape_{self.selected_shape.lower()}" if self.selected_shape != "Hexagon" else action == "shape_hexagon") or
                        (action == "direction_toggle" and getattr(self, "direction_mode", False))
                    )
                )
                self._buttons.append({"rect": rect.move(self.position), "action": action})

        hint_lines = [
            "Tab toggles panel",
            "Mouse wheel changes size",
            "Aim mode makes wheel change angle",
            "[ ] cycles shapes",
            "Left click a button to edit",
            "Click canvas to spawn",
            "D toggles delete mode",
            "V toggles aim mode",
            "Enter spawns at mouse",
        ]
        hint_y = 380
        for i, text in enumerate(hint_lines):
            rendered = self.small_font.render(text, True, (200, 200, 210))
            panel.blit(rendered, (12, hint_y + i * 16))

        surface.blit(panel, self.position)

    def draw_preview(self, surface, mouse_pos):
        if not self.visible:
            return

        shape = self._preview_shape(mouse_pos)
        if hasattr(shape, "refreshPolygon"):
            shape.refreshPolygon()

        points = getattr(shape, "worldVertices", [])
        if len(points) < 3:
            return

        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(overlay, (0, 0, 0, 40), points)
        pygame.draw.polygon(overlay, (80, 200, 255, 180), points, width=max(1, self.outline_width))
        pygame.draw.circle(overlay, (120, 220, 255, 255), mouse_pos, 3)

        center = mouse_pos
        preview_angle = math.radians(self.velocity_angle)
        end_point = (
            center[0] + math.cos(preview_angle) * 60,
            center[1] - math.sin(preview_angle) * 60,
        )
        arrow_color = (255, 120, 80, 220) if self.direction_mode else (80, 160, 255, 180)
        tip_color = (255, 120, 80, 255) if self.direction_mode else (80, 160, 255, 255)
        pygame.draw.line(overlay, arrow_color, center, end_point, 3)
        pygame.draw.circle(overlay, tip_color, end_point, 5)

        surface.blit(overlay, (0, 0))

class PhysUtils:
 
    # HELPER
     
    def GetHitboxBoundaries(Object : Box | Rectangle):
        if hasattr(Object, "radii") and Object.radii:
            hw,hy = Object.radii[0], Object.radii[1]
        else:
            hw,hy = Object.radius, Object.radius
            
        x = Object.location[0]
        y = Object.location[1]
        
        return {
            "Left":  x-hw,
            "Right": x+hw,
            "Top":   y-hy,
            "Bottom":y+hy
        }
    
    def objectOfTypeRadius(Object: Box | Rectangle):
        if hasattr(Object, "radii") and Object.radii:
            return Object.radii[0], Object.radii[1]
        else:
            return Object.radius, Object.radius
    
     
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

    def magnitude(vec):
        return math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])

    def normalize(vec):
        length = PhysUtils.magnitude(vec)
        if length == 0:
            return (0.0, 0.0)
        return (vec[0] / length, vec[1] / length)

    def rotatePoint(point, angle_radians):
        c = math.cos(angle_radians)
        s = math.sin(angle_radians)
        return (point[0] * c - point[1] * s, point[0] * s + point[1] * c)

    def generateCirclePolygon(center, radius, segments=24):
        if segments < 3:
            segments = 3

        points = []
        step = (2 * math.pi) / segments
        for i in range(segments):
            angle = step * i
            points.append((radius * math.cos(angle), radius * math.sin(angle)))
        return points

    def getObjectAngleRadians(obj):
        if hasattr(obj, "angleFixed") and obj.angleFixed is not None:
            return math.radians(obj.angleFixed)
        return 0.0

    def getLocalPolygonVertices(obj):
        if hasattr(obj, "localVertices") and obj.localVertices:
            return obj.localVertices
        if hasattr(obj, "local_vertices") and obj.local_vertices:
            return obj.local_vertices
        if hasattr(obj, "radii") and obj.radii:
            half_x, half_y = obj.radii
            return [
                (half_x, half_y),
                (half_x, -half_y),
                (-half_x, -half_y),
                (-half_x, half_y),
            ]
        if hasattr(obj, "radius"):
            half = obj.radius
            return [
                (half, half),
                (half, -half),
                (-half, -half),
                (-half, half),
            ]
        return []

    def getWorldPolygonVertices(obj):
        local_vertices = PhysUtils.getLocalPolygonVertices(obj)
        angle = PhysUtils.getObjectAngleRadians(obj)
        rotated = [PhysUtils.rotatePoint(vertex, angle) for vertex in local_vertices]
        return [PhysUtils.OffAdd(obj.location, vertex) for vertex in rotated]

    def getPolygonAxes(vertices):
        axes = []
        if len(vertices) < 2:
            return axes

        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            edge = PhysUtils.cSub(p2, p1)
            normal = PhysUtils.normalize((-edge[1], edge[0]))
            if normal != (0.0, 0.0):
                axes.append(normal)
        return axes

    def projectPolygon(vertices, axis):
        dots = [PhysUtils.dot(vertex, axis) for vertex in vertices]
        return min(dots), max(dots)

    def pointInConvexPolygon(point, vertices):
        if len(vertices) < 3:
            return False

        sign = 0
        px, py = point
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]
            cross = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
            if cross == 0:
                continue
            current = 1 if cross > 0 else -1
            if sign == 0:
                sign = current
            elif current != sign:
                return False
        return True

    def CreateSpawnPanel(
        toggle_key=pygame.K_TAB,
        position=(16, 16),
        width=260,
        spawn_size=100,
        world_window=None,
        world_objects=None,
        world_thickness=50,
    ):
        return SpawnPanel(
            toggle_key=toggle_key,
            position=position,
            width=width,
            spawn_size=spawn_size,
            world_window=world_window,
            world_objects=world_objects,
            world_thickness=world_thickness
        )
    
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
        if not hasattr(Object, "angleFixed"):
            return

        x = Object.location[0] + math.cos(Object.angleMotion) * 75
        y = Object.location[1] + -math.sin(Object.angleMotion) * 75

        pygame.draw.line(Surface, (0,0,255),
                        (Object.location[0], Object.location[1]),
                        (x, y), 3)

        if deg:
            gamecuts.displayText(Surface, font,
                str(math.degrees(Object.angleMotion)) + "°",
                color=(0,0,0),
                x=Object.location[0],
                y=Object.location[1])
        else:
            gamecuts.displayText(Surface, font,
                str(Object.angleMotion) + "rad",
                color=(0,0,0),
                x=Object.location[0],
                y=Object.location[1])

        angle_fixed = getattr(Object, "angleFixed", 0)
        x2 = Object.location[0] + math.cos(math.radians(angle_fixed)) * 75
        y2 = Object.location[1] + -math.sin(math.radians(angle_fixed)) * 75

        pygame.draw.line(Surface, (255,0,0),
                        (Object.location[0], Object.location[1]),
                        (x2, y2), 3)

        gamecuts.displayText(Surface, font,
            str(angle_fixed) + "°",
            color=(255,0,0),
            x=Object.location[0],
            y=Object.location[1]-15)
             
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
    def DetectCollision(Objects: list[Box | Rectangle | Circle]):
        return PhysUtils.DetectCollisionSAT(Objects)
    
    def DetectCollisionSAT(Objects: list[Box | Rectangle | Circle]):
        for i in range(len(Objects)):
            for j in range(i+1, len(Objects)):
                o1 = Objects[i]
                o2 = Objects[j]

                if o1 == o2:
                    continue

                o1_vertices = PhysUtils.getWorldPolygonVertices(o1)
                o2_vertices = PhysUtils.getWorldPolygonVertices(o2)

                if len(o1_vertices) < 3 or len(o2_vertices) < 3:
                    continue

                collisionAxes = PhysUtils.getPolygonAxes(o1_vertices) + PhysUtils.getPolygonAxes(o2_vertices)

                collision = True
                smallestAxis = None
                smallestOverlap = math.inf

                for axis in collisionAxes:
                    o1min, o1max = PhysUtils.projectPolygon(o1_vertices, axis)
                    o2min, o2max = PhysUtils.projectPolygon(o2_vertices, axis)

                    overlap = min(o1max, o2max) - max(o1min, o2min)

                    if o1max < o2min or o2max < o1min:
                        collision = False
                        break

                    if overlap < smallestOverlap:
                        smallestOverlap = overlap
                        smallestAxis = axis

                if not collision or smallestAxis is None:
                    continue

                dirVec = PhysUtils.cSub(o2.location, o1.location)

                if PhysUtils.dot(dirVec, smallestAxis) < 0:
                    smallestAxis = PhysUtils.cMul(smallestAxis, (-1, -1))

                MTV = PhysUtils.cMul(smallestAxis, smallestOverlap)
                halfMTV = PhysUtils.cDiv(MTV, (2, 2))

                if o1.anchored and o2.anchored:
                    continue
                elif o1.anchored:
                    o2.location = PhysUtils.cAdd(o2.location, MTV)
                elif o2.anchored:
                    o1.location = PhysUtils.cSub(o1.location, MTV)
                else:
                    o1.location = PhysUtils.cSub(o1.location, halfMTV)
                    o2.location = PhysUtils.cAdd(o2.location, halfMTV)

                RelativeVelocity = PhysUtils.cSub(o2.velocity, o1.velocity)
                velocityNormal = PhysUtils.dot(RelativeVelocity, smallestAxis)

                if velocityNormal > 0:
                    continue

                m1, m2 = o1.mass, o2.mass

                j = -(1 + 1) * velocityNormal
                j /= (1/m1 + 1/m2)

                impulse = PhysUtils.cMul(smallestAxis, j)

                if o1.anchored and o2.anchored:
                    continue
                elif o1.anchored:
                    o2.velocity = PhysUtils.cAdd(o2.velocity, PhysUtils.cDiv(impulse, (m2, m2)))
                elif o2.anchored:
                    o1.velocity = PhysUtils.cSub(o1.velocity, PhysUtils.cDiv(impulse, (m1, m1)))
                else:
                    o1.velocity = PhysUtils.cSub(o1.velocity, PhysUtils.cDiv(impulse, (m1, m1)))
                    o2.velocity = PhysUtils.cAdd(o2.velocity, PhysUtils.cDiv(impulse, (m2, m2)))

        return Objects


    #Use AABB Collision                                       
    def DetectCollisionAABB(Objects : list[Box | Rectangle | Circle]):
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
    

    # This method creates object.Rectangle objects around the edges of the screen
    @staticmethod
    def CreateWorldBounds(window, Objects, thickness=50):
        Objects[:] = [obj for obj in Objects if not getattr(obj, "is_world_bound", False)]
        width, height = window.get_size()

        half_t = thickness / 2

        # FLOOR
        Floor = object.Rectangle(
            name="Floor",
            mass=math.inf,
            location=[width / 2, height + half_t],
            diameters=[width + thickness * 2, thickness],
            angleFixed=0,
            velocity=[0, 0],
            anchored=True
        )
        Floor.is_world_bound = True

        # CEILING
        Ceiling = object.Rectangle(
            name="Ceiling",
            mass=math.inf,
            location=[width / 2, -half_t],
            diameters=[width + thickness * 2, thickness],
            angleFixed=0,
            velocity=[0, 0],
            anchored=True
        )
        Ceiling.is_world_bound = True

        # LEFT WALL
        LeftWall = object.Rectangle(
            name="LeftWall",
            mass=math.inf,
            location=[-half_t - 10, height / 2],
            diameters=[thickness, height + thickness * 2],
            angleFixed=0,
            velocity=[0, 0],
            anchored=True
        )
        LeftWall.is_world_bound = True

        # RIGHT WALL
        RightWall = object.Rectangle(
            name="RightWall",
            mass=math.inf,
            location=[width + half_t, height / 2],
            diameters=[thickness, height + thickness * 2],
            angleFixed=0,
            velocity=[0, 0],
            anchored=True
        )
        RightWall.is_world_bound = True

        bounds = [Floor, Ceiling, LeftWall, RightWall]
        Objects.extend(bounds)
        return bounds

    @staticmethod
    def CreateWorldBoundaries(window, Objects, thickness=50):
        return PhysUtils.CreateWorldBounds(window, Objects, thickness)

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
