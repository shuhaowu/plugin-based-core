import helloworld

class HelloWorld:
    def __init__(self):
        self.name = "HelloWorld Plugin"
        self.author = "Ultimatebuster"
        self.uniquename = "helloworld"
        self.dependency = [[]]
    
    def load(self, system):
        self.system = system
        return True
    
    def prepare(self, system):
        return system.events.registerPluginToEvent(self, "SystemInit", "main")
    
    def signal(self, args):
        pass
    
    def main(self, args=None):
        print "Hello world from pluginA_helloworld.py"
        helloworld.print_helloworld()
        print "Event:", args["event"]
        return True
        
    def unload(self, system):
        return system.events.unregisterPluginFromEvent(self, "SystemInit") 
        

yayPlugins = (HelloWorld(), )