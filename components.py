class Transform:    # Типа класс позиции и размера
    def __init__(self, pos, scale=(1, 1), parent=None):
        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.scale = pygame.math.Vector2(scale[0], scale[1])
        self.parent = parent

    def int_pos(self):
        return self.x(), self.y()

    def set_pos(self, x, y):
        self.pos = pygame.math.Vector2(x, y)

    def global_pos(self):
        return pygame.math.Vector2(self.x(), self.y())

    def x(self):
        if self.parent is not None:
            return int(self.parent.pos.x + self.pos.x)
        return int(self.pos.x)

    def y(self):
        if self.parent is not None:
            return int(self.parent.pos.y + self.pos.y)
        return int(self.pos.y)