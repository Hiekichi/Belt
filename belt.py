import pyxel

class BeltScrollAction:
    def __init__(self):
        # ゲーム画面の初期化 (160x120ピクセル)
        pyxel.init(160, 120, title="Belt Scroller")
        
        # ゲーム状態の初期化
        self.init_game()
        
        # ゲームループ開始
        pyxel.run(self.update, self.draw)
    
    def init_game(self):
        # プレイヤー状態
        self.player_x = 40
        self.player_y = 80
        self.player_speed = 2
        self.player_health = 3
        self.player_direction = 1  # 1: 右向き, -1: 左向き
        self.player_is_jumping = False
        self.player_jump_power = 0
        self.player_attacking = 0  # 攻撃モーション用タイマー
        
        # 敵情報
        self.enemies = []
        self.spawn_enemy_timer = 0
        
        # ゲーム情報
        self.score = 0
        self.scroll_x = 0
        self.game_over = False
        
        # 地面のY座標
        self.ground_y = 90
        
        # 背景オブジェクト
        self.bg_objects = [
            {"x": 120, "type": 0},  # 木
            {"x": 200, "type": 1},  # 石
            {"x": 280, "type": 0},  # 木
            {"x": 350, "type": 1},  # 石
        ]
    
    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.init_game()
            return
        
        # プレイヤーの移動
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x = max(20, self.player_x - self.player_speed)
            self.player_direction = -1
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x = min(120, self.player_x + self.player_speed)
            self.player_direction = 1
        
        # ジャンプ処理
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.player_is_jumping:
            self.player_is_jumping = True
            self.player_jump_power = -8
        
        # 攻撃処理
        if pyxel.btnp(pyxel.KEY_Z):
            self.player_attacking = 10  # 10フレーム攻撃モーション
        
        if self.player_attacking > 0:
            self.player_attacking -= 1
        
        # ジャンプ物理演算
        if self.player_is_jumping:
            self.player_y += self.player_jump_power
            self.player_jump_power += 0.5  # 重力
            
            if self.player_y >= self.ground_y:
                self.player_y = self.ground_y
                self.player_is_jumping = False
        
        # 背景スクロール
        self.scroll_x += 1
        
        # 敵の出現タイマー
        self.spawn_enemy_timer += 1
        if self.spawn_enemy_timer > 60:  # 約1秒ごとに敵出現
            self.spawn_enemy_timer = 0
            if len(self.enemies) < 5:  # 最大5体まで
                self.enemies.append({
                    "x": 170,
                    "y": self.ground_y,
                    "speed": pyxel.rndf(0.5, 1.5),
                    "health": 1
                })
        
        # 敵の更新
        for enemy in self.enemies[:]:
            enemy["x"] -= enemy["speed"]
            
            # 画面外に出た敵を削除
            if enemy["x"] < -10:
                self.enemies.remove(enemy)
                continue
            
            # 攻撃判定
            if (self.player_attacking > 0 and 
                abs(self.player_x - enemy["x"]) < 20 and
                abs(self.player_y - enemy["y"]) < 20):
                enemy["health"] -= 1
                if enemy["health"] <= 0:
                    self.enemies.remove(enemy)
                    self.score += 100
            
            # プレイヤーと敵の衝突判定
            elif (abs(self.player_x - enemy["x"]) < 10 and
                  abs(self.player_y - enemy["y"]) < 10 and
                  self.player_attacking == 0):
                self.player_health -= 1
                self.enemies.remove(enemy)
                if self.player_health <= 0:
                    self.game_over = True
    
    def draw(self):
        pyxel.cls(12)  # 空色の背景
        
        # 背景の描画
        pyxel.rect(0, self.ground_y + 10, 160, 30, 11)  # 地面
        
        # 背景オブジェクト描画
        for obj in self.bg_objects:
            x = obj["x"] - self.scroll_x % 400  # 400ピクセル周期で繰り返し
            if x < -20:
                x += 400
            if obj["type"] == 0:  # 木
                pyxel.rect(x, self.ground_y - 20, 5, 20, 3)
                pyxel.circ(x + 2, self.ground_y - 25, 10, 3)
            else:  # 石
                pyxel.rect(x, self.ground_y - 5, 10, 5, 5)
        
        # 敵の描画
        for enemy in self.enemies:
            pyxel.rect(enemy["x"] - 5, enemy["y"] - 10, 10, 10, 8)
        
        # プレイヤーの描画
        player_color = 7 if (pyxel.frame_count % 8 < 4) and self.player_attacking > 0 else 7
        if self.player_direction > 0:
            pyxel.rect(self.player_x - 5, self.player_y - 15, 10, 15, player_color)
            # 腕の描画（攻撃時は伸ばす）
            arm_length = 15 if self.player_attacking > 0 else 5
            pyxel.rect(self.player_x + 5, self.player_y - 10, arm_length, 3, player_color)
        else:
            pyxel.rect(self.player_x - 5, self.player_y - 15, 10, 15, player_color)
            # 腕の描画（攻撃時は伸ばす）
            arm_length = 15 if self.player_attacking > 0 else 5
            pyxel.rect(self.player_x - 5 - arm_length, self.player_y - 10, arm_length, 3, player_color)
        
        # UIの描画
        pyxel.text(5, 5, f"SCORE: {self.score}", 7)
        pyxel.text(5, 15, f"HEALTH: {self.player_health}", 7)
        
        # ゲームオーバー表示
        if self.game_over:
            pyxel.rect(30, 40, 100, 40, 0)
            pyxel.text(50, 55, "GAME OVER", 8)
            pyxel.text(40, 65, "PRESS R TO RESTART", 7)

# ゲーム開始
BeltScrollAction()