import sys
import os
import pygame

os.environ['SDL_VIDEO_CENTERED'] = '1'

from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game.game import Game


def main():
    try:
        pygame.init()
    except pygame.error as e:
        print(f"Pygame 初始化失败: {e}")
        print("请确保已正确安装 pygame: pip install pygame")
        sys.exit(1)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('流水线生产模拟器 - Factory Pipeline Simulator')

    icon_surface = pygame.Surface((32, 32))
    icon_surface.fill((255, 220, 80))
    pygame.draw.circle(icon_surface, (180, 120, 60), (16, 16), 12)
    pygame.draw.circle(icon_surface, (255, 255, 255), (16, 16), 6)
    pygame.display.set_icon(icon_surface)

    try:
        game = Game(screen)
        game.run()
    except Exception as e:
        print(f"游戏运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == '__main__':
    main()
