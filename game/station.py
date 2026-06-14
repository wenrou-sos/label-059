import pygame
from game.config import (
    STATION_X_START, STATION_Y, STATION_WIDTH, STATION_HEIGHT,
    STATION_GAP, STATION_TYPES, WHITE
)


class Station:
    def __init__(self, station_type, index):
        self.station_type = station_type
        self.index = index
        self.config = STATION_TYPES[station_type]
        self.name = self.config['name']
        self.color = self.config['color']
        self.description = self.config['description']

        self.x = STATION_X_START + index * (STATION_WIDTH + STATION_GAP)
        self.y = STATION_Y
        self.width = STATION_WIDTH
        self.height = STATION_HEIGHT

        self.parts_processed = 0
        self.highlight = False
        self.highlight_correct = False
        self.highlight_wrong = False
        self.highlight_timer = 0
        self.pulse_timer = 0

    def update(self, dt):
        if self.highlight_timer > 0:
            self.highlight_timer -= dt
            if self.highlight_timer <= 0:
                self.highlight = False
                self.highlight_correct = False
                self.highlight_wrong = False
        self.pulse_timer += dt

    def draw(self, surface):
        self._draw_base(surface)
        self._draw_header(surface)
        self._draw_content(surface)
        self._draw_stats(surface)
        self._draw_highlight(surface)
        self._draw_border(surface)

    def _draw_base(self, surface):
        base_color = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.rect(surface, base_color,
                         (self.x, self.y, self.width, self.height),
                         border_radius=10)

    def _draw_header(self, surface):
        header_h = 40
        header_rect = pygame.Rect(self.x, self.y, self.width, header_h)
        pygame.draw.rect(surface, self.color, header_rect,
                         border_top_left_radius=10, border_top_right_radius=10)

        font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 18, bold=True)
        text_surf = font.render(self.name, True, WHITE)
        text_rect = text_surf.get_rect(center=header_rect.center)
        surface.blit(text_surf, text_rect)

    def _draw_content(self, surface):
        icon_y = self.y + 60
        icon_x = self.x + self.width // 2
        icon_size = 60

        pulse = 0
        if self.highlight:
            pulse = int(3 * (1 + (self.pulse_timer // 100) % 2))

        if self.station_type == 'assembly':
            self._draw_assembly_icon(surface, icon_x, icon_y, icon_size, pulse)
        elif self.station_type == 'qa':
            self._draw_qa_icon(surface, icon_x, icon_y, icon_size, pulse)
        elif self.station_type == 'packaging':
            self._draw_packaging_icon(surface, icon_x, icon_y, icon_size, pulse)

        desc_font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 12)
        desc_surf = desc_font.render(self.description, True, WHITE)
        desc_rect = desc_surf.get_rect(centerx=icon_x, top=icon_y + icon_size + 10)
        surface.blit(desc_surf, desc_rect)

    def _draw_assembly_icon(self, surface, cx, cy, size, pulse):
        gear_r = size // 3
        teeth = 8
        import math

        for i in range(teeth):
            angle = (i * 360 / teeth) * math.pi / 180
            tx = cx + (gear_r + pulse) * math.cos(angle)
            ty = cy + (gear_r + pulse) * math.sin(angle)
            tooth_w = size // 10
            pygame.draw.rect(surface, (255, 200, 100),
                             (tx - tooth_w // 2, ty - tooth_w // 2,
                              tooth_w, tooth_w))

        pygame.draw.circle(surface, (255, 180, 80),
                           (cx, cy), gear_r - 2 + pulse)
        pygame.draw.circle(surface, (200, 120, 40),
                           (cx, cy), gear_r // 2 + pulse)

        sx = cx + size // 2 + 5
        sy = cy + 5
        pygame.draw.circle(surface, (180, 180, 180),
                           (sx, sy), size // 5)
        pygame.draw.rect(surface, (160, 160, 160),
                         (sx - 4, sy + size // 6, 8, size // 4))

    def _draw_qa_icon(self, surface, cx, cy, size, pulse):
        magnifier_r = size // 3
        handle_len = size // 3

        pygame.draw.circle(surface, (100, 255, 150),
                           (cx - 10, cy - 5), magnifier_r + pulse)
        pygame.draw.circle(surface, (60, 200, 100),
                           (cx - 10, cy - 5), magnifier_r - 4 + pulse)
        pygame.draw.circle(surface, WHITE,
                           (cx - 10, cy - 5), magnifier_r // 2 + pulse)

        hx = cx + magnifier_r // 2
        hy = cy + magnifier_r // 2
        pygame.draw.line(surface, (120, 80, 40),
                         (hx, hy),
                         (hx + handle_len * 0.7, hy + handle_len * 0.7), 8)

        check_x = cx - 10
        check_y = cy - 5
        pygame.draw.line(surface, (0, 200, 80),
                         (check_x - magnifier_r // 3, check_y),
                         (check_x - magnifier_r // 6, check_y + magnifier_r // 3), 3)
        pygame.draw.line(surface, (0, 200, 80),
                         (check_x - magnifier_r // 6, check_y + magnifier_r // 3),
                         (check_x + magnifier_r // 3, check_y - magnifier_r // 4), 3)

    def _draw_packaging_icon(self, surface, cx, cy, size, pulse):
        box_w = size // 1.5
        box_h = size // 1.8
        bx = cx - box_w // 2
        by = cy - box_h // 2

        pygame.draw.rect(surface, (230, 160, 80),
                         (bx + pulse, by + pulse, box_w - 2 * pulse, box_h - 2 * pulse),
                         border_radius=3)

        flap_h = box_h // 4
        top_color = (200, 130, 60)
        pygame.draw.polygon(surface, top_color, [
            (bx + pulse, by + pulse),
            (cx - 3, by + flap_h // 2),
            (bx + pulse, by + flap_h + pulse)
        ])
        pygame.draw.polygon(surface, top_color, [
            (bx + box_w - pulse, by + pulse),
            (cx + 3, by + flap_h // 2),
            (bx + box_w - pulse, by + flap_h + pulse)
        ])

        tape_w = box_w // 5
        pygame.draw.rect(surface, (255, 220, 120),
                         (cx - tape_w // 2, by + pulse, tape_w, box_h - 2 * pulse))

        ribbon_y = by - 8
        pygame.draw.line(surface, (255, 80, 80),
                         (cx - box_w // 4, ribbon_y),
                         (cx + box_w // 4, ribbon_y), 4)
        pygame.draw.circle(surface, (255, 80, 80),
                           (cx, ribbon_y), 6)

    def _draw_stats(self, surface):
        stat_y = self.y + self.height - 35
        stat_rect = pygame.Rect(self.x + 10, stat_y, self.width - 20, 25)

        pygame.draw.rect(surface, (0, 0, 0, 128), stat_rect, border_radius=5)

        stat_font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 14, bold=True)
        stat_text = f"已处理: {self.parts_processed}"
        text_surf = stat_font.render(stat_text, True, WHITE)
        text_rect = text_surf.get_rect(center=stat_rect.center)
        surface.blit(text_surf, text_rect)

    def _draw_highlight(self, surface):
        if not self.highlight:
            return

        if self.highlight_correct:
            hl_color = (0, 255, 100)
        elif self.highlight_wrong:
            hl_color = (255, 80, 80)
        else:
            hl_color = self.color

        hl_width = 4
        pygame.draw.rect(surface, hl_color,
                         (self.x - hl_width, self.y - hl_width,
                          self.width + 2 * hl_width, self.height + 2 * hl_width),
                         hl_width, border_radius=12)

    def _draw_border(self, surface):
        border_color = tuple(min(255, c + 30) for c in self.color)
        pygame.draw.rect(surface, border_color,
                         (self.x, self.y, self.width, self.height),
                         2, border_radius=10)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def contains_point(self, pos):
        return self.get_rect().collidepoint(pos)

    def contains_rect(self, rect):
        return self.get_rect().contains(rect) or self.get_rect().colliderect(rect)

    def flash_correct(self, duration=500):
        self.highlight = True
        self.highlight_correct = True
        self.highlight_wrong = False
        self.highlight_timer = duration
        self.parts_processed += 1

    def flash_wrong(self, duration=500):
        self.highlight = True
        self.highlight_correct = False
        self.highlight_wrong = True
        self.highlight_timer = duration

    def can_accept(self, part):
        return part.target_station == self.station_type
