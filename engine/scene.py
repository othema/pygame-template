from engine.object import Object


class Scene(Object):
    def __init__(self, game):
        super(Scene, self).__init__(game)

        self.camera = game.camera
        self.wn = game.wn

    def on_close(self):
        pass
