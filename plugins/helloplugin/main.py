import helloworld

class HelloWorld:
    def __init__(self):
        self.name = "HelloWorld Plugin"
        self.author = "Ultimatebuster"
        self.uniquename = "helloworld"
        self.dependency = [["dependant"]]
    
    def load(self, system):
        self.system = system
        if not system.plugins.isActive("dependant"):
            return False
        return True
    
    def prepare(self, system):
        return system.events.registerPluginToEvent(self, "SystemInit", "main")
    
    def signal(self, args):
        pass
    
    def main(self, args=None):
        print "Hello world from main.py"
        helloworld.print_helloworld()
        print "Event:", args["event"]
        return True
        
    def unload(self, system):
        return system.events.unregisterPluginFromEvent(self, "SystemInit") 
        

plugins = (HelloWorld(), )