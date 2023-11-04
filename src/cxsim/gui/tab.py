import dearpygui.dearpygui as dpg


class Tab:
    def __init__(self, name, tag, environment, artifact):
        self.name = name
        self.tag = tag
        self.environment = environment
        self.artifact = artifact

        self.show = False
        self.window = None

    def create(self):
        pass

    def set_show(self, value: bool):
        self.show = value
        if value:
            dpg.show_item(self.window)
        else:
            dpg.hide_item(self.window)