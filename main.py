import pygame
import os
from addution import *  # файл со спрайтами кнопками и прочем
import random
from queue import Queue

# минимальные размеры окна
MINWIDTH = 800
MINHEIGHT = 450


def moving_enemies(x, y):
    global health
    global state
    levmp_cop = []
    for i in range(len(level_map)):
        levmp_cop.append(level_map[i].copy())
    for i in range(len(level_map)):
        for j in range(len(level_map[i])):
            if levmp_cop[i][j] == 'p':
                levmp_cop[i][j] = '.'
                tx, ty = bfs((i, j), (x, y))
                if tx != -1 and ty != -1:
                    level_map[tx][ty] = 'p'
                    level_map[i][j] = '.'
                if tx == x and ty == y:
                    level_map[tx][ty] = '@'
                    if not health.minus():
                        return "died"


def bfs(start: tuple, finish: tuple):
    dist = [[10000 for j in range(w_l)] for i in range(h_l)]
    dist[finish[0]][finish[1]] = 0
    q = Queue()
    q.put(finish)
    cnt = 0
    while q.qsize():
        cnt += 1
        v = q.get()
        if v[0] + 1 < h_l and dist[v[0] + 1][v[1]] == 10000 and level_map[v[0] + 1][v[1]] == '.':
            q.put((v[0] + 1, v[1]))
            dist[v[0] + 1][v[1]] = dist[v[0]][v[1]] + 1

        if v[0] - 1 >= 0 and dist[v[0] - 1][v[1]] == 10000 and level_map[v[0] - 1][v[1]] == '.':
            q.put((v[0] - 1, v[1]))
            dist[v[0] - 1][v[1]] = dist[v[0]][v[1]] + 1

        if v[1] + 1 < w_l and dist[v[0]][v[1] + 1] == 10000 and level_map[v[0]][v[1] + 1] == '.':
            q.put((v[0], v[1] + 1))
            dist[v[0]][v[1] + 1] = dist[v[0]][v[1]] + 1

        if v[1] - 1 > 0 and dist[v[0]][v[1] - 1] == 10000 and level_map[v[0]][v[1] - 1] == '.':
            q.put((v[0], v[1] - 1))
            dist[v[0]][v[1] - 1] = dist[v[0]][v[1]] + 1

        if dist[start[0]][start[1]] != 10000:
            break
    res = (-1, -1)
    if start[0] - 1 >= 0:
        res = (start[0] - 1, start[1])
    elif start[1] - 1 >= 0:
        res = (start[0], start[1] - 1)
    elif start[0] + 1 < h_l:
        res = (start[0] + 1, start[1])
    else:
        res = (start[0], start[1] + 1)

    if start[0] - 1 >= 0 and dist[start[0] - 1][start[1]] < dist[res[0]][res[1]]:
        res = (start[0] - 1, start[1])
    if start[1] - 1 >= 0 and dist[start[0]][start[1] - 1] < dist[res[0]][res[1]]:
        res = (start[0], start[1] - 1)
    if start[0] + 1 < h_l and dist[start[0] + 1][start[1]] < dist[res[0]][res[1]]:
        res = (start[0] + 1, start[1])
    if start[1] + 1 < w_l and dist[start[0]][start[1] + 1] < dist[res[0]][res[1]]:
        res = (start[0], start[1] + 1)

    return res


def gen_lev(v=0):
    global all_sprites
    global cell_size
    global h_l, w_l
    h_l, w_l = len(level_map), len(level_map[0])
    cell_size = int(min((width - LEFT - 20) / w_l, (height - TOP - 20) / h_l))

    all_sprites = MySpritesGroup()
    new_player, x, y = -1, -1, -1
    for k in range(len(level_map)):
        for j in range(len(level_map[k])):
            if level_map[k][j] == '#':
                Tile('box', LEFT + j * cell_size, TOP + k * cell_size, all_sprites, cell_size)
            elif level_map[k][j] == '@':
                new_player = Player(LEFT + j * cell_size, TOP + k * cell_size, all_sprites, cell_size, v)
                x, y = k, j
            elif level_map[k][j] == 'p':
                Prizrak(LEFT + j * cell_size, TOP + k * cell_size, all_sprites, cell_size, v=0,
                        cnt_mx=random.randint(20, 30))
    return new_player, x, y


if __name__ == '__main__':
    state = "start_window"  # переменная в которой хранится состояние (FSM на минималках)
    pygame.init()
    size = width, height = 1280, 720
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    running = True
    clock = pygame.time.Clock()
    all_sprites = MySpritesGroup()
    # pl = Player(20, 50, all_sprites, 75)
    # Tile('box', 100, 400, all_sprites, 50)

    cnt_an = 30  # счетчик задержки для анимаций

    v_ = 0
    level = -1
    level_map = [['.']]
    x_pos = y_pos = -1
    size_lev = w_lev, h_lev = -1, -1
    cell_size = 60
    buttons = list()  # список всех кнопок
    buttons.append(Button("play", width * 0.4, height * 0.4, 150, 60, text="Play", sh=50))
    orig_fon = load_image('fon.jpg')
    game_over_image = load_image('game_over.jpg')
    fon = pygame.transform.scale(orig_fon, (width, height))  # задний фон игры
    while running:
        cnt_an = min(30, cnt_an + 1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if cnt_an < 30:
                continue
            if state == "start_window":
                if event.type == pygame.VIDEORESIZE:  # изменение размеров окна и размеров всех объектов
                    old_size = size
                    width, height = pygame.display.get_surface().get_size()
                    width = max(width, MINWIDTH)
                    height = max(height, MINHEIGHT)
                    size = width, height
                    for el in buttons:
                        el.update(*old_size, *size)
                    fon = pygame.transform.scale(orig_fon, (width, height))
                    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range(len(buttons)):
                        if buttons[i].check_click(*event.pos):
                            if buttons[i].name == "play":
                                state = "select_level"
                                buttons = []
                                all_sprites = MySpritesGroup()
                                cnt = 0
                                for row in range(2):
                                    for col in range(10):
                                        cnt += 1
                                        buttons.append(Button(f'level:{cnt}',
                                                              col * 100 + 40, (row + 1) * 100,
                                                              90, 90,
                                                              '#ffffff', f"{cnt}",
                                                              "#ffffff", 30))

                            break

            if state == "select_level":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range(len(buttons)):
                        if buttons[i].check_click(*event.pos):
                            but = buttons[i].name.split(':')
                            if but[0] == "level":
                                level = int(but[1])
                                try:
                                    level_map = load_level(f"map{level}.map")
                                    buttons = []

                                    h_l, w_l = len(level_map), len(level_map[0])
                                    player, x_pos, y_pos = gen_lev()
                                    health = Health(3)
                                    state = "level_go"
                                except Exception as ex:
                                    print("file not find or error:\n", ex)

                            break

            if state == "level_go":
                if event.type == pygame.KEYDOWN:

                    level_map[x_pos][y_pos] = '.'
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if is_go(level_map, x_pos - 1, y_pos):
                            x_pos -= 1
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if is_go(level_map, x_pos + 1, y_pos):
                            x_pos += 1
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        v_ = 0
                        if is_go(level_map, x_pos, y_pos - 1):
                            y_pos -= 1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        v_ = 1
                        if is_go(level_map, x_pos, y_pos + 1):
                            y_pos += 1
                    level_map[x_pos][y_pos] = '@'
                    if moving_enemies(x_pos, y_pos) == "died":
                        health.delete()
                        for el in all_sprites:
                            el.kill()
                        all_sprites = MySpritesGroup()
                        state = "died"

                    player, x_pos, y_pos = gen_lev(v_)

                if event.type == pygame.VIDEORESIZE:  # изменение размеров окна и размеров всех объектов
                    old_size = size
                    width, height = pygame.display.get_surface().get_size()
                    width = max(width, MINWIDTH)
                    height = max(height, MINHEIGHT)
                    size = width, height
                    player, x_pos, y_pos = gen_lev(v_)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    xc, yc = get_coord(*event.pos, cell_size)
                    if 0 <= xc < h_l and 0 <= yc < w_l:
                        if (abs(x_pos - xc) == 1 and abs(y_pos - yc) == 0) or (
                                abs(x_pos - xc) == 0 and abs(y_pos - yc) == 1):
                            if y_pos < yc:
                                v_ = 1
                            elif y_pos > yc:
                                v_ = 0
                            level_map[xc][yc] = '.'
                            player, x_pos, y_pos = gen_lev(v_)
                            player.cnt = 0
                            player.state = "attack"
                            cnt_an = 0
                            if moving_enemies(x_pos, y_pos) == "died":
                                health.delete()
                                for el in all_sprites:
                                    el.kill()
                                all_sprites = MySpritesGroup()
                                state = "died"

                            player, x_pos, y_pos = gen_lev(v_)

            if state == "died":
                if event.type == pygame.VIDEORESIZE:  # изменение размеров окна и размеров всех объектов
                    old_size = size
                    width, height = pygame.display.get_surface().get_size()
                    width = max(width, MINWIDTH)
                    height = max(height, MINHEIGHT)
                    size = width, height

        clock.tick(50)
        screen.fill('#000000')
        if state == "start_window":
            screen.blit(fon, (0, 0))

        draw_buttons(buttons, screen)  # отрисовка всех кнопок
        all_sprites.draw(screen)
        all_sprites.update(state)
        if state == "level_go":
            health.update(screen)
            for k in range(len(level_map)):
                for j in range(len(level_map[k])):
                    if level_map[k][j] != '#':
                        pygame.draw.rect(screen, 'white',
                                         (LEFT + j * cell_size, TOP + k * cell_size, cell_size, cell_size), 1)
        if state == "died":

        pygame.display.flip()
