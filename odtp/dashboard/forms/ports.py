from nicegui import ui
import odtp.dashboard.utils.validators as validators
import odtp.dashboard.utils.helpers as helpers


class ContainerPorts(object):
    def __init__(self, version_tags, ports):
        self.containers = []
        self.ports = ports
        self.version_tags = version_tags
        self.count = len(version_tags)
        for i in range(self.count):
            self.containers.append(ui.row().classes("w-full"))
        self.prefill()    

    def prefill(self):        
        for index, version_tag in enumerate(self.version_tags):     
            self.add_label(index, version_tag)
            self.add_button(index) 
        if self.ports:     
            for i, row in enumerate(self.ports):
                if self.ports[i]:
                    for value in self.ports[i]:    
                        self.add_port(i, value)                                  

    def add_label(self, index, tag):
        with self.containers[index].classes("flex align-center"):
            ui.mermaid(f"""
                {helpers.get_workflow_mermaid([tag], init='graph TB;')}"""
            ) 

    def add_button(self, index):
        with self.containers[index]:
            ui.button( 
                on_click=lambda index=index: self.add_port(index), 
                icon="add",
            ).props("flat").classes("content-center pt-5 text-xs") 
            ui.button( 
                on_click=lambda index=index: self.remove_port(index), 
                icon="remove",
            ).props("flat").classes("content-center pt-5 text-xs")               

    def remove_port(self, index): 
        row = [item for item in self.containers[index] if item.tag == "nicegui-input"]
        if row and len(row) > 0:
            self.containers[index].remove(-1)                        

    def add_port(self, index, value=""):  
        with self.containers[index]:
            ui.input(
                label="port",
                validation={f"Please provide a valid port mapping":
                lambda value: validators.validate_ports_mapping_input(value)},
                value=value,
                placeholder="8001:8001"
            )

    def get_ports(self):
        ports_inputs = []
        for row in self.containers:
            ports_per_row = []
            for item in list(row):
                if item.tag == 'nicegui-input' :
                    ports_per_row.append(item)   
            ports_inputs.append(ports_per_row)  
        return ports_inputs      
