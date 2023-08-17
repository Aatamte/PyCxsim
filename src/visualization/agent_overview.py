import dearpygui.dearpygui as dpg


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
        self.message_box.update()

    def update(self):
        if self.agent:
            dpg.set_value(self.agent_name_text, self.agent_name)
            dpg.set_value(self.agent_inventory_text, self.agent.display_inventory())

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

        self.window = None

    def set_agent(self, agent):
        self.agent = agent
        if self.agent != self.last_agent:
            self.redraw_everything()

    def redraw_everything(self):
        dpg.delete_item(self.input_text)
        self.last_agent = self.agent
        for message in self.existing_messages:
            dpg.delete_item(message)
        self.existing_messages = []

        for idx, message in enumerate(self.agent.message_history):
            if "user" in message:
                indent = 150
            elif "system" in message:
                indent = 150
            else:
                indent = 0

            new_message = dpg.add_text(
                message,
                indent=indent,
                parent=self.window,

                #pos=(10 + indent, idx * 25)
            )
            self.existing_messages.append(new_message)

        self.input_text = dpg.add_input_text(
            label="",
            default_value="chat with agent...",
            callback=self.send_message_to_agent,
            on_enter=True,
            parent=self.window,
        )

    def draw(self):
        with dpg.child_window(label="message box") as self.window:
            if self.agent:
                print(self.agent.message_history)
                for message in self.agent.mesage_history:
                    dpg.add_text(message)

        self.input_text = dpg.add_input_text()

    def send_message_to_agent(self, id, message):
        self.agent.message_history.append(
            {"user": message}
        )
        self.redraw_everything()
        print(message)

    def update(self):
        print(self.agent.model_id)
        print(self.agent.usage_statistics)
        print(self.agent.message_history)
        print(self.agent.usage_statistics)
        pass

    def add_agent_message(self, message: str):
        pass

    def add_user_message(self, message: str):
        pass

