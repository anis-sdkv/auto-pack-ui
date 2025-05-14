

class ScreenBase:
    def __init__(self, context):
        self.context = context
        self.surface = context.surface
        self.ui_manager = context.ui_manager
        self.screen_manager = context.screen_manager
        self.config = context.config

    def handle_event(self, event):
        pass

    def handle_resize(self, new_size):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass
