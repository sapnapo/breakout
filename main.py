# ========== 第一步：锁定窗口大小（必须在导入 Kivy 其他模块之前） ==========
from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', '0')

# ========== 第二步：导入 Kivy 模块 ==========
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window


class BreakoutGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_started = False

        # 游戏区域固定尺寸
        self.game_w = 400
        self.game_h = 700

        # 球的属性
        self.ball_pos = [self.game_w / 2, self.game_h / 2]
        self.ball_vel = [4, -4]
        self.ball_radius = 10

        # 挡板属性
        self.paddle_pos = [self.game_w / 2 - 50, 50]
        self.paddle_size = [100, 15]

        # 砖块
        self.bricks = []
        self.create_bricks()

        # 时钟，每秒更新 60 次
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.bind(pos=self.redraw, size=self.redraw)

    def create_bricks(self):
        self.bricks = []
        rows = 5
        cols = 8
        brick_width = 40
        brick_height = 20
        padding = 5

        total_width = cols * (brick_width + padding) - padding
        start_x = (self.game_w - total_width) / 2
        start_y = self.game_h - 100

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (brick_width + padding)
                y = start_y - row * (brick_height + padding)
                self.bricks.append({
                    'x': x, 'y': y,
                    'w': brick_width, 'h': brick_height,
                    'alive': True
                })

    def redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            # 背景
            Color(0.1, 0.1, 0.1)
            Rectangle(pos=(0, 0), size=(self.game_w, self.game_h))

            # 球
            Color(1, 1, 1)
            Ellipse(
                pos=(self.ball_pos[0] - self.ball_radius,
                     self.ball_pos[1] - self.ball_radius),
                size=(self.ball_radius * 2, self.ball_radius * 2)
            )

            # 挡板
            Color(0.2, 0.6, 1)
            Rectangle(pos=self.paddle_pos, size=self.paddle_size)

            # 砖块
            for brick in self.bricks:
                if brick['alive']:
                    Color(1, 0.8, 0.2)
                    Rectangle(
                        pos=(brick['x'], brick['y']),
                        size=(brick['w'], brick['h'])
                    )

    def update(self, dt):
        if not self.game_started or self.game_over:
            self.redraw()
            return

        # 球移动
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]

        # 墙壁碰撞
        if self.ball_pos[0] - self.ball_radius <= 0 or \
           self.ball_pos[0] + self.ball_radius >= self.game_w:
            self.ball_vel[0] *= -1
        if self.ball_pos[1] + self.ball_radius >= self.game_h:
            self.ball_vel[1] *= -1

        # 挡板碰撞
        if (self.ball_pos[1] - self.ball_radius <=
                self.paddle_pos[1] + self.paddle_size[1] and
                self.ball_pos[1] - self.ball_radius >= self.paddle_pos[1] and
                self.paddle_pos[0] <= self.ball_pos[0] <=
                self.paddle_pos[0] + self.paddle_size[0]):
            self.ball_vel[1] *= -1
            hit_pos = (self.ball_pos[0] - self.paddle_pos[0]) / self.paddle_size[0]
            self.ball_vel[0] = 8 * (hit_pos - 0.5)

        # 砖块碰撞
        for brick in self.bricks:
            if brick['alive']:
                if (brick['x'] <= self.ball_pos[0] <= brick['x'] + brick['w'] and
                        brick['y'] <= self.ball_pos[1] <= brick['y'] + brick['h']):
                    brick['alive'] = False
                    self.ball_vel[1] *= -1
                    self.score += 10
                    break

        # 球掉落
        if self.ball_pos[1] - self.ball_radius <= 0:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball_pos = [self.game_w / 2, self.game_h / 2]
                self.ball_vel = [4, -4]

        # 胜利判断
        if all(not b['alive'] for b in self.bricks):
            self.game_over = True

        self.redraw()

    # ===== 注意：下面这两个函数的缩进是 4 个空格，和 update 同级 =====
    def on_touch_down(self, touch):
        if not self.game_started:
            self.game_started = True
        return True

    def on_touch_move(self, touch):
        self.paddle_pos[0] = max(
            0,
            min(self.game_w - self.paddle_size[0],
                touch.x - self.paddle_size[0] / 2)
        )


class BreakoutApp(App):
    def build(self):
        self.title = "弹球打砖块 - 由 刘镇恺 + AI 制作"
        return BreakoutGame()


if __name__ == '__main__':
    BreakoutApp().run()