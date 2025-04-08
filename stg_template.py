#STGのひな型

import pyxel

class Player: #自機クラス
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.speed = 1.3
        self.is_living = True
        self.shot_timer = 0

        self.game.player = self

    def update(self):
        if not self.is_living:
            self.game.game_over = True
            return
        
        #自機移動
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += self.speed
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= self.speed
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= self.speed
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += self.speed
        
        self.x = min(max(self.x, -2), pyxel.width - 6)
        self.y = min(max(self.y, -2), pyxel.height - 6)

        #ショット発射
        if pyxel.btn(pyxel.KEY_Z) and self.shot_timer == 0:
            self.game.shots.append(Shot(self.x + 3, self.y))
            self.shot_timer = 3
        
        if self.shot_timer > 0:
            self.shot_timer -= 1
        

    def draw(self):
        if not self.is_living:
            return
        pyxel.rect(self.x, self.y, 8, 8, 8) 
        pyxel.rect(self.x + 3, self.y + 3, 2, 2, 7)   

class Enemy: #敵クラス
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.dx = 0 #敵の向き　0右　1左
        self.speed = 0.5
        self.life_time = 0
        self.hp = 1000
        self.hakkyou = 1
        self.phase = 0 #今のフェイズ
        self.cool_timer = 0

        self.is_muteki = False

        self.option1_x = self.x - 20
        self.option2_x = self.x + 20 + 2

        self.game.enemy = self

#敵クールタイムの時に一定時間敵無敵タイムを用意する
#cool 1形態 cool 2形態 cool 3形態 
    def get_next_phase(self):
            if self.hp >= 700:
                return 1
            elif self.hp >= 400:
                return 2
            elif self.hp > 0:
                return 3
            return 0




    def update(self):
        self.life_time += 1
        prev_phase = self.get_next_phase()
        
        # クールタイム中はカウントダウンし、無敵状態維持
        if self.cool_timer > 0:
            self.cool_timer -= 1
            self.is_muteki = True
            return  # フェーズ更新などはスキップ

        self.is_muteki = False
        next_phase = self.get_next_phase()

        # フェーズが変わったらクールタイム突入
        if next_phase != self.phase:
            self.phase = next_phase
            self.cool_timer = 120 
            self.is_muteki = True

        if prev_phase == 0:
            self.is_muteki = True
        else:
            self.is_muteki = False

        # 弾発射
        if prev_phase == 1:  # 第一形態
            if self.life_time % 5 == 0:
                for i in range(10):
                    self.game.bullets.append(Bullet(self.x + 4, self.y + 8, self.life_time * 5 + i * 36, 2, 7))
            if self.life_time % 2 == 0:
                angle = (self.life_time * 8) % 360
                self.game.bullets.append(Bullet(self.x + 4, self.y + 8, angle, 1.5, 8 + self.life_time % 5))
                self.game.bullets.append(Bullet(self.x + 4, self.y + 8, -angle, 1.5, 8 + self.life_time % 5))

        elif prev_phase == 2:  # 第二形態
            if self.life_time % 20 != 0:
                for i in range(4):
                    self.game.bullets.append(Bullet(self.x + 4, self.y + 8, 45 + i * 90, 2, 10))

            if self.life_time % 30 == 0:
                for angle in [90, 110, 70]:
                    self.game.bullets.append(Bullet(self.x + 4, self.y + 8, angle, 1.5, 7))
                    self.game.bullets.append(Bullet(self.option1_x, self.y + 10, angle, 1.5, 7))
                    self.game.bullets.append(Bullet(self.option2_x, self.y + 10, angle, 1.5, 7))

            if self.life_time % 60 == 0:
                for i in range(10):
                    self.game.bullets.append(Bullet(self.x + 4, self.y + 8, i * 36, 3, 6))

        elif prev_phase == 3:  # 第三形態
            if self.life_time % 5 == 0:
                self.game.bullets.append(Bullet(self.x + 4, self.y + 8, pyxel.rndi(0, 360), 2, 7))
            if self.life_time % 5 == 0:
                self.hakkyou += 1
                for i in range(self.hakkyou):
                    self.game.bullets.append(Bullet(self.x + 4, self.y + 8, 360 / self.hakkyou * i, 1.5, 7))

        else:
            pass


        #敵の移動
        if prev_phase == 1: #第一形態
            if self.dx == 0: #右へ動く
                self.x += self.speed
                if self.x > 70 - 8:
                    self.dx = 1
            elif self.dx == 1: #左へ動く
                self.x -= self.speed
                if self.x < 10:
                    self.dx = 0

        elif prev_phase == 2: #第二形態
            self.x = 40 - 4 + pyxel.sin(self.life_time * 5) * 10
            self.y = 30 + pyxel.sin(self.life_time * 10) * 20

        elif prev_phase == 3: #第三形態
            self.x = 40 - 4
            self.y = 30

        else:
            pass

        if self.hp < 0:
            self.phase = 0



    def draw(self):
        pyxel.rect(self.x, self.y, 8, 8, 11)    

        if self.get_next_phase() == 2: #第二形態
            #オプション描画
            pyxel.rect(self.option1_x, self.y + 10, 4, 4, 11)
            pyxel.rect(self.option2_x, self.y + 10, 4, 4, 11)

        if self.hp < 0:
            pyxel.text(20, 30, "GAME CLEAR!!", pyxel.frame_count%16)


class Bullet: #敵弾クラス
    def __init__(self, x, y, angle, speed, color):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.color = color
        self.dx = self.speed * pyxel.cos(self.angle)
        self.dy = self.speed * pyxel.sin(self.angle)


    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        pyxel.rect(self.x, self.y, 4, 4, self.color)    

class Shot: #ショットクラス
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        self.y -= 5

    def draw(self):
        pyxel.rect(self.x, self.y, 2, 8, 10)    

def collision(game):
    # プレイヤーと敵弾の当たり判定
    if not game.player.is_living:
        return

    player_hitbox_x = game.player.x + 3
    player_hitbox_y = game.player.y + 3
    player_hitbox_size = 2


    for bullet in game.bullets:
        # 弾とプレイヤーの当たり判定（
        if (player_hitbox_x < bullet.x + 4 and
            player_hitbox_x + player_hitbox_size > bullet.x and
            player_hitbox_y < bullet.y + 4 and
            player_hitbox_y + player_hitbox_size > bullet.y):
            game.player.is_living = False
            break

    # プレイヤーのショットと敵の当たり判定
    if not game.enemy.is_muteki: #敵が無敵でないとき、ショットのあたり判定
        for shot in game.shots[:]:
            if abs(shot.x - game.enemy.x) < 8 and abs(shot.y - game.enemy.y) < 8:
                game.enemy.hp -= 8
                game.shots.remove(shot)

class Game:
    def __init__(self):
        pyxel.init(80, 120, "stg template")
        self.retry()

        #各インスタンスを生成
        self.player = Player(self, pyxel.width / 2 - 4, 100 - 4)
        self.enemy = Enemy(self, pyxel.width / 2 - 4, 20 - 4)
        self.shots = []
        self.bullets = []

        pyxel.run(self.update, self.draw) #実行！

    def retry(self):
        self.player = Player(self, pyxel.width / 2 - 4, 100 - 4)
        self.enemy = Enemy(self, pyxel.width / 2 - 4, 20 - 4)
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.frame_count = 0
        self.game_over = False
        self.retry_flag = False


    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_SPACE):  #スペースキーでリトライ
                self.retry()

        self.player.update()
        self.enemy.update()
        collision(self)

        for shot in self.shots:
            shot.update()
        self.shots = [shot for shot in self.shots if shot.y > -8] # 画面外のショットを削除

        for bullet in self.bullets:
            bullet.update()
        self.bullets = [
            bullet for bullet in self.bullets 
            if -10 < bullet.x < pyxel.width + 10 and -10 < bullet.y < pyxel.height + 10
            ]


    def draw(self):
        pyxel.cls(0)
        self.player.draw()
        self.enemy.draw()
        
        for shot in self.shots:
            shot.draw()
        for bullet in self.bullets:
            bullet.draw()

        #HP表示
        pyxel.rect(0, 5, self.enemy.hp * 80 / 1000, 2, 7)

        if self.enemy.hp < 0:
            pyxel.text(20, 30, "GAME CLEAR!!", pyxel.frame_count%16)

        if self.game_over:
            pyxel.text(25, 60, "GAME OVER", pyxel.COLOR_RED)
            pyxel.text(1, 80, "PRESS SPACE TO RETRY", pyxel.COLOR_WHITE) 

Game()