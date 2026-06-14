import pygame
import random
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, GRAY,
    LIGHT_GRAY, DARK_GRAY, RED, GREEN, YELLOW,
    INITIAL_SPEED, SPEED_INCREMENT, MAX_SPEED,
    SPAWN_INTERVAL_START, SPAWN_INTERVAL_MIN, SPAWN_DECREMENT,
    MAX_MISSED_PARTS, SCORE_CORRECT, SCORE_WRONG,
    STATION_TYPES
)

BLUE = (80, 160, 255)
from game.conveyor import ConveyorBelt
from game.part import Part
from game.station import Station
from game.task_manager import TaskManager, TaskStatus, TaskPriority
from game.ui_components import TaskManagerUI


class GameState:
    MENU = 'menu'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'
    TASK_MANAGER = 'task_manager'


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self.running = True

        self.conveyor = ConveyorBelt()
        self.stations = []
        self.parts = []
        self.task_manager = TaskManager()

        self.score = 0
        self.missed_parts = 0
        self.speed = INITIAL_SPEED
        self.spawn_interval = SPAWN_INTERVAL_START
        self.last_spawn_time = 0
        self.game_time = 0

        self.dragged_part = None
        self.selected_part = None

        self._init_stations()
        self._init_tasks()
        self._init_fonts()
        self._init_effects()
        self._init_ui()

    def _init_stations(self):
        for i, station_type in enumerate(['assembly', 'qa', 'packaging']):
            self.stations.append(Station(station_type, i))

    def _init_tasks(self):
        self.task_manager.create_task(
            title='新手启动',
            description='完成10个零件的组装',
            station_type='assembly',
            priority='high',
            target_count=10
        )
        self.task_manager.create_task(
            title='质量控制',
            description='完成8个零件的质检',
            station_type='qa',
            priority='medium',
            target_count=8
        )
        self.task_manager.create_task(
            title='包装达人',
            description='完成6个零件的包装',
            station_type='packaging',
            priority='low',
            target_count=6
        )
        for task in self.task_manager.list_tasks(status_filter=['pending']):
            self.task_manager.start_task(task.id)

    def _init_fonts(self):
        self.font_large = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 48, bold=True)
        self.font_medium = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 28, bold=True)
        self.font_small = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 18)
        self.font_tiny = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 14)

    def _init_effects(self):
        self.effects = []
        self.score_popups = []

    def _init_ui(self):
        self.task_manager_ui = TaskManagerUI(
            self.task_manager,
            on_close=self._close_task_manager
        )

    def _close_task_manager(self):
        self.state = GameState.PLAYING

    def reset(self):
        self.parts.clear()
        self.score = 0
        self.missed_parts = 0
        self.speed = INITIAL_SPEED
        self.spawn_interval = SPAWN_INTERVAL_START
        self.last_spawn_time = 0
        self.game_time = 0
        self.dragged_part = None
        self.selected_part = None
        self.effects.clear()
        self.score_popups.clear()
        for station in self.stations:
            station.parts_processed = 0
        self.task_manager.clear_all()
        self._init_tasks()

    def handle_event(self, event):
        if self.state == GameState.MENU:
            self._handle_menu_event(event)
        elif self.state == GameState.PLAYING:
            self._handle_playing_event(event)
        elif self.state == GameState.PAUSED:
            self._handle_paused_event(event)
        elif self.state == GameState.GAME_OVER:
            self._handle_game_over_event(event)
        elif self.state == GameState.TASK_MANAGER:
            self.task_manager_ui.handle_event(event)

    def _handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.state = GameState.PLAYING
                self.reset()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.state = GameState.PLAYING
                self.reset()

    def _handle_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
            elif event.key == pygame.K_t:
                self.state = GameState.TASK_MANAGER
                self.task_manager_ui.show()
            elif event.key == pygame.K_1 and self.selected_part:
                self._place_part(0)
            elif event.key == pygame.K_2 and self.selected_part:
                self._place_part(1)
            elif event.key == pygame.K_3 and self.selected_part:
                self._place_part(2)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._handle_mouse_down(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self._handle_mouse_up(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.dragged_part:
                self.dragged_part.update_drag(event.pos)

    def _handle_paused_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                self.state = GameState.PLAYING
            elif event.key == pygame.K_r:
                self.state = GameState.PLAYING
                self.reset()
            elif event.key == pygame.K_m:
                self.state = GameState.MENU

    def _handle_game_over_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                self.state = GameState.PLAYING
                self.reset()
            elif event.key == pygame.K_m:
                self.state = GameState.MENU
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.state = GameState.PLAYING
                self.reset()

    def _handle_mouse_down(self, pos):
        for part in reversed(self.parts):
            if part.is_inside(pos) and not part.missed and not part.processed:
                if self.selected_part and self.selected_part is not part:
                    self.selected_part.dragging = False
                part.start_drag(pos)
                self.dragged_part = part
                self.selected_part = part
                return

        for i, station in enumerate(self.stations):
            if station.contains_point(pos) and self.selected_part:
                self._place_part(i)
                return

        if self.selected_part:
            self.selected_part.dragging = False
            self.selected_part = None

    def _handle_mouse_up(self, pos):
        if self.dragged_part:
            self.dragged_part.end_drag()
            placed = False

            for i, station in enumerate(self.stations):
                if station.contains_point(pos):
                    self._place_part(i)
                    placed = True
                    break

            if not placed:
                if not self.conveyor.is_above_conveyor(self.dragged_part.get_rect()):
                    pass
                else:
                    self.dragged_part.reset_origin()

            self.dragged_part = None

    def _place_part(self, station_index):
        if not self.selected_part:
            return

        station = self.stations[station_index]
        part = self.selected_part

        if station.can_accept(part):
            self.score += SCORE_CORRECT
            station.flash_correct()
            part.processed = True
            self._add_score_popup(part.x, part.y, f"+{SCORE_CORRECT}", GREEN)
            self.task_manager.update_progress(station_type=station.station_type)
            self.parts.remove(part)
        else:
            self.score += SCORE_WRONG
            station.flash_wrong()
            part.return_to_origin()
            self._add_score_popup(part.x, part.y, f"{SCORE_WRONG}", RED)

        self.selected_part = None

    def _add_score_popup(self, x, y, text, color):
        self.score_popups.append({
            'x': x, 'y': y,
            'text': text, 'color': color,
            'alpha': 255, 'vy': -2
        })

    def update(self):
        dt = self.clock.get_time()
        if self.state == GameState.PLAYING:
            self._update_game()
        elif self.state == GameState.TASK_MANAGER:
            self.task_manager_ui.update(dt)
        self._update_effects()

    def _update_game(self):
        dt = self.clock.get_rawtime()
        self.game_time += dt

        if self.game_time - self.last_spawn_time > self.spawn_interval:
            self._spawn_part()
            self.last_spawn_time = self.game_time

        for part in self.parts[:]:
            part.update(self.speed)
            if part.missed:
                self.missed_parts += 1
                self.parts.remove(part)
                self._add_score_popup(SCREEN_WIDTH - 100, 400, "MISS!", RED)
                if self.missed_parts >= MAX_MISSED_PARTS:
                    self.state = GameState.GAME_OVER

        for station in self.stations:
            station.update(dt)

        self.conveyor.update(self.speed)

        if self.speed < MAX_SPEED:
            self.speed += SPEED_INCREMENT * (dt / 1000)

        if self.spawn_interval > SPAWN_INTERVAL_MIN:
            self.spawn_interval -= SPAWN_DECREMENT * (dt / 1000)

    def _spawn_part(self):
        part = Part()
        self.parts.append(part)

    def _update_effects(self):
        for popup in self.score_popups[:]:
            popup['y'] += popup['vy']
            popup['alpha'] -= 3
            if popup['alpha'] <= 0:
                self.score_popups.remove(popup)

    def draw(self):
        self.screen.fill(DARK_GRAY)

        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.PLAYING:
            self._draw_game()
        elif self.state == GameState.PAUSED:
            self._draw_game()
            self._draw_paused()
        elif self.state == GameState.GAME_OVER:
            self._draw_game()
            self._draw_game_over()
        elif self.state == GameState.TASK_MANAGER:
            self._draw_game()
            self.task_manager_ui.draw(self.screen)

        self._draw_score_popups()
        pygame.display.flip()

    def _draw_menu(self):
        title = self.font_large.render('流水线生产模拟器', True, YELLOW)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH // 2, y=100)
        self.screen.blit(title, title_rect)

        subtitle = self.font_medium.render('Factory Pipeline Simulator', True, LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(centerx=SCREEN_WIDTH // 2, y=160)
        self.screen.blit(subtitle, subtitle_rect)

        instructions = [
            '游戏玩法：',
            '  1. 传送带上会不断出现各种零件',
            '  2. 拖拽零件到右侧对应的工位',
            '  3. 放对位置得分，放错扣分并退回',
            '  4. 速度会越来越快，坚持更久！',
            '',
            '操作方式：',
            '  鼠标左键拖拽 / 点击选中后按数字键 1-3',
            '  ESC - 暂停 | T - 任务管理',
            '',
            '按 空格键 或 点击 开始游戏'
        ]

        for i, line in enumerate(instructions):
            text = self.font_small.render(line, True, WHITE)
            self.screen.blit(text, (150, 220 + i * 32))

        self._draw_legend()

    def _draw_legend(self):
        legend_x = 700
        legend_y = 220

        title = self.font_medium.render('零件对应工位', True, YELLOW)
        self.screen.blit(title, (legend_x, legend_y))

        from game.config import PART_TYPES
        row = 0
        for part_type, config in PART_TYPES.items():
            station_name = STATION_TYPES[config['target_station']]['name']
            station_color = STATION_TYPES[config['target_station']]['color']

            color_rect = pygame.Rect(legend_x, legend_y + 40 + row * 35, 20, 20)
            pygame.draw.rect(self.screen, config['color'], color_rect)
            pygame.draw.rect(self.screen, BLACK, color_rect, 2)

            name_text = self.font_small.render(config['name'], True, WHITE)
            self.screen.blit(name_text, (legend_x + 30, legend_y + 40 + row * 35))

            arrow_text = self.font_small.render('→', True, LIGHT_GRAY)
            self.screen.blit(arrow_text, (legend_x + 100, legend_y + 40 + row * 35))

            station_rect = pygame.Rect(legend_x + 130, legend_y + 40 + row * 35, 20, 20)
            pygame.draw.rect(self.screen, station_color, station_rect)
            pygame.draw.rect(self.screen, BLACK, station_rect, 2)

            station_text = self.font_small.render(station_name, True, WHITE)
            self.screen.blit(station_text, (legend_x + 160, legend_y + 40 + row * 35))
            row += 1

    def _draw_game(self):
        self._draw_background()
        self.conveyor.draw(self.screen)

        for station in self.stations:
            station.draw(self.screen)

        for part in self.parts:
            if part is not self.dragged_part:
                part.draw(self.screen)

        if self.dragged_part:
            self.dragged_part.draw(self.screen)

        self._draw_hud()
        self._draw_tasks()
        self._draw_hints()

    def _draw_background(self):
        bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (30, 30, 40), bg_rect)

        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (40, 40, 50), (i, 0), (i, SCREEN_HEIGHT), 1)
        for i in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (40, 40, 50), (0, i), (SCREEN_WIDTH, i), 1)

        top_bar = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, (20, 20, 30), top_bar)
        pygame.draw.line(self.screen, YELLOW, (0, 60), (SCREEN_WIDTH, 60), 2)

    def _draw_hud(self):
        score_text = self.font_medium.render(f'得分: {self.score}', True, YELLOW)
        self.screen.blit(score_text, (30, 15))

        speed_text = self.font_small.render(f'速度: {self.speed:.1f}x', True, WHITE)
        self.screen.blit(speed_text, (250, 22))

        missed_text = self.font_small.render(
            f'漏件: {self.missed_parts}/{MAX_MISSED_PARTS}',
            True, RED if self.missed_parts > MAX_MISSED_PARTS * 0.7 else WHITE
        )
        self.screen.blit(missed_text, (400, 22))

        time_text = self.font_small.render(
            f'时间: {self.game_time // 1000}s', True, WHITE
        )
        self.screen.blit(time_text, (600, 22))

        lives_rect = pygame.Rect(800, 15, 150, 30)
        pygame.draw.rect(self.screen, (50, 50, 60), lives_rect, border_radius=5)
        life_width = (lives_rect.width - 4) * (1 - self.missed_parts / MAX_MISSED_PARTS)
        life_color = GREEN if self.missed_parts < MAX_MISSED_PARTS * 0.5 else (
            YELLOW if self.missed_parts < MAX_MISSED_PARTS * 0.8 else RED
        )
        pygame.draw.rect(self.screen, life_color,
                         (lives_rect.x + 2, lives_rect.y + 2, max(0, life_width), lives_rect.height - 4),
                         border_radius=4)
        lives_label = self.font_tiny.render('生命', True, WHITE)
        self.screen.blit(lives_label, (lives_rect.x + 55, lives_rect.y + 7))

    def _draw_tasks(self):
        task_panel_x = 820
        task_panel_y = 400
        task_panel_w = 360
        task_panel_h = 280

        panel_bg = pygame.Rect(task_panel_x, task_panel_y, task_panel_w, task_panel_h)
        pygame.draw.rect(self.screen, (35, 35, 45), panel_bg, border_radius=8)
        pygame.draw.rect(self.screen, YELLOW, panel_bg, 2, border_radius=8)

        title = self.font_medium.render('当前任务', True, YELLOW)
        self.screen.blit(title, (task_panel_x + 120, task_panel_y + 8))

        tasks = self.task_manager.list_tasks(
            status_filter=['in_progress', 'pending'],
            sort_by='priority'
        )

        task_y = task_panel_y + 50
        for i, task in enumerate(tasks[:4]):
            self._draw_task_card(task, task_panel_x + 10, task_y + i * 55, task_panel_w - 20, 48)

        hint = self.font_tiny.render('按 T 键打开完整任务管理', True, LIGHT_GRAY)
        self.screen.blit(hint, (task_panel_x + 80, task_panel_y + task_panel_h - 28))

    def _draw_task_card(self, task, x, y, w, h):
        card_rect = pygame.Rect(x, y, w, h)

        priority_colors = {
            'high': RED,
            'medium': YELLOW,
            'low': GREEN
        }
        border_color = priority_colors.get(task.priority.value, GRAY)
        pygame.draw.rect(self.screen, (50, 50, 60), card_rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, card_rect, 2, border_radius=5)

        status_colors = {
            'pending': GRAY,
            'in_progress': BLUE,
            'completed': GREEN,
            'cancelled': RED
        }
        status_color = status_colors.get(task.status.value, GRAY)
        pygame.draw.rect(self.screen, status_color, (x + 4, y + 4, 6, h - 8))

        title = self.font_small.render(task.title, True, WHITE)
        self.screen.blit(title, (x + 20, y + 5))

        progress = task.get_progress_percentage()
        progress_bg = pygame.Rect(x + 20, y + 28, w - 120, 14)
        pygame.draw.rect(self.screen, (30, 30, 40), progress_bg, border_radius=3)
        progress_w = (w - 122) * (progress / 100)
        pygame.draw.rect(self.screen, GREEN, (x + 21, y + 29, progress_w, 12), border_radius=3)

        progress_text = self.font_tiny.render(
            f'{task.current_count}/{task.target_count}', True, WHITE
        )
        self.screen.blit(progress_text, (x + w - 90, y + 28))

        if task.station_type:
            station_color = STATION_TYPES[task.station_type]['color']
            station_name = STATION_TYPES[task.station_type]['name']
            tag_rect = pygame.Rect(x + w - 90, y + 5, 80, 18)
            pygame.draw.rect(self.screen, station_color, tag_rect, border_radius=3)
            tag_text = self.font_tiny.render(station_name, True, WHITE)
            text_rect = tag_text.get_rect(center=tag_rect.center)
            self.screen.blit(tag_text, text_rect)

    def _draw_hints(self):
        hints = [
            '拖拽零件到对应工位 或 点击选中后按 1/2/3',
            'ESC 暂停 | T 任务管理'
        ]
        for i, hint in enumerate(hints):
            text = self.font_tiny.render(hint, True, LIGHT_GRAY)
            self.screen.blit(text, (30, SCREEN_HEIGHT - 35 + i * 18))

    def _draw_paused(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render('游戏暂停', True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(title, title_rect)

        options = [
            ('ESC / 空格', '继续游戏'),
            ('R', '重新开始'),
            ('M', '返回菜单')
        ]

        for i, (key, action) in enumerate(options):
            key_text = self.font_small.render(key, True, YELLOW)
            action_text = self.font_small.render(action, True, WHITE)
            y = SCREEN_HEIGHT // 2 + i * 40
            self.screen.blit(key_text, (SCREEN_WIDTH // 2 - 150, y))
            self.screen.blit(action_text, (SCREEN_WIDTH // 2 - 30, y))

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render('游戏结束', True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(title, title_rect)

        score_text = self.font_medium.render(f'最终得分: {self.score}', True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(score_text, score_rect)

        time_text = self.font_small.render(f'坚持时间: {self.game_time // 1000} 秒', True, WHITE)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(time_text, time_rect)

        processed = sum(s.parts_processed for s in self.stations)
        processed_text = self.font_small.render(f'处理零件: {processed} 个', True, WHITE)
        processed_rect = processed_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 45))
        self.screen.blit(processed_text, processed_rect)

        completed_tasks = self.task_manager.get_task_count(status_filter=['completed'])
        task_text = self.font_small.render(f'完成任务: {completed_tasks} 个', True, GREEN)
        task_rect = task_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(task_text, task_rect)

        options = [
            ('空格 / R', '再来一局'),
            ('M', '返回菜单')
        ]

        for i, (key, action) in enumerate(options):
            key_text = self.font_small.render(key, True, YELLOW)
            action_text = self.font_small.render(action, True, WHITE)
            y = SCREEN_HEIGHT // 2 + 130 + i * 40
            self.screen.blit(key_text, (SCREEN_WIDTH // 2 - 150, y))
            self.screen.blit(action_text, (SCREEN_WIDTH // 2 - 30, y))

    def _draw_score_popups(self):
        for popup in self.score_popups:
            text = self.font_medium.render(popup['text'], True, popup['color'])
            text.set_alpha(popup['alpha'])
            self.screen.blit(text, (popup['x'], popup['y']))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.state == GameState.TASK_MANAGER:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                else:
                    self.handle_event(event)

            self.update()
            self.draw()
            self.clock.tick(FPS)
