import dearpygui.dearpygui as dpg

color_dict = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'brown': (165, 42, 42),
    'gray': (128, 128, 128),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}


class AgentOverview:
    def __init__(self, environment):
        self.environment = environment
        self.agent = None
        self.message_box = MessageBox()
        self.show = False
        self.agent_name = None

        self.agent_overview_window = None

        self.agent_name_text = dpg.generate_uuid()
        self.agent_inventory_text = dpg.generate_uuid()

    def change_agent(self, new_agent_name):
        self.agent_name = new_agent_name
        self.agent = self.environment.agent_name_lookup[new_agent_name]
        self.message_box.set_agent(self.agent)
        self.update()
        self.message_box.update(self.agent)

    def update(self):
        if self.agent:
            dpg.set_value(self.agent_name_text, self.agent_name)
            dpg.set_value(self.agent_inventory_text, self.agent.display_inventory())
            self.message_box.update(self.agent)

    def set_show(self, value: bool):
        self.show = value
        if value:
            dpg.show_item(self.agent_overview_window)
        else:
            dpg.hide_item(self.agent_overview_window)

    def draw(self):
        with dpg.child_window(label="Agent Overview", show=self.show) as self.agent_overview_window:
            with dpg.collapsing_header(label="agent"):
                for agent in self.environment.agents:
                    dpg.add_selectable(label=agent.name, tag=agent.name, callback=self.change_agent, disable_popup_close=True)

            dpg.add_text("Name")
            dpg.add_same_line()
            self.agent_name_text = dpg.add_text(self.agent_name)

            dpg.add_text("Inventory")
            self.agent_inventory_text = dpg.add_text(self.agent)

            self.message_box.draw()

    def get_window(self):
        return self.agent_overview_window


class MessageBox:
    def __init__(self):
        self.agent = None
        self.last_agent = None
        self.existing_messages = []

        self.agent_name = dpg.generate_uuid()
        self.agent_messages = [dpg.generate_uuid()]
        self.user_messages = [dpg.generate_uuid()]

        self.num_existing_messages = 0

        self.input_text = dpg.generate_uuid()

        self.send_hint = dpg.generate_uuid()

        self.window = None

    def set_agent(self, agent):
        self.agent = agent
        if self.agent != self.last_agent:
            self.redraw_everything()

    def redraw_everything(self):
        dpg.delete_item(self.input_text)
        dpg.delete_item(self.send_hint)
        self.last_agent = self.agent
        for message in self.existing_messages:
            dpg.delete_item(message)
        self.existing_messages = []
        print(self.agent.messages)
        for idx, message in enumerate(self.agent.messages):
            if "user" in message.keys():
                indent = 0
                color = color_dict["red"]
            elif "system" in message.keys():
                indent = 0
                color = color_dict["blue"]
            else:
                indent = 0
                color = color_dict["orange"]

            new_message = dpg.add_text(
                message["content"],
                indent=indent,
                parent=self.window,
                wrap=350,
                color = color
                #pos=(10 + indent, idx * 25)
            )
            self.existing_messages.append(new_message)

        self.input_text = dpg.add_input_text(
            label="",
            multiline=True,
            default_value="",
            hint="chat with agent...",
            callback=self.send_message_to_agent,
            on_enter=True,
            parent=self.window,
        )
        self.send_hint = dpg.add_text("CTRL + ENTER to send message", parent=self.window)

    def draw(self):
        with dpg.child_window(label="message box") as self.window:
            if self.agent:
                for message in self.agent.messages:
                    dpg.add_text(message)

        self.input_text = dpg.add_input_text()
        self.send_hint = dpg.add_text("CTRL + ENTER to send message", parent=self.window)

    def send_message_to_agent(self, id, message):
        self.agent.receives_message(message)
        self.redraw_everything()
        print(message)

    def update(self, agent):
        if len(self.existing_messages) != len(agent.messages):
            self.redraw_everything()

    def add_agent_message(self, message: str):
        pass

    def add_user_message(self, message: str):
        pass

