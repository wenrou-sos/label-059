
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
BLUE = (80, 160, 255)
YELLOW = (255, 220, 80)
ORANGE = (255, 160, 60)
CYAN = (80, 255, 255)
PURPLE = (180, 100, 255)

CONVEYOR_Y = 450
CONVEYOR_X_START = 50
CONVEYOR_X_END = 750
CONVEYOR_HEIGHT = 80
CONVEYOR_WIDTH = CONVEYOR_X_END - CONVEYOR_X_START

STATION_Y = 200
STATION_WIDTH = 140
STATION_HEIGHT = 180
STATION_X_START = 820
STATION_GAP = 30

INITIAL_SPEED = 1.5
SPEED_INCREMENT = 0.05
MAX_SPEED = 8.0

SPAWN_INTERVAL_START = 2500
SPAWN_INTERVAL_MIN = 600
SPAWN_DECREMENT = 80

MAX_MISSED_PARTS = 10
SCORE_CORRECT = 10
SCORE_WRONG = -15

PART_SIZE = 60

PART_TYPES = {
    'gear': {
        'name': '齿轮',
        'color': (180, 120, 60),
        'target_station': 'assembly',
        'shape': 'gear'
    },
    'screw': {
        'name': '螺丝',
        'color': (160, 160, 160),
        'target_station': 'assembly',
        'shape': 'screw'
    },
    'circuit': {
        'name': '电路板',
        'color': (60, 160, 80),
        'target_station': 'qa',
        'shape': 'circuit'
    },
    'chip': {
        'name': '芯片',
        'color': (100, 60, 160),
        'target_station': 'qa',
        'shape': 'chip'
    },
    'box': {
        'name': '包装盒',
        'color': (200, 140, 80),
        'target_station': 'packaging',
        'shape': 'box'
    },
    'label': {
        'name': '标签',
        'color': (220, 220, 220),
        'target_station': 'packaging',
        'shape': 'label'
    }
}

STATION_TYPES = {
    'assembly': {
        'name': '组装工位',
        'color': BLUE,
        'description': '组装零件'
    },
    'qa': {
        'name': '质检工位',
        'color': GREEN,
        'description': '质量检测'
    },
    'packaging': {
        'name': '包装工位',
        'color': ORANGE,
        'description': '产品包装'
    }
}

TASK_STATUSES = ['pending', 'in_progress', 'completed', 'cancelled']
TASK_PRIORITIES = ['low', 'medium', 'high']
