import pygame
from uuid import uuid4

from engine.helpers import JSON
from engine.camera import Camera
import engine.ui as ui
from src.components.notifications import NotificationManager


class Game:
    main = None

    def __init__(self, initial_scene):
        if Game.main is None:
            Game.main = self

        pygame.init()

        self.config = JSON.load("conf/config.json")
        self.images = JSON.load("conf/images.json")
        self.sounds = JSON.load("conf/sounds.json")

        self.window_size = self.config["window_size"]
        self.wn = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption(self.config["window_caption"])

        self.scene_id = str(uuid4())

        self.camera = None
        self.camera = Camera(self)
        self.notifications = NotificationManager(self)
        self.scene = initial_scene(self) if initial_scene is not None else None
        self.debug_menu = False

        self.clock = pygame.time.Clock()
        self.delta_time = 0.1
        self.fps = 0
        self.events = []
        self.keys = {}

        self.is_mouse_down = False
        self.was_mouse_down = False
        self.just_mouse_down = False
        self.just_mouse_up = False

        self.transition_to = (None, None, None, None)  # Scene, args, transition, wait_for

    def run(self):
        while True:
            self.calculate_fps()
            self.run_events()

            self.update()
            self.render()

    def calculate_fps(self):
        self.delta_time = self.clock.tick(self.config["target_fps"]) / 1000
        self.fps = self.clock.get_fps()

    def run_events(self):
        self.keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed(3)
        self.is_mouse_down = mouse[0]
        self.just_mouse_down = not self.was_mouse_down and self.is_mouse_down
        self.just_mouse_up = self.was_mouse_down and not self.is_mouse_down

        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.debug_menu = not self.debug_menu

        self.was_mouse_down = self.is_mouse_down

    def update(self):
        self.camera.update()
        self.notifications.update()
        if self.scene is not None: self.scene.update()

    def render(self, update=True):
        self.wn.fill((0, 0, 0))

        if self.scene is not None:
            self.scene.render()
        else:
            ui.text_screen(self, "No scene is loaded.", (20, 20))

        self.notifications.render()

        if self.debug_menu:
            style = {"size": 30, "color": "white", "font": None, "background": (0, 0, 0)}
            ui.text_screen(self, f"{round(self.fps)} fps (at {self.config['target_fps']} cap)", (5, 5), **style)
            ui.text_screen(self, f"{self.delta_time} delta", (5, 30), **style)
            ui.text_screen(self, f"Scene: {self.scene.__class__.__name__}", (5, 80), **style)
            ui.text_screen(self, f"Camera at {round(self.camera.position.x)},{round(self.camera.position.y)}", (5, 105),
                           **style)

        if update:
            pygame.display.update()
            self._transition()

    def _transition(self):
        if None in self.transition_to[:2]:
            return

        self.scene_id = str(uuid4())
        self.scene.on_close()

        new = self.transition_to[0](self, *self.transition_to[1])
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if self.transition_to[2] == "instant":
            self.scene = new
        elif self.transition_to[2] == "fade":
            self.run_events()
            # self.render(False)
            old_surf = self.wn.copy().convert()

            if self.transition_to[3]:
                while not self.transition_to[3]():
                    self.render()

            self.scene = new
            self.render(False)
            new_surf = self.wn.copy().convert()

            for i in range(255):
                self.wn.fill((0, 0, 0))

                old_surf.set_alpha(255 - i)
                self.wn.blit(old_surf, (0, 0))

                new_surf.set_alpha(i)
                self.wn.blit(new_surf, (0, 0))

                pygame.display.update()

            self.scene.render()
        self.transition_to = (None, None, None, None)

    def transition_scene(self, other, *other_args, transition="fade", wait_for=None):
        # transitions include: instant, fade, slide_left, slide_right
        self.transition_to = (other, other_args, transition, wait_for)

    def exit(self):
        if self.scene:
            self.scene.on_close()
        pygame.quit()
        exit()
