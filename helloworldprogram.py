import os.path
import core
scriptpath = os.path.dirname(os.path.realpath( __file__ ))
system = core.System([os.path.join(scriptpath, "plugins")], [os.path.join(scriptpath, "defaults")])
print system.plugins.getOptimalLoadOrder()