import pygame
import os
import sqlite3

LEFT = 30
TOP = 140


class Sql:
    def __init__(self):
        self.con = sqlite3.connect("databese.sqlite")
        self.cur = self.con.cursor()

    def add_lev(self, n: int):
        try:
            self.cur.execute(f"INSERT INTO main (lev) VALUES ({n})")
            self.con.commit()
            return True
        except Exception:
            return False

    def get_levs(self):
        return [el[0] for el in self.cur.execute("SELECT * FROM main").fetchall()]


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as f:
        lev_map_ = [line.strip() for line in f]
    max_width = max(map(len, lev_map_))
    return list(map(lambda x: list(x.ljust(max_width, '.')), lev_map_))


def load_image(name):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    return image


def draw_buttons(mas, screen):
    for i in range(len(mas)):
        mas[i].draw(screen)


class MySpritesGroup(pygame.sprite.Group):
    def update_sprites(self, state):
        for el in self:
            el.update(state)

    def resize(self, cs):
        for el in self:
            el.resize(cs)


tile_images = {
    'box': load_image('box.png'),
    'empty': load_image('empty.png'),
    'heart': load_image('heart.png')
}


class Sprite(pygame.sprite.Sprite):
    def __init__(self, cs=0, *group):
        super().__init__(*group)
        self.rect = None
        self.cs = cs

    def get_event(self, event):
        pass

    def resize(self, cs):
        self.cs = cs
        self.rect.update(LEFT, TOP, cs, cs)


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y, spr_gr, cs):
        super().__init__(cs, spr_gr)
        self.image = tile_images[tile_type]
        self.image = pygame.transform.scale(self.image, (cs, cs))
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update(self, *args, **kwargs):
        pass


class Player(Sprite):
    def __init__(self, x, y, spr_gr, cs, v=0):
        super().__init__(cs, spr_gr)
        self.images = [load_image(f'{i}.png') for i in range(1, 6)]
        self.k = 0  # индекс изображение спрайта
        self.cnt = 17  # счетчик количества обновлений для анимаций
        self.v = v  # куда направлен герой? 0 - вдево ; 1 - впарво
        self.state = 'main'
        self.image = pygame.transform.scale(self.images[self.k], (cs, cs))
        if v:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect().move(x, y)
        self.x = x
        self.y = y

    def move(self, x, y):
        self.x, self.y = x, y
        self.rect = self.image.get_rect().move(self.x, self.y)

    def update(self, *args, **kwargs):
        self.image = pygame.transform.scale(self.images[self.k], (self.cs, self.cs))
        if self.v:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.state == 'main':

            self.cnt += 1
            if self.cnt >= 18:
                self.cnt = 0
                if self.k != 0:
                    self.k = 0
                else:
                    self.k = 1

                self.rect = self.image.get_rect()
                self.rect.x = self.x
                self.rect.y = self.y
            return
        if self.state == "attack":
            self.cnt += 1
            if self.cnt >= 20:
                self.state = "main"
                return
            self.k = 3


class Prizrak(Sprite):
    def __init__(self, x, y, spr_gr, cs, v=0, cnt_mx=20):
        super().__init__(cs, spr_gr)
        self.orig_im = load_image(f'prizrak.png')
        self.v = v  # куда направлен герой? 0 - вдево ; 1 - впарво
        self.cnt = 15  # счетчик количества обновлений для анимаций
        self.xp = 2  # для анимации
        self.yp = 1  # для анимации
        self.k = 1  # для анимации
        self.cmt_mx = cnt_mx
        self.image = pygame.transform.scale(self.orig_im, (cs, cs))
        if v:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect().move(x, y)
        self.x = x
        self.y = y

    def update(self, *args, **kwargs):
        self.cnt += 1
        if self.cnt == self.cmt_mx:
            self.cnt = 0
            self.k += 1
            self.x = self.rect.x = self.x + self.xp
            self.y = self.rect.y = self.y + self.yp
            self.xp *= -1
            self.yp *= -1


class Button:
    def __init__(self, name: str, x, y, w, h,
                 color_rect='#ff0000', text="",
                 color_txt='#00ff00', sh=0):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
        self.pos = self.x, self.y
        self.name = name
        self.color_rect = color_rect
        self.color_txt = color_txt
        self.size = self.w, self.h = w, h
        self.text = text
        self.sh = sh

    def update(self, old_w, old_h, new_w, new_h):
        self.pos = self.x, self.y = int(new_w * self.x / old_w), int(new_h * self.y / old_h)
        self.size = self.w, self.h = int(new_w * self.w / old_w), int(new_h * self.h / old_h)
        self.sh = int(self.sh * new_w * new_h / old_h / old_w)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color_rect, (self.x, self.y, self.w, self.h), 2)
        if self.sh:
            font = pygame.font.Font(None, self.sh)
            text = font.render(self.text, True, self.color_txt)
            text_w = text.get_width()
            text_h = text.get_height()
            screen.blit(text, (self.x + abs(self.w - text_w) // 2, self.y + abs(self.h - text_h) // 2))

    def check_click(self, x, y):
        return (self.x <= x <= self.x + self.w) and (self.y <= y <= self.y + self.h)

    def change_text(self, text, color_txt, sh):
        self.text, self.color_txt, self.sh = text, color_txt, sh


def is_go(lvl_mp: list, x, y):
    if 0 <= x < len(lvl_mp) and 0 <= y < len(lvl_mp[x]):
        if lvl_mp[x][y] == '.':
            return True
    return False


def get_coord(x, y, cs):
    return (y - TOP) // cs, (x - LEFT) // cs


class Health:
    def __init__(self, n=3, mx=5):
        self.spr_gr = MySpritesGroup()
        self.hp = n  # кол-во жизней
        self.max_hp = mx
        self.sprites = []
        for i in range(n):
            self.sprites.append(Tile('heart', i * 70 + 20, 10, self.spr_gr, 75))

    def plus(self):
        self.hp = min(self.max_hp, self.hp + 1)
        self.sprites.append(Tile('heart', self.hp * 70 - 25, 10, self.spr_gr, 75))

    def minus(self):
        self.hp -= 1
        if self.hp <= 0:
            return False
        self.sprites.pop().kill()
        return True

    def update(self, screen):
        self.spr_gr.draw(screen)

    def delete(self):
        self.hp = 0
        while len(self.sprites):
            self.sprites.pop().kill()


if __name__ == '__main__':
    print(load_level("map1.map"))
