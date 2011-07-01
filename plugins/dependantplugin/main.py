class Plugin:
    def __init__(self):
        self.name = "Depandent Plugin A"
        self.uniquename = "dependant"
        self.dependency = [["basedep"]]
    
    def load(self, system):
        return True
    
    def unload(self, system):
        system.events.unregisterPluginFromEvent(self, "SystemInit")
        return True
    
    def prepare(self, system):
        return system.events.registerPluginToEvent(self, "SystemInit", "main")
    
    def main(self, args):
        print "Depandent Plugin A Mained!"
    
    def signal(self, args):
        pass
    

plugins = (Plugin(), )