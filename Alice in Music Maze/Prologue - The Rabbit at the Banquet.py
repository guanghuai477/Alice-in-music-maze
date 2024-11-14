'''
这是注释：
左上是起点，右下是终点，玩家通过ASDW移动，注意提前调整键盘至 “英文模式 ”。
迷宫为 15 行，20 列，注意编程默认从 “0” 开始计数。每个格子均有对应坐标，注释在迷宫数组的右侧。
蓝色小点为缩小药水的位置，玩家碰撞到药水会变小。
(11, 9) 和 (13, 9) 为特殊格子，检测到玩家变小后才允许通过。添加图片素材时这两个格子需要和正常道路的格子区分开，显示出这里是需要喝药水变小才能通过的窄路。
    例如正常格子是草地素材，这里就是藤蔓素材。

11.14更新内容：
增加了绿色的引导小球（即兔子先生），引导玩家走到迷宫终点。
增加了玩家走过的格子的变白效果（后期可以替换成花朵生长的动画）。
增加了游戏开始时的对话框，方便添加故事情节和新手引导。
格子大小标准为40像素*40像素，尝试铺了草地素材，素材名称为grass2.gif。
'''

import pygame
import sys
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
PLAYER_RADIUS = 15
PLAYER_COLOR = "white"
GUIDE_COLOR = "green"
BACKGROUND_COLOR = "white"
MAZE_COLOR = "black"
ITEM_COLOR = "blue"
VISITED_COLOR = "white"
DIALOG_BOX_COLOR = (200, 200, 200)
DIALOG_TEXT_COLOR = (0, 0, 0)
FPS = 30
PLAYER_SPEED = 5
GUIDE_SPEED = 3  # Slightly slower than the player

# Maze layout (1 represents wall, 0 represents path)
MAZE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Player starting position
player_pos = [1 * TILE_SIZE + TILE_SIZE // 2, 1 * TILE_SIZE + TILE_SIZE // 2]

# Guide starting position
guide_pos = [3 * TILE_SIZE + TILE_SIZE // 2, 3 * TILE_SIZE + TILE_SIZE // 2]

# Item position (to shrink player)
item_pos = [9 * TILE_SIZE + TILE_SIZE // 2, 3 * TILE_SIZE + TILE_SIZE // 2]

# Exit position
exit_pos = (18, 13)  # Grid position of the exit

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")
clock = pygame.time.Clock()

# Load and scale the grass image
grass_image = pygame.image.load("grass2.gif")
grass_image = pygame.transform.scale(grass_image, (TILE_SIZE, TILE_SIZE))

# Track visited tiles
visited_tiles = {}

# Font setup
font = pygame.font.SysFont(None, 24)

def draw_maze():
    for y, row in enumerate(MAZE):
        for x, tile in enumerate(row):
            if tile == 1:
                color = MAZE_COLOR
                pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            else:
                screen.blit(grass_image, (x * TILE_SIZE, y * TILE_SIZE))
                if (x, y) in visited_tiles:
                    pygame.draw.rect(screen, VISITED_COLOR, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

def draw_dialog_box():
    dialog_rect = pygame.Rect((WIDTH - 700) // 2, HEIGHT - 100, 700, 100)
    pygame.draw.rect(screen, DIALOG_BOX_COLOR, dialog_rect)
    pygame.draw.rect(screen, DIALOG_TEXT_COLOR, dialog_rect, 2)  # Border

    # Draw the name "Alice" at the top-left corner of the dialog box
    name_text = font.render("Alice", True, DIALOG_TEXT_COLOR)
    screen.blit(name_text, (dialog_rect.x + 10, dialog_rect.y + 5))

    # Draw the dialog text
    dialog_text = font.render("The wind in the forest is so comfortable ...... Huh? What's that white thing in front?", True, DIALOG_TEXT_COLOR)
    screen.blit(dialog_text, (dialog_rect.x + 10, dialog_rect.y + 40))

def is_colliding(pos1, pos2, radius):
    return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2 < radius ** 2

def can_move(new_pos, radius, player_shrunk):
    grid_x = new_pos[0] // TILE_SIZE
    grid_y = new_pos[1] // TILE_SIZE
    if 0 <= grid_x < len(MAZE[0]) and 0 <= grid_y < len(MAZE):
        if MAZE[grid_y][grid_x] == 0:
            if (grid_x, grid_y) in [(11, 9), (13, 9)]:
                return player_shrunk
            return True
    return False

def update_visited_tiles(player_pos):
    grid_x = player_pos[0] // TILE_SIZE
    grid_y = player_pos[1] // TILE_SIZE
    visited_tiles[(grid_x, grid_y)] = 0  # Mark the tile as visited

    # Update distances for all visited tiles
    for tile in list(visited_tiles.keys()):
        distance = abs(tile[0] - grid_x) + abs(tile[1] - grid_y)
        if distance > 3:
            del visited_tiles[tile]  # Remove tile if it's more than 3 tiles away

def bfs_path(start, goal):
    queue = deque([start])
    came_from = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        x, y = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (x + dx, y + dy)
            if 0 <= neighbor[0] < len(MAZE[0]) and 0 <= neighbor[1] < len(MAZE):
                if MAZE[neighbor[1]][neighbor[0]] == 0 and neighbor not in came_from:
                    queue.append(neighbor)
                    came_from[neighbor] = current
    path = []
    current = goal
    while current:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

guide_path = bfs_path((3, 3), exit_pos)
guide_index = 0

player_shrunk = False
dialog_displayed = True
dialog_start_time = pygame.time.get_ticks()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    new_pos = player_pos[:]
    if keys[pygame.K_w]:
        new_pos[1] -= PLAYER_SPEED
    if keys[pygame.K_s]:
        new_pos[1] += PLAYER_SPEED
    if keys[pygame.K_a]:
        new_pos[0] -= PLAYER_SPEED
    if keys[pygame.K_d]:
        new_pos[0] += PLAYER_SPEED

    if can_move(new_pos, PLAYER_RADIUS, player_shrunk):
        player_pos = new_pos
        update_visited_tiles(player_pos)

    if is_colliding(player_pos, item_pos, PLAYER_RADIUS):
        player_shrunk = True

    current_player_radius = PLAYER_RADIUS // 2 if player_shrunk else PLAYER_RADIUS

    # Move the guide along the path only after the dialog is closed
    if not dialog_displayed and guide_index < len(guide_path):
        guide_grid_pos = guide_path[guide_index]
        guide_pos = [guide_grid_pos[0] * TILE_SIZE + TILE_SIZE // 2, guide_grid_pos[1] * TILE_SIZE + TILE_SIZE // 2]
        guide_index += 1

    screen.fill(BACKGROUND_COLOR)
    draw_maze()
    pygame.draw.circle(screen, PLAYER_COLOR, player_pos, current_player_radius)
    pygame.draw.circle(screen, GUIDE_COLOR, guide_pos, PLAYER_RADIUS)
    if not player_shrunk:
        pygame.draw.circle(screen, ITEM_COLOR, item_pos, PLAYER_RADIUS // 2)

    # Display the dialog box for 2 seconds
    if dialog_displayed:
        draw_dialog_box()
        if pygame.time.get_ticks() - dialog_start_time > 4000:
            dialog_displayed = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()