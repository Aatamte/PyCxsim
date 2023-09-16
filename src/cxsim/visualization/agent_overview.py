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
        self.show = False
        self.agent_name = None

        self.agent_overview_window = None

        self.agent_name_text = dpg.generate_uuid()
        self.agent_inventory_text = dpg.generate_uuid()

        self.message_box = MessageBox()
        self.action_history = ActionHistoryVisualization()
        self.inventory_viz = InventoryVisualization()
        self.parameter_viz = ParameterVisualization()

        self.current_tab = "inventory"

        self.tab_options = {
            "messages": self.message_box,
            "actions": self.action_history,
            "inventory": self.inventory_viz,
            "params": self.parameter_viz
        }

    def resize(self):
        self.message_box.resize()

    def change_agent(self, sender, new_agent_name):
        self.agent_name = new_agent_name
        self.agent = self.environment.agent_name_lookup[new_agent_name]

        self.update()

    def update(self):
        if self.agent:
            for name, tab in self.tab_options.items():
                tab.update(self.agent)

    def set_show(self, value: bool):
        self.show = value
        if value:
            dpg.show_item(self.agent_overview_window)
        else:
            dpg.hide_item(self.agent_overview_window)

    def show_tab(self, sender, data):

        if self.current_tab:
            self.tab_options[self.current_tab].set_show(False)
        self.tab_options[sender].set_show(True)
        self.current_tab = sender

    def draw(self):
        with dpg.child_window(label="Agent Overview", show=self.show, border=False) as self.agent_overview_window:
            dpg.add_combo(label="Agent", items=[agent.name for agent in self.environment.agents], callback=self.change_agent)
            with dpg.child_window(label="Agent information", menubar=True):
                with dpg.menu_bar(label="agent menu bar"):
                    dpg.add_menu_item(label="inventory", tag="inventory", callback=self.show_tab)
                    dpg.add_menu_item(label="messages", tag="messages", callback=self.show_tab)
                    dpg.add_menu_item(label="actions", tag="actions", callback=self.show_tab)
                    dpg.add_menu_item(label="events", tag="events", callback=self.show_tab)
                    dpg.add_menu_item(label="params", tag="params", callback=self.show_tab)

                for name, tab in self.tab_options.items():
                    tab.draw()

    def get_window(self):
        return self.agent_overview_window


class ActionHistoryVisualization:
    def __init__(self):
        self.show = False
        self.agent = None
        self.window = None

        self.action_table = None

        self.action_history_text = dpg.generate_uuid()

        self.action_history_values = []

        self.max_action_length = 50
        self.action_history_uid = []
        for row_idx in range(self.max_action_length):
            self.action_history_uid.append([dpg.generate_uuid(), dpg.generate_uuid(), dpg.generate_uuid()])

        self.rows_uuids = []

    def resize(self):
        pass

    def update(self, agent):
        self.agent = agent
        for idx, row in enumerate(range(len(agent.action_history))):
            dpg.set_value(self.action_history_uid[idx][2], str(agent.action_history[-(idx + 1)]))
            dpg.set_value(self.action_history_uid[idx][0], len(agent.action_history) - (idx + 1))

    def draw(self):
        with dpg.child_window(label="actions", border=False, show=self.show) as self.window:
            with dpg.table(header_row=True) as self.action_table:
                # use add_table_column to add columns to the table,
                # table columns use child slot 0
                dpg.add_table_column(label="step", init_width_or_weight=0.2)
                dpg.add_table_column(label="artifact", init_width_or_weight=0.3)
                dpg.add_table_column(label="action")

                for i in range(self.max_action_length):
                    with dpg.table_row():
                        for j in range(0, 3):
                            self.action_history_uid[i][j] = dpg.add_text("N/A", wrap=250)

    def set_show(self, value):
        self.show = value
        if self.show:
            dpg.show_item(self.window)
        else:
            dpg.hide_item(self.window)


class InventoryVisualization:
    def __init__(self):
        self.show = False
        self.agent = None
        self.window = None

        self.inventory_text = dpg.generate_uuid()

    def update(self, agent):
        self.agent = agent
        dpg.set_value(self.inventory_text, self.agent.display_inventory())

    def draw(self):
        with dpg.child_window(label="inventory", border=False, show=self.show) as self.window:
            self.inventory_text = dpg.add_text("")

    def set_show(self, value):
        self.show = value
        if self.show:
            dpg.show_item(self.window)
        else:
            dpg.hide_item(self.window)


class ParameterVisualization:
    def __init__(self):
        self.show = False
        self.agent = None
        self.window = None

        self.param_text = dpg.generate_uuid()

    def update(self, agent):
        self.agent = agent
        dpg.set_value(self.param_text, self.agent.params)

    def draw(self):
        with dpg.child_window(label="inventory", border=False, show=self.show) as self.window:
            self.param_text = dpg.add_text("")

    def set_show(self, value):
        self.show = value
        if self.show:
            dpg.show_item(self.window)
        else:
            dpg.hide_item(self.window)


class MessageBox:
    def __init__(self):
        self.agent = None
        self.last_agent = None
        self.existing_messages = []
        self.show = False

        self.agent_name = dpg.generate_uuid()
        self.agent_messages = [dpg.generate_uuid()]
        self.user_messages = [dpg.generate_uuid()]

        self.num_existing_messages = 0

        self.input_text = dpg.generate_uuid()

        self.send_hint = dpg.generate_uuid()

        self.window = None

        self.wrap_size = 350

    def update(self, agent):
        self.agent = agent
        self.redraw_everything(True)

    def resize(self):
        self.wrap_size = int((2 * dpg.get_viewport_width() / 5) * 0.8)
        if self.existing_messages:
            self.redraw_everything(True)

    def redraw_everything(self, include_input_text):
        if include_input_text:
            dpg.delete_item(self.input_text)
            dpg.delete_item(self.send_hint)

        self.last_agent = self.agent
        for message in self.existing_messages:
            dpg.delete_item(message)
        self.existing_messages = []

        for idx, message in enumerate(self.agent.messages):
            if message["role"] == "user":
                message["content"] = "User: " + message["content"]
                indent = 0
                color = color_dict["green"]
            elif message["role"] == "system":
                indent = 0
                message["content"] = "System: " + message["content"]
                color = color_dict["red"]
            else:
                indent = 0
                if message["content"]:
                    message["content"] = self.agent.name + ": " + message["content"]
                else:
                    message["content"] = self.agent.name + ": made function call"
                color = color_dict["orange"]

            new_message = dpg.add_text(
                message["content"],
                indent=indent,
                parent=self.window,
                wrap=self.wrap_size,
                color=color
                #pos=(10 + indent, idx * 25)
            )
            self.existing_messages.append(new_message)

        if include_input_text:
            self.input_text = dpg.add_input_text(
                label="",
                multiline=True,
                default_value="",
                hint="chat with agent...",
                callback=self.send_message_to_agent,
                on_enter=True,
                parent=self.window,
            )
            self.send_hint = dpg.add_text("CTRL + ENTER to send message\n\n\n\n\n\n", parent=self.window)

    def set_show(self, value):
        self.show = value
        if self.show:
            dpg.show_item(self.window)
        else:
            dpg.hide_item(self.window)

    def draw(self):
        with dpg.child_window(label="message box", border=False, show=self.show) as self.window:
            if self.agent:
                for message in self.agent.messages:
                    dpg.add_text(message)

            self.input_text = dpg.add_input_text()
            self.send_hint = dpg.add_text("CTRL + ENTER to send message", parent=self.window)

    def send_message_to_agent(self, id, message):
        self.agent.messages.append(
            {
                "role": "user",
                "content": message
            }
        )
        self.agent.create_ChatCompletion()
        self.redraw_everything(True)

    def add_agent_message(self, message: str):
        pass

    def add_user_message(self, message: str):
        pass

