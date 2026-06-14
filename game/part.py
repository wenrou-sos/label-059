import math
import random
import pygame
from game.config import (
    PART_TYPES, PART_SIZE, CONVEYOR_X_START, CONVEYOR_X_END,
    CONVEYOR_Y, CONVEYOR_HEIGHT, YELLOW
)


class Part:
    def __init__(self, part_type=None, x=None, y=None):
        if part_type is None:
            part_type = random.choice(list(PART_TYPES.keys()))
        self.part_type = part_type
        self.config = PART_TYPES[part_type]
        self.name = self.config['name']
        self.color = self.config['color']
        self.target_station = self.config['target_station']
        self.shape = self.config['shape']
        self.size = PART_SIZE

        self.x = x if x is not None else CONVEYOR_X_START - self.size
        self.y = y if y is not None else CONVEYOR_Y + (CONVEYOR_HEIGHT - self.size) // 2
        self.origin_x = self.x
        self.origin_y = self.y

        self.speed = 0
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.missed = False
        self.returning = False
        self.return_speed = 8
        self.processed = False

    def update(self, speed):
        if self.dragging:
            return

        if self.returning:
            self._return_to_conveyor()
            return

        self.speed = speed
        self.x += self.speed
        self.origin_x = self.x
        self.origin_y = self.y

        if self.x > CONVEYOR_X_END:
            self.missed = True

    def _return_to_conveyor(self):
        dx = self.origin_x - self.x
        dy = self.origin_y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.return_speed:
            self.x = self.origin_x
            self.y = self.origin_y
            self.returning = False
        else:
            self.x += (dx / dist) * self.return_speed
            self.y += (dy / dist) * self.return_speed

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        size = self.size

        if self.shape == 'gear':
            self._draw_gear(surface, x, y, size)
        elif self.shape == 'screw':
            self._draw_screw(surface, x, y, size)
        elif self.shape == 'circuit':
            self._draw_circuit(surface, x, y, size)
        elif self.shape == 'chip':
            self._draw_chip(surface, x, y, size)
        elif self.shape == 'box':
            self._draw_box(surface, x, y, size)
        elif self.shape == 'label':
            self._draw_label(surface, x, y, size)

        self._draw_outline(surface, x, y, size)

    def _draw_gear(self, surface, x, y, size):
        cx = x + size // 2
        cy = y + size // 2
        outer_r = size // 2 - 2
        inner_r = size // 4
        teeth = 8

        for i in range(teeth):
            angle = (i * 360 / teeth) * math.pi / 180
            tx = cx + outer_r * math.cos(angle)
            ty = cy + outer_r * math.sin(angle)
            tooth_w = size // 8
            pygame.draw.rect(surface, self.color,
                             (tx - tooth_w // 2, ty - tooth_w // 2, tooth_w, tooth_w))

        pygame.draw.circle(surface, self.color, (cx, cy), outer_r - 4)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), inner_r)
        pygame.draw.circle(surface, (100, 60, 30), (cx, cy), inner_r - 4)

    def _draw_screw(self, surface, x, y, size):
        cx = x + size // 2
        head_r = size // 3
        shaft_w = size // 5
        shaft_h = size // 2

        head_y = y + size // 6
        pygame.draw.circle(surface, self.color, (cx, head_y), head_r)
        pygame.draw.circle(surface, (80, 80, 80), (cx, head_y), head_r - 3)

        shaft_top = head_y + head_r - 2
        pygame.draw.rect(surface, self.color,
                         (cx - shaft_w // 2, shaft_top, shaft_w, shaft_h))

        thread_offset = size // 20
        for i in range(3):
            ty = shaft_top + i * (shaft_h // 3) + 5
            pygame.draw.line(surface, (100, 100, 100),
                             (cx - shaft_w // 2 + thread_offset, ty),
                             (cx + shaft_w // 2 - thread_offset, ty + 3), 2)

        start_x = cx - shaft_w // 2
        start_y = shaft_top + shaft_h
        end_y = start_y + size // 10
        pygame.draw.polygon(surface, self.color, [
            (start_x, start_y),
            (start_x + shaft_w, start_y),
            (cx, end_y)
        ])

    def _draw_circuit(self, surface, x, y, size):
        margin = size // 10
        rect_w = size - 2 * margin
        rect_h = size - 2 * margin

        pygame.draw.rect(surface, self.color,
                         (x + margin, y + margin, rect_w, rect_h),
                         border_radius=3)

        line_color = (180, 255, 180)
        cx = x + size // 2
        cy = y + size // 2

        for i in range(3):
            ly = y + margin + 8 + i * 10
            pygame.draw.line(surface, line_color,
                             (x + margin + 5, ly),
                             (x + margin + rect_w - 5, ly), 1)

        pad_size = size // 8
        pad_positions = [
            (x + margin + 5, y + margin + 5),
            (x + size - margin - pad_size - 5, y + margin + 5),
            (x + margin + 5, y + size - margin - pad_size - 5),
            (x + size - margin - pad_size - 5, y + size - margin - pad_size - 5),
        ]
        for px, py in pad_positions:
            pygame.draw.rect(surface, (255, 215, 0),
                             (px, py, pad_size, pad_size), border_radius=2)

        pygame.draw.circle(surface, (255, 255, 255), (cx - 5, cy - 5), 3)
        pygame.draw.circle(surface, (255, 255, 255), (cx + 8, cy + 3), 2)

    def _draw_chip(self, surface, x, y, size):
        margin = size // 6
        body_w = size - 2 * margin
        body_h = size - 2 * margin

        pygame.draw.rect(surface, (30, 30, 30),
                         (x + margin, y + margin, body_w, body_h),
                         border_radius=2)
        pygame.draw.rect(surface, self.color,
                         (x + margin + 2, y + margin + 2, body_w - 4, body_h - 4),
                         border_radius=2)

        pin_w = 4
        pin_h = size // 10
        pin_count = 4

        for i in range(pin_count):
            px = x + margin + (i + 1) * body_w // (pin_count + 1) - pin_w // 2
            pygame.draw.rect(surface, (180, 180, 180),
                             (px, y + margin - pin_h, pin_w, pin_h))
            pygame.draw.rect(surface, (180, 180, 180),
                             (px, y + size - margin, pin_w, pin_h))

        for i in range(2):
            py = y + margin + (i + 1) * body_h // 3 - pin_w // 2
            pygame.draw.rect(surface, (180, 180, 180),
                             (x + margin - pin_h, py, pin_h, pin_w))
            pygame.draw.rect(surface, (180, 180, 180),
                             (x + size - margin, py, pin_h, pin_w))

    def _draw_box(self, surface, x, y, size):
        margin = size // 12
        box_w = size - 2 * margin
        box_h = size - 2 * margin

        pygame.draw.rect(surface, self.color,
                         (x + margin, y + margin, box_w, box_h),
                         border_radius=3)

        flap_h = box_h // 4
        cx = x + size // 2

        pygame.draw.polygon(surface, (self.color[0] - 30, self.color[1] - 20, self.color[2] - 20), [
            (x + margin, y + margin),
            (cx - 3, y + margin + flap_h // 2),
            (x + margin, y + margin + flap_h)
        ])
        pygame.draw.polygon(surface, (self.color[0] - 30, self.color[1] - 20, self.color[2] - 20), [
            (x + size - margin, y + margin),
            (cx + 3, y + margin + flap_h // 2),
            (x + size - margin, y + margin + flap_h)
        ])

        tape_w = box_w // 6
        pygame.draw.rect(surface, (230, 200, 120),
                         (cx - tape_w // 2, y + margin, tape_w, flap_h))
        pygame.draw.rect(surface, (230, 200, 120),
                         (cx - tape_w // 2, y + margin + flap_h, tape_w, box_h - flap_h))

        line_color = (140, 90, 40)
        pygame.draw.line(surface, line_color,
                         (x + margin, y + margin + flap_h),
                         (x + size - margin, y + margin + flap_h), 1)

    def _draw_label(self, surface, x, y, size):
        margin = size // 8
        label_w = size - 2 * margin
        label_h = size // 2

        base_y = y + (size - label_h) // 2
        pygame.draw.rect(surface, self.color,
                         (x + margin, base_y, label_w, label_h),
                         border_radius=4)

        border_color = (180, 180, 180)
        pygame.draw.rect(surface, border_color,
                         (x + margin, base_y, label_w, label_h), 2, border_radius=4)

        line_y1 = base_y + label_h // 3
        line_y2 = base_y + 2 * label_h // 3
        line_color = (120, 120, 120)
        pygame.draw.line(surface, line_color,
                         (x + margin + 6, line_y1),
                         (x + margin + label_w - 10, line_y1), 2)
        pygame.draw.line(surface, line_color,
                         (x + margin + 6, line_y2),
                         (x + margin + label_w - 16, line_y2), 2)

        barcode_w = label_w // 3
        barcode_x = x + size // 2 - barcode_w // 2
        barcode_y = base_y + 2
        for i in range(barcode_w // 3):
            if i % 2 == 0:
                bw = 2 if i % 4 == 0 else 1
                pygame.draw.line(surface, BLACK,
                                 (barcode_x + i * 3, barcode_y),
                                 (barcode_x + i * 3, barcode_y + 5), bw)

    def _draw_outline(self, surface, x, y, size):
        if self.dragging:
            outline_color = YELLOW = (255, 220, 80)
            outline_width = 3
            pygame.draw.rect(surface, outline_color,
                             (x - 2, y - 2, size + 4, size + 4),
                             outline_width, border_radius=4)

    def is_inside(self, pos):
        mx, my = pos
        return self.x <= mx <= self.x + self.size and self.y <= my <= self.y + self.size

    def start_drag(self, pos):
        mx, my = pos
        self.dragging = True
        self.drag_offset_x = mx - self.x
        self.drag_offset_y = my - self.y

    def update_drag(self, pos):
        if self.dragging:
            mx, my = pos
            self.x = mx - self.drag_offset_x
            self.y = my - self.drag_offset_y

    def end_drag(self):
        self.dragging = False

    def return_to_origin(self):
        self.returning = True

    def reset_origin(self, x=None, y=None):
        if x is not None:
            self.origin_x = x
        if y is not None:
            self.origin_y = y
        if not self.dragging:
            self.x = self.origin_x
            self.y = self.origin_y
