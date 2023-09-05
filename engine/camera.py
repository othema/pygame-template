import random

import pygame
import time

from engine.object import Object


class Camera(Object):
    def __init__(self, game, position=(0, 0)):
        super(Camera, self).__init__(game)

        self.position = pygame.Vector2(position)
        self.bounds = pygame.Rect(*self.position, *self.game.window_size)

        self.size = pygame.Vector2(game.window_size)

        self.offset = pygame.Vector2(0, 0)
        self.do_shake = False
        self.finish_shake = 0
        self.shake_intensity = 0
        self.shake_wait = 0
        self.next_shake = 0
        self.shake_length = 0

    def update(self):
        self.bounds.topleft = self.position
        if self.do_shake and self.finish_shake > time.time():
            if self.next_shake > time.time():
                time_left = self.finish_shake - time.time()
                multiplier = time_left / self.shake_length

                self.offset = random.uniform(-self.shake_intensity, self.shake_intensity) * multiplier, \
                              random.uniform(-self.shake_intensity, self.shake_intensity) * multiplier

                self.next_shake = time.time() + self.shake_wait

    def lerp(self, position, lerp=0.1):
        self.position += (pygame.Vector2(position) - self.size / 2 - self.position) * lerp * self.game.delta_time * 60

    def _adjust(self, position):
        return position[0] - self.position[0] + self.offset[0], position[1] - self.position[1] + self.offset[1]

    def blit(self, surf, position):
        adjust = self._adjust(position)
        rect = pygame.Rect(position[0], position[1], *surf.get_size())
        if self.in_canvas(rect):
            self.game.wn.blit(surf, adjust)

    def in_canvas(self, rect):
        return self.bounds.colliderect(rect)

    def rect(self, color, rect, border_radius=0, width=0):
        rect = pygame.Rect(rect)
        if not self.in_canvas(rect):
            return

        adjust = self._adjust((rect.x, rect.y))
        new_rect = pygame.Rect(*adjust, rect.w, rect.h)
        pygame.draw.rect(self.game.wn, color, new_rect, width, border_radius=border_radius)

    def line(self, color, point1, point2, width=1):
        adjust1 = self._adjust(point1)
        adjust2 = self._adjust(point2)
        pygame.draw.line(self.game.wn, color, point1, point2, width)

    def shake(self, intensity, length, wait=0.1):
        self.do_shake = True
        self.finish_shake = time.time() + length
        self.shake_intensity = intensity
        self.shake_wait = wait
        self.shake_length = length
        self.next_shake = time.time() + wait
