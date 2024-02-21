from barfi import st_barfi, barfi_schemas, Block

# TODO: Extract barfi examples for 1 component run, 2 components run, Confluence 3 components, Divergence 3 components

class BarfiManager:
    """This class check all the components available in the components database, and prepare the Barfi class"""
    def __init__(self):
        self.blocks = []
        pass

    def addBlock(self, name, inputs, outputs, options, dockerfunc):
        b = Block(name="name")
        for option in options:
            # Different types of blocks contains different options parameters
            if option["type"] == "display":
                b.add_option(name=option["name"],
                             type=option["type"],
                             value=option["value"])
            elif option["type"] == "select":
                b.add_option(name=option["name"],
                            type=option["type"],
                            value=option["value"],
                            items=option["items"])
            elif option["type"] == "input":
                b.add_option(name=option["name"],
                             type=option["type"],
                             value=option["value"])
            elif option["type"] == "integer":
                b.add_option(name=option["name"],
                             type=option["type"],
                             value=option["value"])
            elif option["type"] == "checkbox":
                b.add_option(name=option["name"],
                             type=option["type"],
                             value=option["value"])
            elif option["type"] == "slider":
                b.add_option(name=option["name"],
                             type=option["type"],
                             value=option["value"],
                             min=option["min"],
                             max=option["max"])
                
        for input in inputs:
            b.add_input(name=input["name"])

        for output in outputs:
            b.add_output(name=output["name"])

        def barfiFunc(self):
            # Here we need to build the docker method that will be send to run
            envStringList = []
            for option in options:
                optionValue = self.get_option(name=option["name"])
                envStringList.append("{}={}".format(option['name'], optionValue))


            # Actually Inputs/Outputs will not be managed by Barfi
            for input in inputs:
                inputValue = self.get_interface(name=input["name"])
                # Need to be copied in a folder. How this works on Barfi?

            for output in outputs:
                self.set_interface(name=output["name"], 
                                   value=output["value"])

            # Run the Component
            # 1. Copy input files
            # 2. Run component

        b.add_compute(barfiFunc)
            
        self.blocks.append(b)
