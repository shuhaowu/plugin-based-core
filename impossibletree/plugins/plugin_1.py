class Plugin1:
    def __init__(self, level, dep):
        self.name = "Level %d Plugin" % level
        self.uniquename = "level-%d" % level
        self.dependency = dep
    
    def load(self, system):
        self.system = system
        return True
    
    def prepare(self, system):
        return system.events.registerPluginToEvent(self, "SystemInit", "main")
    
    def signal(self, args):
        pass
    
    def main(self, args=None):
        print self.name + " mained."
        return True
        
    def unload(self, system):
        return system.events.unregisterPluginFromEvent(self, "SystemInit") 
    def __repr__(self):
        return self.uniquename
        

plugins = (Plugin1(1, [[]]), Plugin1(2, [['level-1', 'level-5']]), Plugin1(3, [['level-2']], ),
           Plugin1(4, [['level-3']]), )