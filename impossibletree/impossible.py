import os.path
import sys
sys.path.append("..")
import core
scriptpath = os.path.dirname(os.path.realpath( __file__ ))
system = core.System([os.path.join(scriptpath, "plugins")], byFile=True)
print system.plugins.getOptimalLoadOrder()