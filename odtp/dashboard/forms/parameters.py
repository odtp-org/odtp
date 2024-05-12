from nicegui import ui
import odtp.dashboard.utils.helpers as helpers


class ContainerParameters(object):
    def __init__(self, version_tags, parameters):
        self.containers = []
        self.parameters = parameters
        self.version_tags = version_tags
        self.count = len(version_tags)
        for i in range(self.count):
            self.containers.append(ui.row().classes("w-full"))
        self.prefill()

    def prefill(self):        
        for index, version_tag in enumerate(self.version_tags):  
            with ui.grid(columns=2):
                self.add_label_and_buttons(index, version_tag) 
        if self.parameters:     
            for i, row in enumerate(self.parameters):
                if self.parameters[i]:
                    for key, value in self.parameters[i].items():    
                        self.add_parameter_line_for_step(i, key, value)                                     

    def add_label_and_buttons(self, index, tag):
        with self.containers[index]:
            with ui.row():
                with (self.containers[index]).classes("flex items-center"):
                    ui.mermaid(f"""
                        {helpers.get_workflow_mermaid([tag], init='graph TB;')}"""
                    )                 
                    ui.button( 
                        "add line",
                        on_click=lambda index=index: self.add_parameter_line_for_step(index), 
                        icon="add",
                    ).props("flat").classes("text-xs")   
                    ui.button( 
                        "remove line",
                        on_click=lambda index=index: self.remove_parameter_line_for_step(index), 
                        icon="remove",
                    ).props("flat").classes("text-xs")                                             

    def remove_parameter_line_for_step(self, index): 
        if list(self.containers[index]):
            self.containers[index].remove(-1)                        

    def add_parameter_line_for_step(self, index, key="", value=""):  
        with self.containers[index]:
            with ui.grid(columns=2).classes("w-full") :
                key = ui.input(
                    label="key",
                    value=key,
                    placeholder="key"
                )
                value = ui.input(
                    label="value",
                    value=value,
                    placeholder="value"
                )                

    def get_parameters(self):
        parameters = []
        for row in self.containers:
            row_values = []
            for div in row:
                for item in div: 
                    if item.tag == 'nicegui-input':
                        row_values.append(item.value)
            keys = [value for i, value in enumerate(row_values) if i % 2 == 0] 
            values = [value for i, value in enumerate(row_values) if i % 2 != 0]     
            row_parameters = list(zip(tuple(keys), tuple(values))) 
            row_parameters_as_dict = {t[0]: t[1] for t in row_parameters}  
            parameters.append(row_parameters_as_dict)  
        return parameters   
