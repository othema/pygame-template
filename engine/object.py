import src


class Object():
    def __init__(self, game):
        super(Object, self).__init__()
        self.game: src.game.Game = game
        self.camera = game.camera

    def update(self):
        pass

    def render(self):
        pass
