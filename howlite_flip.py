#!/usr/bin/env python3
"""Howlite Flip — neon vertical pinball arcade for ElbowOS."""
from __future__ import annotations

import math
import os
import random
import subprocess
import sys

import pygame

W, H = 1080, 1920
FPS = 30
TITLE = "HOWLITE FLIP"
HANDLE = "x.com/ElbowOS"
BG = (8, 6, 22)
INK = (244, 240, 232)
INDIGO = (28, 22, 78)
VEIN = (196, 212, 232)
GOLD = (255, 196, 64)
CORAL = (255, 78, 118)
CYAN = (88, 230, 255)
LILAC = (186, 140, 255)
PLAY_L, PLAY_R = 70, 1010
PLAY_T, PLAY_B = 210, 1760


class Spark:
    __slots__ = ("x", "y", "vx", "vy", "life", "col", "r")

    def __init__(self, x, y, vx, vy, life, col, r=5):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life, self.col, self.r = life, col, r


class Game:
    def __init__(self, record: bool):
        self.record = record
        self.surf = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.Font(None, 62)
        self.font_md = pygame.font.Font(None, 42)
        self.font_sm = pygame.font.Font(None, 28)
        self.score = 0
        self.reset()

    def reset(self) -> None:
        self.t = 0.0
        self.flash = 0.0
        self.combo = 1
        self.bx, self.by = W * 0.5, PLAY_B - 220
        self.bvx, self.bvy = random.uniform(-90, 90), -780
        self.balls = 3
        self.held = False
        self.la = self.ra = 0.55
        self.lv = self.rv = 0.0
        self.bumpers = [
            (W * 0.32, 520, 54, GOLD),
            (W * 0.68, 520, 54, CYAN),
            (W * 0.50, 740, 62, LILAC),
            (W * 0.28, 980, 46, CORAL),
            (W * 0.72, 980, 46, GOLD),
        ]
        self.spinners = [(W * 0.5, 380, 0.0)]
        self.sparks: list[Spark] = []
        self.stars = [[random.uniform(0, W), random.uniform(0, H), random.uniform(0.4, 2.0)]
                      for _ in range(70)]

    def burst(self, x, y, col, n=14) -> None:
        for _ in range(n):
            a = random.random() * math.tau
            spd = random.uniform(60, 420)
            self.sparks.append(Spark(x, y, math.cos(a) * spd, math.sin(a) * spd,
                                     random.uniform(0.18, 0.45), col, random.randint(3, 7)))

    def _flipper_pts(self, left: bool, ang: float):
        if left:
            base = (PLAY_L + 150, PLAY_B - 70)
            a = math.pi * 0.12 - ang
        else:
            base = (PLAY_R - 150, PLAY_B - 70)
            a = math.pi - math.pi * 0.12 + ang
        tip = (base[0] + math.cos(a) * 210, base[1] + math.sin(a) * 210)
        return base, tip

    def autoplay(self) -> None:
        if self.by > PLAY_B - 380 and self.bvy > 0:
            if self.bx < W * 0.52:
                self.lv = -10.0
            if self.bx > W * 0.48:
                self.rv = -10.0
        else:
            if random.random() < 0.02:
                self.lv = -9.0
            if random.random() < 0.02:
                self.rv = -9.0

    def update(self, dt: float) -> None:
        self.t += dt
        self.flash = max(0.0, self.flash - dt)
        if self.record:
            self.autoplay()
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_z]:
                self.lv = -10.0
            if keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_SLASH]:
                self.rv = -10.0
        self.lv += 18.0 * dt
        self.rv += 18.0 * dt
        self.la = max(0.08, min(0.78, self.la + self.lv * dt))
        self.ra = max(0.08, min(0.78, self.ra + self.rv * dt))
        if self.la >= 0.77:
            self.lv = 0.0
        if self.ra >= 0.77:
            self.rv = 0.0
        self.bvy += 980 * dt
        self.bx += self.bvx * dt
        self.by += self.bvy * dt
        if self.bx < PLAY_L + 28:
            self.bx = PLAY_L + 28
            self.bvx = abs(self.bvx) * 0.86
            self.burst(self.bx, self.by, VEIN, 6)
        if self.bx > PLAY_R - 28:
            self.bx = PLAY_R - 28
            self.bvx = -abs(self.bvx) * 0.86
            self.burst(self.bx, self.by, VEIN, 6)
        if self.by < PLAY_T + 28:
            self.by = PLAY_T + 28
            self.bvy = abs(self.bvy) * 0.8
        for i, (x, y, r, col) in enumerate(self.bumpers):
            dx, dy = self.bx - x, self.by - y
            d = math.hypot(dx, dy) or 1
            if d < r + 18:
                nx, ny = dx / d, dy / d
                self.bx = x + nx * (r + 19)
                self.by = y + ny * (r + 19)
                vn = self.bvx * nx + self.bvy * ny
                self.bvx = (self.bvx - 2 * vn * nx) + nx * 340
                self.bvy = (self.bvy - 2 * vn * ny) + ny * 340
                self.score += 40 * self.combo
                self.combo = min(8, self.combo + 1)
                self.flash = 0.08
                self.burst(x + nx * r, y + ny * r, col, 16)
        sx, sy, ang = self.spinners[0]
        if abs(self.bx - sx) < 90 and abs(self.by - sy) < 36:
            self.spinners[0] = (sx, sy, ang + 14 * dt)
            self.score += 2
            self.bvy -= 20
        else:
            self.spinners[0] = (sx, sy, ang + 1.6 * dt)
        for left, ang, rising in ((True, self.la, self.lv < -1), (False, self.ra, self.rv < -1)):
            base, tip = self._flipper_pts(left, ang)
            self._hit_segment(base, tip, rising)
        if self.by > PLAY_B + 40:
            self.balls -= 1
            self.combo = 1
            self.burst(self.bx, PLAY_B - 20, CORAL, 28)
            self.bx, self.by = W * 0.5 + random.uniform(-40, 40), PLAY_B - 240
            self.bvx, self.bvy = random.uniform(-120, 120), -820
            if self.balls <= 0:
                self.balls = 3
        spd = math.hypot(self.bvx, self.bvy)
        if spd > 1400:
            self.bvx *= 1400 / spd
            self.bvy *= 1400 / spd
        self._tick_fx(dt)

    def _hit_segment(self, p0, p1, rising: bool) -> None:
        ax, ay = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(ax, ay) or 1
        ux, uy = ax / L, ay / L
        wx, wy = self.bx - p0[0], self.by - p0[1]
        t = max(0.0, min(1.0, (wx * ux + wy * uy) / L))
        cx, cy = p0[0] + ux * L * t, p0[1] + uy * L * t
        dx, dy = self.bx - cx, self.by - cy
        d = math.hypot(dx, dy) or 1
        if d < 22:
            nx, ny = dx / d, dy / d
            self.bx = cx + nx * 23
            self.by = cy + ny * 23
            vn = self.bvx * nx + self.bvy * ny
            kick = 620 if rising else 180
            self.bvx = self.bvx - 1.7 * vn * nx + nx * kick * 0.15
            self.bvy = self.bvy - 1.7 * vn * ny - kick
            self.score += 15
            self.burst(cx, cy, CORAL, 8)

    def _tick_fx(self, dt: float) -> None:
        live = []
        for sp in self.sparks:
            sp.life -= dt
            if sp.life <= 0:
                continue
            sp.x += sp.vx * dt
            sp.y += sp.vy * dt
            live.append(sp)
        self.sparks = live
        for st in self.stars:
            st[1] += (10 + st[2] * 10) * dt
            if st[1] > H:
                st[1] = -4
                st[0] = random.uniform(0, W)

    def handle(self, ev) -> None:
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
            self.score = 0
            self.reset()

    def draw(self, s: pygame.Surface) -> None:
        s.fill(BG)
        for x, y, r in self.stars:
            pygame.draw.circle(s, (40, 36, 90), (int(x), int(y)), int(r))
        table = pygame.Rect(PLAY_L - 18, PLAY_T - 18, PLAY_R - PLAY_L + 36, PLAY_B - PLAY_T + 80)
        pygame.draw.rect(s, INDIGO, table, border_radius=36)
        pygame.draw.rect(s, VEIN, table, 5, border_radius=36)
        for i in range(7):
            y = PLAY_T + 80 + i * 210 + int(math.sin(self.t * 0.7 + i) * 10)
            pygame.draw.line(s, (48, 52, 110), (PLAY_L + 20, y), (PLAY_R - 20, y), 2)
        sx, sy, ang = self.spinners[0]
        pygame.draw.circle(s, (18, 16, 50), (int(sx), int(sy)), 28)
        for k in range(3):
            a = ang + k * math.tau / 3
            pygame.draw.line(s, CYAN, (sx, sy), (sx + math.cos(a) * 70, sy + math.sin(a) * 16), 6)
        pulse = 0.6 + 0.4 * math.sin(self.t * 5)
        for x, y, r, col in self.bumpers:
            pygame.draw.circle(s, (12, 10, 36), (int(x), int(y)), r + 6)
            pygame.draw.circle(s, col, (int(x), int(y)), r)
            pygame.draw.circle(s, INK, (int(x), int(y)), int(r * 0.35 * pulse))
        for left, ang in ((True, self.la), (False, self.ra)):
            base, tip = self._flipper_pts(left, ang)
            pygame.draw.line(s, (40, 8, 24), base, tip, 28)
            pygame.draw.line(s, CORAL, base, tip, 16)
            pygame.draw.circle(s, GOLD, (int(base[0]), int(base[1])), 18)
            pygame.draw.circle(s, INK, (int(tip[0]), int(tip[1])), 10)
        pygame.draw.circle(s, (90, 90, 140), (int(self.bx + 4), int(self.by + 6)), 18)
        pygame.draw.circle(s, INK, (int(self.bx), int(self.by)), 18)
        pygame.draw.circle(s, VEIN, (int(self.bx), int(self.by)), 18, 3)
        pygame.draw.circle(s, (255, 255, 255), (int(self.bx - 5), int(self.by - 6)), 5)
        for sp in self.sparks:
            pygame.draw.circle(s, sp.col, (int(sp.x), int(sp.y)), max(1, int(sp.r * sp.life * 2.4)))
        if self.flash > 0:
            fl = pygame.Surface((W, H), pygame.SRCALPHA)
            fl.fill((255, 220, 120, int(40 * self.flash / 0.08)))
            s.blit(fl, (0, 0))
        title = self.font_lg.render(TITLE, True, VEIN)
        s.blit(title, title.get_rect(center=(W // 2, 54)))
        handle = self.font_sm.render(HANDLE, True, GOLD)
        s.blit(handle, handle.get_rect(center=(W // 2, 104)))
        hud = self.font_md.render(f"SCORE  {self.score}    x{self.combo}    BALLS {self.balls}", True, CYAN)
        s.blit(hud, hud.get_rect(center=(W // 2, 154)))
        hint = self.font_sm.render("A / Z left flipper    D / / right flipper    R reset    x.com/ElbowOS", True, CORAL)
        s.blit(hint, hint.get_rect(center=(W // 2, H - 46)))

    def play(self) -> None:
        screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                else:
                    self.handle(ev)
            self.update(dt)
            self.draw(self.surf)
            screen.blit(self.surf, (0, 0))
            pygame.display.flip()

    def record_mp4(self, path: str) -> None:
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "fast", "-movflags", "+faststart", path,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        frames = FPS * 15
        for i in range(frames):
            self.update(1.0 / FPS)
            self.draw(self.surf)
            proc.stdin.write(pygame.image.tostring(self.surf, "RGB"))
            if i % 30 == 0:
                print(f"frame {i}/{frames}", flush=True)
        proc.stdin.close()
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed: {rc}")
        print("wrote", path)


def main() -> None:
    record = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
    play = "--play" in sys.argv
    if record or not play:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    g = Game(record or not play)
    if record or not play:
        out = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/HOWLITE_FLIP_ElbowOS.mp4")
        g.record_mp4(out)
    else:
        g.play()
    pygame.quit()


if __name__ == "__main__":
    main()
