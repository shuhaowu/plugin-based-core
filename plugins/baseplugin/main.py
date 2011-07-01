class Plugin:
    def __init__(self):
        self.name = "Base Depandent Plugin"
        self.uniquename = "basedep"
    
    def load(self, system):
        return True
    
    def unload(self, system):
        return True
    
    def main(self, args):
        pass
    
    def prepare(self, system):
        return True
    
    def signal(self, args):
        pass
    

plugins = (Plugin(), )