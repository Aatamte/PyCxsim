import dearpygui.dearpygui as dpg


class Tab:
    def __init__(self, name, tag):
        self.name = name
        self.tag = tag

    def create(self):
        pass

    def draw_adjacency_matrix(self, adjacency_matrix):
        mat = self.environment.artifact_controller.artifacts["Market"].get_adjacency_matrix()
        for source_idx, source_agent in enumerate(self.environment.agents):
            for target_idx, target_agent in enumerate(self.environment.agents):
                try:
                    if mat[source_idx][target_idx] == 1:
                        dpg.show_item(self.agent_interaction_table[source_agent.id][target_agent.id])
                    elif source_agent != target_agent:
                        dpg.hide_item(self.agent_interaction_table[source_agent.id][target_agent.id])
                except Exception as e:
                    print(e)
                    print(source_agent, source_idx, target_agent, target_idx)
                    raise Warning()