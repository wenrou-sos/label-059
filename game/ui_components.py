import pygame
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY,
    LIGHT_GRAY, DARK_GRAY, RED, GREEN, YELLOW,
    STATION_TYPES
)

BLUE = (80, 160, 255)
from game.task_manager import TaskManager, TaskStatus, TaskPriority


class UIComponent:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def contains_point(self, pos):
        return self.get_rect().collidepoint(pos)

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class Button(UIComponent):
    def __init__(self, x, y, width, height, text, on_click=None,
                 color=(70, 70, 80), hover_color=(100, 100, 120),
                 text_color=WHITE, border_color=None):
        super().__init__(x, y, width, height)
        self.text = text
        self.on_click = on_click
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color or color
        self.hovered = False
        self.font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 16, bold=True)

    def handle_event(self, event):
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.contains_point(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(event.pos) and self.on_click:
                self.on_click()
                return True

        return False

    def draw(self, surface):
        if not self.visible:
            return

        current_color = self.hover_color if self.hovered and self.enabled else self.color
        if not self.enabled:
            current_color = (50, 50, 55)

        pygame.draw.rect(surface, current_color, self.get_rect(), border_radius=6)
        pygame.draw.rect(surface, self.border_color, self.get_rect(), 2, border_radius=6)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.get_rect().center)
        surface.blit(text_surf, text_rect)


class InputBox(UIComponent):
    def __init__(self, x, y, width, height, label='', default_text=''):
        super().__init__(x, y, width, height)
        self.label = label
        self.text = default_text
        self.active = False
        self.cursor_pos = len(self.text)
        self.cursor_timer = 0
        self.label_font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 14)
        self.text_font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 16)

    def handle_event(self, event):
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.contains_point(event.pos)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.unicode and event.unicode.isprintable():
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1

        return self.active

    def update(self, dt):
        self.cursor_timer += dt

    def draw(self, surface):
        if not self.visible:
            return

        if self.label:
            label_surf = self.label_font.render(self.label, True, LIGHT_GRAY)
            surface.blit(label_surf, (self.x, self.y - 20))

        bg_color = (40, 40, 50) if self.active else (35, 35, 45)
        border_color = YELLOW if self.active else GRAY

        pygame.draw.rect(surface, bg_color, self.get_rect(), border_radius=4)
        pygame.draw.rect(surface, border_color, self.get_rect(), 2, border_radius=4)

        text_surf = self.text_font.render(self.text, True, WHITE)
        surface.blit(text_surf, (self.x + 8, self.y + 8))

        if self.active and (self.cursor_timer // 500) % 2 == 0:
            cursor_x = self.x + 8 + self.text_font.size(self.text[:self.cursor_pos])[0]
            pygame.draw.line(surface, WHITE,
                             (cursor_x, self.y + 8),
                             (cursor_x, self.y + self.height - 8), 2)


class Dropdown(UIComponent):
    def __init__(self, x, y, width, height, label='', options=None, default_index=0):
        super().__init__(x, y, width, height)
        self.label = label
        self.options = options or []
        self.selected_index = default_index if options else 0
        self.expanded = False
        self.hovered_index = -1
        self.label_font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 14)
        self.text_font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 16)

    def get_selected_value(self):
        if self.options and 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return None

    def get_selected_key(self):
        value = self.get_selected_value()
        if isinstance(value, tuple) and len(value) >= 2:
            return value[0]
        return value

    def get_selected_label(self):
        value = self.get_selected_value()
        if isinstance(value, tuple) and len(value) >= 2:
            return value[1]
        return str(value) if value else ''

    def handle_event(self, event):
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(event.pos):
                self.expanded = not self.expanded
                return True
            elif self.expanded:
                item_height = self.height
                for i in range(len(self.options)):
                    item_rect = pygame.Rect(
                        self.x, self.y + self.height + i * item_height,
                        self.width, item_height
                    )
                    if item_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.expanded = False
                        return True
                self.expanded = False

        elif event.type == pygame.MOUSEMOTION and self.expanded:
            item_height = self.height
            self.hovered_index = -1
            for i in range(len(self.options)):
                item_rect = pygame.Rect(
                    self.x, self.y + self.height + i * item_height,
                    self.width, item_height
                )
                if item_rect.collidepoint(event.pos):
                    self.hovered_index = i
                    break

        return self.expanded

    def draw(self, surface):
        if not self.visible:
            return

        if self.label:
            label_surf = self.label_font.render(self.label, True, LIGHT_GRAY)
            surface.blit(label_surf, (self.x, self.y - 20))

        main_rect = self.get_rect()
        pygame.draw.rect(surface, (40, 40, 50), main_rect, border_radius=4)
        pygame.draw.rect(surface, YELLOW if self.expanded else GRAY, main_rect, 2, border_radius=4)

        text_surf = self.text_font.render(self.get_selected_label(), True, WHITE)
        surface.blit(text_surf, (self.x + 8, self.y + 8))

        arrow_points = [
            (self.x + self.width - 20, self.y + self.height // 2 - 5),
            (self.x + self.width - 10, self.y + self.height // 2 - 5),
            (self.x + self.width - 15, self.y + self.height // 2 + 5),
        ]
        pygame.draw.polygon(surface, WHITE, arrow_points)

        if self.expanded and self.options:
            total_height = len(self.options) * self.height
            dropdown_rect = pygame.Rect(self.x, self.y + self.height, self.width, total_height)
            pygame.draw.rect(surface, (30, 30, 40), dropdown_rect)
            pygame.draw.rect(surface, GRAY, dropdown_rect, 2)

            item_height = self.height
            for i, option in enumerate(self.options):
                item_rect = pygame.Rect(
                    self.x, self.y + self.height + i * item_height,
                    self.width, item_height
                )
                if i == self.hovered_index:
                    pygame.draw.rect(surface, (60, 60, 80), item_rect)

                label = option[1] if isinstance(option, tuple) and len(option) >= 2 else str(option)
                if isinstance(option, tuple) and len(option) >= 3:
                    color = option[2]
                    color_rect = pygame.Rect(self.x + 5, item_rect.y + 5, 10, item_height - 10)
                    pygame.draw.rect(surface, color, color_rect)
                    text_x = self.x + 25
                else:
                    text_x = self.x + 8

                text_surf = self.text_font.render(label, True, WHITE)
                surface.blit(text_surf, (text_x, item_rect.y + 8))


class TaskCard(UIComponent):
    def __init__(self, x, y, width, height, task, on_edit=None, on_delete=None, on_status_change=None):
        super().__init__(x, y, width, height)
        self.task = task
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_status_change = on_status_change
        self.font_title = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 16, bold=True)
        self.font_desc = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 12)
        self.font_small = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 11)

        self.edit_button = Button(x + width - 130, y + 5, 55, 25, '编辑',
                                  on_click=lambda: on_edit(task) if on_edit else None,
                                  color=(60, 100, 140), hover_color=(80, 130, 180))
        self.delete_button = Button(x + width - 70, y + 5, 55, 25, '删除',
                                    on_click=lambda: on_delete(task) if on_delete else None,
                                    color=(140, 60, 60), hover_color=(180, 80, 80))

        status_options = [
            ('pending', '待处理', GRAY),
            ('in_progress', '进行中', BLUE),
            ('completed', '已完成', GREEN),
            ('cancelled', '已取消', RED)
        ]
        current_status = task.status.value
        status_index = next((i for i, opt in enumerate(status_options) if opt[0] == current_status), 0)
        self.status_dropdown = Dropdown(
            x + width - 130, y + 35, 120, 24,
            label='', options=status_options, default_index=status_index
        )

    def handle_event(self, event):
        if not self.visible:
            return False

        self.edit_button.handle_event(event)
        self.delete_button.handle_event(event)
        if self.status_dropdown.handle_event(event):
            new_status = self.status_dropdown.get_selected_key()
            if new_status != self.task.status.value and self.on_status_change:
                self.on_status_change(self.task, new_status)
                self._update_status_dropdown()

        return False

    def _update_status_dropdown(self):
        current_status = self.task.status.value
        for i, opt in enumerate(self.status_dropdown.options):
            if opt[0] == current_status:
                self.status_dropdown.selected_index = i
                break

    def update(self, dt):
        self.edit_button.update(dt)
        self.delete_button.update(dt)
        self.status_dropdown.update(dt)

    def draw(self, surface):
        if not self.visible:
            return

        priority_colors = {
            'high': (200, 60, 60),
            'medium': (200, 160, 60),
            'low': (60, 160, 80)
        }
        status_colors = {
            'pending': GRAY,
            'in_progress': BLUE,
            'completed': GREEN,
            'cancelled': RED
        }

        card_rect = self.get_rect()
        border_color = priority_colors.get(self.task.priority.value, GRAY)
        pygame.draw.rect(surface, (45, 45, 55), card_rect, border_radius=6)
        pygame.draw.rect(surface, border_color, card_rect, 2, border_radius=6)

        status_color = status_colors.get(self.task.status.value, GRAY)
        pygame.draw.rect(surface, status_color,
                         (self.x + 4, self.y + 4, 4, self.height - 8))

        title_surf = self.font_title.render(self.task.title, True, WHITE)
        surface.blit(title_surf, (self.x + 15, self.y + 8))

        if self.task.description:
            desc_surf = self.font_desc.render(self.task.description[:40], True, LIGHT_GRAY)
            surface.blit(desc_surf, (self.x + 15, self.y + 28))

        if self.task.station_type:
            station_config = STATION_TYPES.get(self.task.station_type, {})
            station_name = station_config.get('name', self.task.station_type)
            station_color = station_config.get('color', GRAY)
            tag_rect = pygame.Rect(self.x + 15, self.y + 48, 70, 18)
            pygame.draw.rect(surface, station_color, tag_rect, border_radius=3)
            tag_surf = self.font_small.render(station_name, True, WHITE)
            tag_rect2 = tag_surf.get_rect(center=tag_rect.center)
            surface.blit(tag_surf, tag_rect2)

        priority_text = {'high': '高', 'medium': '中', 'low': '低'}
        priority_label = priority_text.get(self.task.priority.value, self.task.priority.value)
        priority_tag_rect = pygame.Rect(self.x + 95, self.y + 48, 40, 18)
        pygame.draw.rect(surface, priority_colors.get(self.task.priority.value, GRAY),
                         priority_tag_rect, border_radius=3)
        priority_surf = self.font_small.render(f'优:{priority_label}', True, WHITE)
        priority_rect2 = priority_surf.get_rect(center=priority_tag_rect.center)
        surface.blit(priority_surf, priority_rect2)

        progress = self.task.get_progress_percentage()
        progress_bg = pygame.Rect(self.x + 15, self.y + 72, 180, 14)
        pygame.draw.rect(surface, (30, 30, 40), progress_bg, border_radius=3)
        progress_w = 178 * (progress / 100)
        pygame.draw.rect(surface, GREEN, (self.x + 16, self.y + 73, progress_w, 12), border_radius=3)

        progress_surf = self.font_small.render(
            f'{self.task.current_count}/{self.task.target_count} ({progress:.0f}%)',
            True, WHITE
        )
        surface.blit(progress_surf, (self.x + 200, self.y + 72))

        self.edit_button.draw(surface)
        self.delete_button.draw(surface)
        self.status_dropdown.draw(surface)


class TaskManagerUI:
    def __init__(self, task_manager, on_close=None):
        self.task_manager = task_manager
        self.on_close = on_close
        self.visible = False
        self.components = []
        self.task_cards = []
        self.selected_task = None
        self.editing_task = None
        self.scroll_offset = 0
        self.scroll_speed = 30

        self.panel_x = 100
        self.panel_y = 50
        self.panel_w = SCREEN_WIDTH - 200
        self.panel_h = SCREEN_HEIGHT - 100

        self._init_fonts()
        self._init_filters()
        self._init_buttons()
        self._init_form()
        self._refresh_task_cards()

    def _init_fonts(self):
        self.font_title = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 28, bold=True)
        self.font_section = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 18, bold=True)
        self.font_small = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 14)

    def _init_filters(self):
        filter_y = self.panel_y + 80

        status_options = [
            ('all', '全部状态', WHITE),
            ('pending', '待处理', GRAY),
            ('in_progress', '进行中', BLUE),
            ('completed', '已完成', GREEN),
            ('cancelled', '已取消', RED)
        ]
        self.status_filter = Dropdown(
            self.panel_x + 20, filter_y, 150, 30,
            label='状态筛选', options=status_options, default_index=0
        )

        priority_options = [
            ('all', '全部优先级', WHITE),
            ('high', '高优先级', RED),
            ('medium', '中优先级', YELLOW),
            ('low', '低优先级', GREEN)
        ]
        self.priority_filter = Dropdown(
            self.panel_x + 200, filter_y, 150, 30,
            label='优先级筛选', options=priority_options, default_index=0
        )

        station_options = [('all', '全部工位', WHITE)]
        for st_key, st_config in STATION_TYPES.items():
            station_options.append((st_key, st_config['name'], st_config['color']))
        self.station_filter = Dropdown(
            self.panel_x + 380, filter_y, 150, 30,
            label='工位筛选', options=station_options, default_index=0
        )

        sort_options = [
            ('created_at', '按创建时间'),
            ('updated_at', '按更新时间'),
            ('priority', '按优先级'),
            ('status', '按状态'),
            ('progress', '按进度')
        ]
        self.sort_selector = Dropdown(
            self.panel_x + 560, filter_y, 150, 30,
            label='排序方式', options=sort_options, default_index=0
        )

    def _init_buttons(self):
        btn_y = self.panel_y + 135

        self.new_task_btn = Button(
            self.panel_x + 20, btn_y, 120, 35, '新建任务',
            on_click=self._open_new_task_form,
            color=(60, 140, 80), hover_color=(80, 180, 100)
        )

        self.refresh_btn = Button(
            self.panel_x + 155, btn_y, 100, 35, '刷新',
            on_click=self._refresh_task_cards,
            color=(80, 100, 120), hover_color=(100, 130, 160)
        )

        self.clear_completed_btn = Button(
            self.panel_x + 270, btn_y, 120, 35, '清除已完成',
            on_click=self._clear_completed,
            color=(140, 100, 60), hover_color=(180, 130, 80)
        )

        self.close_btn = Button(
            self.panel_x + self.panel_w - 120, self.panel_y + 15,
            100, 35, '关闭 (ESC)',
            on_click=self.close,
            color=(120, 60, 60), hover_color=(160, 80, 80)
        )

    def _init_form(self):
        form_x = self.panel_x + 20
        form_y = self.panel_y + 190
        form_w = self.panel_w - 40
        form_h = 200

        self.form_visible = False
        self.form_title = self.font_section.render('新建任务', True, YELLOW)

        self.title_input = InputBox(form_x + 20, form_y + 40, 300, 32, '任务名称')
        self.desc_input = InputBox(form_x + 350, form_y + 40, 380, 32, '任务描述')

        station_options = [(None, '不限工位', WHITE)]
        for st_key, st_config in STATION_TYPES.items():
            station_options.append((st_key, st_config['name'], st_config['color']))
        self.station_select = Dropdown(
            form_x + 20, form_y + 110, 180, 32,
            label='关联工位', options=station_options, default_index=0
        )

        priority_options = [
            ('low', '低', GREEN),
            ('medium', '中', YELLOW),
            ('high', '高', RED)
        ]
        self.priority_select = Dropdown(
            form_x + 230, form_y + 110, 180, 32,
            label='优先级', options=priority_options, default_index=1
        )

        self.target_input = InputBox(form_x + 440, form_y + 110, 100, 32, '目标数量', '10')

        self.submit_btn = Button(
            form_x + 570, form_y + 125, 100, 35, '创建',
            on_click=self._submit_form,
            color=(60, 140, 80), hover_color=(80, 180, 100)
        )

        self.cancel_btn = Button(
            form_x + 680, form_y + 125, 100, 35, '取消',
            on_click=self._close_form,
            color=(120, 80, 80), hover_color=(160, 100, 100)
        )

    def show(self):
        self.visible = True
        self._refresh_task_cards()

    def close(self):
        self.visible = False
        if self.on_close:
            self.on_close()

    def _open_new_task_form(self):
        self.editing_task = None
        self.form_title = self.font_section.render('新建任务', True, YELLOW)
        self.submit_btn.text = '创建'
        self.title_input.text = ''
        self.desc_input.text = ''
        self.station_select.selected_index = 0
        self.priority_select.selected_index = 1
        self.target_input.text = '10'
        self.form_visible = True

    def _open_edit_task_form(self, task):
        self.editing_task = task
        self.form_title = self.font_section.render('编辑任务', True, BLUE)
        self.submit_btn.text = '保存'
        self.title_input.text = task.title
        self.desc_input.text = task.description

        for i, opt in enumerate(self.station_select.options):
            if opt[0] == task.station_type:
                self.station_select.selected_index = i
                break

        for i, opt in enumerate(self.priority_select.options):
            if opt[0] == task.priority.value:
                self.priority_select.selected_index = i
                break

        self.target_input.text = str(task.target_count)
        self.form_visible = True

    def _close_form(self):
        self.form_visible = False
        self.editing_task = None

    def _submit_form(self):
        title = self.title_input.text.strip()
        if not title:
            return

        try:
            target_count = int(self.target_input.text) if self.target_input.text.strip() else 10
        except ValueError:
            target_count = 10

        station_type = self.station_select.get_selected_key()
        priority = self.priority_select.get_selected_key() or 'medium'
        description = self.desc_input.text.strip()

        if self.editing_task:
            self.task_manager.edit_task(
                self.editing_task.id,
                title=title,
                description=description,
                station_type=station_type,
                priority=priority,
                target_count=target_count
            )
        else:
            self.task_manager.create_task(
                title=title,
                description=description,
                station_type=station_type,
                priority=priority,
                target_count=target_count
            )

        self._close_form()
        self._refresh_task_cards()

    def _delete_task(self, task):
        self.task_manager.delete_task(task.id)
        self._refresh_task_cards()

    def _change_task_status(self, task, new_status):
        self.task_manager.set_task_status(task.id, new_status)
        self._refresh_task_cards()

    def _clear_completed(self):
        self.task_manager.clear_completed()
        self._refresh_task_cards()

    def _get_task_list_y(self):
        if self.form_visible:
            return self.panel_y + 410
        else:
            return self.panel_y + 220

    def _get_task_list_height(self):
        return self.panel_y + self.panel_h - 30 - self._get_task_list_y()

    def _refresh_task_cards(self):
        self.task_cards.clear()
        self.all_tasks = []

        status_filter = self.status_filter.get_selected_key()
        if status_filter == 'all':
            status_filter = None

        priority_filter = self.priority_filter.get_selected_key()
        if priority_filter == 'all':
            priority_filter = None

        station_filter = self.station_filter.get_selected_key()
        if station_filter == 'all':
            station_filter = None

        sort_by = self.sort_selector.get_selected_key() or 'created_at'

        self.all_tasks = self.task_manager.list_tasks(
            status_filter=status_filter,
            priority_filter=priority_filter,
            station_filter=station_filter,
            sort_by=sort_by
        )

        card_x = self.panel_x + 20
        card_w = self.panel_w - 60
        card_h = 95

        max_scroll = max(0, len(self.all_tasks) * (card_h + 5) - self._get_task_list_height())
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        start_y = self._get_task_list_y() - self.scroll_offset

        visible_count = 0
        for i, task in enumerate(self.all_tasks):
            card_y = start_y + i * (card_h + 5)
            if card_y + card_h < self._get_task_list_y():
                continue
            if card_y > self.panel_y + self.panel_h - 30:
                break

            card = TaskCard(
                card_x, card_y,
                card_w, card_h, task,
                on_edit=self._open_edit_task_form,
                on_delete=self._delete_task,
                on_status_change=self._change_task_status
            )
            self.task_cards.append(card)
            visible_count += 1

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.form_visible:
                self._close_form()
            else:
                self.close()
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h)
            if not panel_rect.collidepoint(event.pos) and not self.form_visible:
                self.close()
                return True

        if event.type == pygame.MOUSEWHEEL:
            if not self.form_visible:
                list_rect = pygame.Rect(
                    self.panel_x + 20, self._get_task_list_y(),
                    self.panel_w - 40, self._get_task_list_height()
                )
                if list_rect.collidepoint(pygame.mouse.get_pos()):
                    self.scroll_offset -= event.y * self.scroll_speed
                    self.scroll_offset = max(0, self.scroll_offset)
                    self._refresh_task_cards()
                    return True

        if self.form_visible:
            self.title_input.handle_event(event)
            self.desc_input.handle_event(event)
            self.station_select.handle_event(event)
            self.priority_select.handle_event(event)
            self.target_input.handle_event(event)
            self.submit_btn.handle_event(event)
            self.cancel_btn.handle_event(event)
            return True

        dropdown_expanded = (
            self.status_filter.expanded or
            self.priority_filter.expanded or
            self.station_filter.expanded or
            self.sort_selector.expanded
        )

        self.status_filter.handle_event(event)
        self.priority_filter.handle_event(event)
        self.station_filter.handle_event(event)
        self.sort_selector.handle_event(event)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not dropdown_expanded:
            self._refresh_task_cards()

        self.new_task_btn.handle_event(event)
        self.refresh_btn.handle_event(event)
        self.clear_completed_btn.handle_event(event)
        self.close_btn.handle_event(event)

        if not dropdown_expanded:
            for card in self.task_cards:
                card.handle_event(event)

        return True

    def update(self, dt):
        if not self.visible:
            return

        self.status_filter.update(dt)
        self.priority_filter.update(dt)
        self.station_filter.update(dt)
        self.sort_selector.update(dt)
        self.new_task_btn.update(dt)
        self.refresh_btn.update(dt)
        self.clear_completed_btn.update(dt)
        self.close_btn.update(dt)

        if self.form_visible:
            self.title_input.update(dt)
            self.desc_input.update(dt)
            self.station_select.update(dt)
            self.priority_select.update(dt)
            self.target_input.update(dt)
            self.submit_btn.update(dt)
            self.cancel_btn.update(dt)

        for card in self.task_cards:
            card.update(dt)

    def draw(self, surface):
        if not self.visible:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h)
        pygame.draw.rect(surface, (35, 35, 45), panel_rect, border_radius=10)
        pygame.draw.rect(surface, YELLOW, panel_rect, 3, border_radius=10)

        title_surf = self.font_title.render('任务管理中心', True, YELLOW)
        surface.blit(title_surf, (self.panel_x + 30, self.panel_y + 15))

        total_count = self.task_manager.get_task_count()
        pending_count = self.task_manager.get_task_count(status_filter=['pending'])
        progress_count = self.task_manager.get_task_count(status_filter=['in_progress'])
        completed_count = self.task_manager.get_task_count(status_filter=['completed'])

        stats_text = (
            f'总计: {total_count} | '
            f'待处理: {pending_count} | '
            f'进行中: {progress_count} | '
            f'已完成: {completed_count}'
        )
        stats_surf = self.font_small.render(stats_text, True, LIGHT_GRAY)
        surface.blit(stats_surf, (self.panel_x + 250, self.panel_y + 25))

        self.status_filter.draw(surface)
        self.priority_filter.draw(surface)
        self.station_filter.draw(surface)
        self.sort_selector.draw(surface)

        self.new_task_btn.draw(surface)
        self.refresh_btn.draw(surface)
        self.clear_completed_btn.draw(surface)
        self.close_btn.draw(surface)

        separator_y = self.panel_y + 180
        pygame.draw.line(surface, GRAY,
                         (self.panel_x + 20, separator_y),
                         (self.panel_x + self.panel_w - 20, separator_y), 1)

        if self.form_visible:
            form_rect = pygame.Rect(
                self.panel_x + 20, self.panel_y + 190,
                self.panel_w - 40, 200
            )
            pygame.draw.rect(surface, (45, 45, 55), form_rect, border_radius=8)
            pygame.draw.rect(surface, BLUE, form_rect, 2, border_radius=8)
            surface.blit(self.form_title, (form_rect.x + 15, form_rect.y + 10))

            self.title_input.draw(surface)
            self.desc_input.draw(surface)
            self.station_select.draw(surface)
            self.priority_select.draw(surface)
            self.target_input.draw(surface)
            self.submit_btn.draw(surface)
            self.cancel_btn.draw(surface)
        else:
            tasks_title = self.font_section.render('任务列表', True, WHITE)
            surface.blit(tasks_title, (self.panel_x + 25, self.panel_y + 195))

            list_y = self._get_task_list_y()
            list_h = self._get_task_list_height()

            clip_rect = pygame.Rect(
                self.panel_x + 10, list_y,
                self.panel_w - 20, list_h
            )

            old_clip = surface.get_clip()
            surface.set_clip(clip_rect)

            for card in self.task_cards:
                card.draw(surface)

            surface.set_clip(old_clip)

            total_tasks = len(self.all_tasks) if hasattr(self, 'all_tasks') else 0
            if total_tasks > 0:
                scrollbar_x = self.panel_x + self.panel_w - 25
                scrollbar_y = list_y + 5
                scrollbar_w = 12
                scrollbar_h = list_h - 10
                pygame.draw.rect(surface, (50, 50, 60),
                                 (scrollbar_x, scrollbar_y, scrollbar_w, scrollbar_h),
                                 border_radius=6)

                if total_tasks > 0:
                    card_h = 100
                    total_content_h = total_tasks * card_h
                    thumb_h = max(30, scrollbar_h * (list_h / total_content_h))
                    max_offset = max(1, total_content_h - list_h)
                    thumb_y = scrollbar_y + (self.scroll_offset / max_offset) * (scrollbar_h - thumb_h)
                    pygame.draw.rect(surface, YELLOW,
                                     (scrollbar_x + 2, thumb_y, scrollbar_w - 4, thumb_h),
                                     border_radius=4)

            if not self.task_cards and total_tasks == 0:
                no_task_surf = self.font_small.render(
                    '暂无任务，点击"新建任务"创建第一个任务吧！', True, LIGHT_GRAY
                )
                surface.blit(no_task_surf,
                             (self.panel_x + self.panel_w // 2 - 180, list_y + 50))

            if total_tasks > 0:
                count_text = f'共 {total_tasks} 个任务'
                count_surf = self.font_small.render(count_text, True, LIGHT_GRAY)
                surface.blit(count_surf, (self.panel_x + self.panel_w - 150, self.panel_y + 195))
