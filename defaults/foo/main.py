class Foo:
    def __init__(self):
        self.name = "Foo default plugin"
        self.uniquename = "foo"
    
    def load(self, system):
        return True
    
    def unload(self, system):
        return True
    
    def main(self, args):
        print "Foo default plugin"
    
    def signal(self, args):
        pass
    
    def prepare(self, system):
        return True
    
plugins = (Foo(), )