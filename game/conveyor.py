import pygame
from game.config import (
    CONVEYOR_X_START, CONVEYOR_X_END, CONVEYOR_Y, CONVEYOR_HEIGHT,
    CONVEYOR_WIDTH, LIGHT_GRAY, DARK_GRAY, GRAY, BLACK
)


class ConveyorBelt:
    def __init__(self):
        self.x_start = CONVEYOR_X_START
        self.x_end = CONVEYOR_X_END
        self.y = CONVEYOR_Y
        self.height = CONVEYOR_HEIGHT
        self.width = CONVEYOR_WIDTH
        self.roller_radius = self.height // 2
        self.belt_offset = 0
        self.speed = 0

    def update(self, speed):
        self.speed = speed
        self.belt_offset = (self.belt_offset + speed * 2) % 40

    def draw(self, surface):
        self._draw_frame(surface)
        self._draw_rollers(surface)
        self._draw_belt(surface)
        self._draw_texture_lines(surface)
        self._draw_end_markers(surface)

    def _draw_frame(self, surface):
        frame_color = (80, 80, 80)
        pygame.draw.rect(surface, frame_color,
                         (self.x_start - 10, self.y - 8,
                          self.width + 20, self.height + 16),
                         border_radius=6)

    def _draw_rollers(self, surface):
        roller_color = (100, 100, 100)
        dark_roller = (60, 60, 60)

        left_x = self.x_start
        right_x = self.x_end
        cy = self.y + self.height // 2

        pygame.draw.circle(surface, roller_color,
                           (left_x, cy), self.roller_radius)
        pygame.draw.circle(surface, dark_roller,
                           (left_x, cy), self.roller_radius - 4)

        pygame.draw.circle(surface, roller_color,
                           (right_x, cy), self.roller_radius)
        pygame.draw.circle(surface, dark_roller,
                           (right_x, cy), self.roller_radius - 4)

    def _draw_belt(self, surface):
        belt_top = self.y + 5
        belt_bottom = self.y + self.height - 5
        pygame.draw.rect(surface, GRAY,
                         (self.x_start, belt_top,
                          self.width, belt_bottom - belt_top))

    def _draw_texture_lines(self, surface):
        line_color = DARK_GRAY
        belt_top = self.y + 5
        belt_bottom = self.y + self.height - 5

        for i in range(-1, self.width // 40 + 2):
            x = self.x_start + i * 40 + self.belt_offset
            if self.x_start <= x <= self.x_end:
                pygame.draw.line(surface, line_color,
                                 (x, belt_top), (x, belt_bottom), 2)

    def _draw_end_markers(self, surface):
        cy = self.y + self.height // 2

        arrow_color = (0, 180, 255)
        arrow_size = 12
        start_x = self.x_end + 20

        for i in range(3):
            offset = i * 18
            pygame.draw.polygon(surface, arrow_color, [
                (start_x + offset, cy - arrow_size),
                (start_x + offset + arrow_size, cy),
                (start_x + offset, cy + arrow_size)
            ])
            arrow_color = tuple(max(0, c - 40) for c in arrow_color)

    def get_rect(self):
        return pygame.Rect(self.x_start, self.y, self.width, self.height)

    def is_above_conveyor(self, rect):
        conveyor_rect = self.get_rect()
        return rect.colliderect(conveyor_rect)
