import os.path
import core
scriptpath = os.path.dirname(os.path.realpath( __file__ ))
kwargs = {"byFile": True, "pluginsAttributeName" : "yayPlugins"}
system = core.System([os.path.join(scriptpath, "pluginbyfile")], **kwargs)