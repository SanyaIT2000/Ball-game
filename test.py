import datetime
import pyray
from raylib import colors


class Image():
    def __init__(self, x, y, filename) -> None:
         self.filename = filename
         self.image = pyray.load_image(filename)
         self.texture = pyray.load_texture(self.image)
         self.x = x
         self.y = y
         self.rect = pyray.Rectangle(x,y,self.texture.width,self.texture.height)
    def __del__(self):
        pyray.unload_image(self.image)
    def draw(self):
        pyray.draw_texture(self.texture,self.rect.x,self.rect.y,colors.BLACK)


class Ball(Image):
    def __init__(self, x, y, filename) -> None:
        super().__init__(x, y, filename)
        self.shift = [0, 0]
        self.radius = self.texture.width / 2
        self.initial = dict()
        self.initial["x"] = self.rect.x
        self.initial["y"] = self.rect.y
    def activate(self):
        self.rect.x = self.initial["x"]
        self.rect.y = self.initial["y"]
    def step(self):
        self.rect.x += self.shift[0]
        self.rect.y += self.shift[1]
    def collides_with_horizontal_border(self, window_height):
        return self.texture.y == window_height
    def collides_with_vertical_border(self, window_width):
        return self.texture.x == window_width
    def bounce_x(self):
        self.shift[0] *= -1
    def bounce_y(self):
        self.shift[1] *= -1
    def collides_with(self, other_ball):
        return pyray.check_collision_circles(pyray.Vector2(self.texture.x,self.texture.y),self.radius,pyray.Vector2(other_ball.texture.x,other_ball.texture.y),other_ball.radius)
    def collide(self, other_ball):
        self.shift[0],self.shift[1],other_ball.shift[0],other_ball.shift[1] = other_ball.shift[0],other_ball.shift[1],self.shift[0],self.shift[1]
    def logic(self, window_width, window_height):
        self.step()
        if self.collides_with_horizontal_border(window_height):
            self.bounce_y()
        if self.collides_with_vertical_border(window_width):
            self.bounce_x()

def menu_scene_on_activate(motion_start,motion_now,percent_completed):
    return motion_start,motion_now,percent_completed


def game_scene_on_activate(ball_0, ball_1_position, ball_1_shift, ball_2_position, ball_2_shift, collision_count):
    ball_0.activate()
    return ball_1_position, ball_1_shift, ball_2_position, ball_2_shift, collision_count


def game_over_scene_on_activate(open_scene_datetime):
    open_scene_datetime = datetime.datetime.now()
    return open_scene_datetime


def menu_scene_process_event(scene_0_button_new_geometry, scene_0_button_exit_geometry, scene_changed, scene_index):
    if pyray.gui_button(scene_0_button_new_geometry, 'New game'):
                    scene_changed = True
                    scene_index = 1
    if pyray.gui_button(scene_0_button_exit_geometry, 'Exit'):
        pyray.close_window()
        exit(0)
    return scene_changed, scene_index


def game_scene_process_event(scene_changed,scene_index):
    if pyray.is_key_down(pyray.KeyboardKey.KEY_ESCAPE):
                    scene_changed = True
                    scene_index = 0
    return scene_changed,scene_index


def game_over_scene_process_event(scene_changed,scene_index):
    if pyray.is_key_down(pyray.KeyboardKey.KEY_ESCAPE):
                    scene_changed = True
                    scene_index = 0
    return scene_changed,scene_index


def menu_scene_process_logic(motion_start, motion_seconds):
    motion_now = datetime.datetime.now()
    delta = (motion_now - motion_start)
    ms = delta.seconds * 1000000 + delta.microseconds
    percent_completed = min(1.0, ms / (motion_seconds * 1000000))
    return motion_now, percent_completed


def game_scene_process_logic(ball_0: Ball, ball_1_position, ball_1_shift, ball_2_position, ball_2_shift, window_width, window_height, collision_count, max_collision_count, scene_changed, scene_index):
    # Движение мячиков
    ball_0.rect.x += ball_0.shift[0]
    ball_0.rect.y += ball_0.shift[1]
    ball_1_position.x += ball_1_shift[0]
    ball_1_position.y += ball_1_shift[1]
    ball_2_position.x += ball_2_shift[0]
    ball_2_position.y += ball_2_shift[1]

    # Отражение от стенок
    if ball_0.rect.x < 0 or ball_0.rect.x + ball_0.texture.width > window_width:
        ball_0.shift[0] *= -1
    if ball_0.rect.y < 0 or ball_0.rect.y + ball_0.texture.height > window_height:
        ball_0.shift[1] *= -1
    if ball_1_position.x < 0 or ball_1_position.x + ball_0.texture.width > window_width:
        ball_1_shift[0] *= -1
    if ball_1_position.y < 0 or ball_1_position.y + ball_0.texture.height > window_height:
        ball_1_shift[1] *= -1
    if ball_2_position.x < 0 or ball_2_position.x + ball_0.texture.width > window_width:
        ball_2_shift[0] *= -1
    if ball_2_position.y < 0 or ball_2_position.y + ball_0.texture.height > window_height:
        ball_2_shift[1] *= -1

    # Обработка коллизий
    ball_0.center = pyray.Vector2(ball_0.rect.x + ball_0.texture.width / 2,
                                ball_0.rect.y + ball_0.texture.height / 2)
    ball_0.radius = ball_0.texture.width / 2
    ball_1_center = pyray.Vector2(ball_1_position.x + ball_0.texture.width / 2,
                                ball_1_position.y + ball_0.texture.height / 2)
    ball_1_radius = ball_0.texture.width / 2
    ball_2_center = pyray.Vector2(ball_2_position.x + ball_0.texture.width / 2,
                                ball_2_position.y + ball_0.texture.height / 2)
    ball_2_radius = ball_0.texture.width / 2
    if pyray.check_collision_circles(ball_0.center, ball_0.radius, ball_1_center, ball_1_radius):
        ball_0.shift, ball_1_shift = ball_1_shift, ball_0.shift
        collision_count += 1
    if pyray.check_collision_circles(ball_0.center, ball_0.radius, ball_2_center, ball_2_radius):
        ball_0.shift, ball_2_shift = ball_2_shift, ball_0.shift
        collision_count += 1
    if pyray.check_collision_circles(ball_1_center, ball_1_radius, ball_2_center, ball_2_radius):
        ball_1_shift, ball_2_shift = ball_2_shift, ball_1_shift
        collision_count += 1

    # Переключение сцен при достижении нужного количества коллизий
    if collision_count == max_collision_count:
        scene_changed = True
        scene_index = 2
    return collision_count, scene_changed, scene_index, ball_1_shift, ball_2_shift


def game_over_scene_process_logic(open_scene_datetime, max_wait_seconds, scene_changed, scene_index):
    now = datetime.datetime.now()
    wait_seconds = (now - open_scene_datetime).seconds

    # Переключение сцен при достижении нужного количества секунд (микросекунд)
    if wait_seconds == max_wait_seconds:
        scene_changed = True
        scene_index = 0
    return wait_seconds, scene_changed, scene_index


def menu_scene_process_draw(line_color, percent_completed):
    # четыре анимированные линии (две кнопки уже отрисовались)
    pyray.draw_line_ex(pyray.Vector2(100, 100), pyray.Vector2(100 + 600 * percent_completed, 100),
                    4, line_color)
    pyray.draw_line_ex(pyray.Vector2(700, 100), pyray.Vector2(700, 100 + 400 * percent_completed, ),
                    4, line_color)
    pyray.draw_line_ex(pyray.Vector2(700, 500), pyray.Vector2(700 - 600 * percent_completed, 500),
                    4, line_color)
    pyray.draw_line_ex(pyray.Vector2(100, 500), pyray.Vector2(100, 500 - 400 * percent_completed),
                    4, line_color)


def game_scene_process_draw(ball_0, ball_1_position, ball_2_position, collision_text_format, collision_count):
    pyray.draw_texture_v(ball_0.texture, pyray.Vector2(ball_0.x,ball_0.y), colors.WHITE)
    pyray.draw_texture_v(ball_0.texture, ball_1_position, colors.WHITE)
    pyray.draw_texture_v(ball_0.texture, ball_2_position, colors.WHITE)
    pyray.draw_text(collision_text_format.format(collision_count), 10, 10, 78, colors.WHITE)


def game_over_scene_process_draw(gameover_text_format, wait_seconds):
    pyray.draw_text(gameover_text_format.format(wait_seconds), 100, 250, 78, colors.RED)
    

def main():
    # Инициализация окна
    window_width = 800
    window_height = 600
    pyray.init_window(window_width, window_height, 'Hello, raylib')
    pyray.set_exit_key(pyray.KeyboardKey.KEY_F8)
    pyray.set_target_fps(120)

    # Инициализация глобальных переменных
    scene_index = 0
    scene_changed = True
    background_color = colors.BLACK

    # Инициализация сцены 0 (menu)
    scene_0_button_new_geometry = pyray.Rectangle(window_width / 2 - 100 / 2, window_height / 2 - 10 - 50, 100, 50)
    scene_0_button_exit_geometry = pyray.Rectangle(window_width / 2 - 100 / 2, window_height / 2 + 10, 100, 50)

    motion_seconds = 3
    motion_start = datetime.datetime.now()
    motion_now = datetime.datetime.now()
    percent_completed = 0
    line_color = colors.WHITE
    # Инициализация сцены 1 (game)

    max_collision_count = 5

    collision_text_format = 'Collisions: {}/' + str(max_collision_count)

    ball_0 = Ball(10,10,'basketball.png')
    ball_0.shift = [1, 1]
    ball_1_position = pyray.Vector2(500, 100)
    ball_1_shift = [-1, 1]
    ball_2_position = pyray.Vector2(400, 500)
    ball_2_shift = [-1, -1]
    collision_count = 0    

    # Инициализация сцены 2 (gameover)
    max_wait_seconds = 3
    wait_seconds = 0
    gameover_text_format = 'Game over ({}/{})'.format('{}', max_wait_seconds)
    open_scene_datetime = datetime.datetime.now()
    # Основной цикл программы
    while not pyray.window_should_close():

        # Действия, выполняемые при первом появлении сцены на экране
        if scene_changed:
            scene_changed = False
            if scene_index == 0:  # menu
                motion_start,motion_now,percent_completed = menu_scene_on_activate(motion_start,motion_now,percent_completed)
            elif scene_index == 1:  # game
                ball_1_position, ball_1_shift, ball_2_position, ball_2_shift, collision_count = game_scene_on_activate(ball_0, ball_1_position, ball_1_shift, ball_2_position, ball_2_shift, collision_count)
            elif scene_index == 2:  # gameover
                open_scene_datetime = game_over_scene_on_activate(open_scene_datetime)

        # Обработка событий различных сцен (при каждом кадре)
        if not scene_changed:
            if scene_index == 0:  # menu
                scene_changed,scene_index = menu_scene_process_event(scene_0_button_new_geometry, scene_0_button_exit_geometry, scene_changed, scene_index)
            elif scene_index == 1:  # game
                scene_changed,scene_index = game_scene_process_event(scene_changed,scene_index)
            elif scene_index == 2:  # gameover
                scene_changed,scene_index = game_over_scene_process_event(scene_changed,scene_index)

        # Обработка логики работы сцен (при каждом кадре)
        if not scene_changed:
            if scene_index == 0:  # menu
                motion_now,percent_completed = menu_scene_process_logic(motion_start, motion_seconds)
            elif scene_index == 1:  # game
                collision_count, scene_changed, scene_index, ball_1_shift, ball_2_shift = game_scene_process_logic(ball_0, ball_1_position, ball_1_shift, ball_2_position, ball_2_shift, window_width, window_height, collision_count, max_collision_count, scene_changed, scene_index)

            elif scene_index == 2:  # gameover
                wait_seconds, scene_changed, scene_index = game_over_scene_process_logic(open_scene_datetime, max_wait_seconds, scene_changed, scene_index)

        # Обработка отрисовки различных сцен (при каждом кадре)
        if not scene_changed:
            pyray.begin_drawing()
            pyray.clear_background(background_color)

            if scene_index == 0:  # menu
                menu_scene_process_draw(line_color,percent_completed)
            elif scene_index == 1:  # game
                game_scene_process_draw(ball_0, ball_1_position, ball_2_position, collision_text_format, collision_count)
            elif scene_index == 2:  # gameover
                game_over_scene_process_draw(gameover_text_format, wait_seconds)

            pyray.end_drawing()

    pyray.unload_texture(ball_0.texture)
    pyray.close_window()
    exit(0)


if __name__ == '__main__':
    main()
