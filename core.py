""" plugin-based-core created by Shuhao Wu. """

__author__ = "Shuhao Wu"
__copyright__ = "Copyright 2010, Shuhao Wu"
__license__ = "Apache License 2.0"
__version__ = "trunk"
__email__ = "admin@thekks.net"
__status__ = "Development"

# importing some essential modules.
import os, sys
import logging
logger = logging.getLogger("core")
# Set logging basic formats
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

# Just an exception with a different name
class DependencyNotSatisfiedError(Exception): pass

class PlaceHolder: pass
placeholder = PlaceHolder()

def constructSignalArguments(**kwargs):
    """ Construct a dictionary with required arguments there. 
        Prevents issue with KeyErrors.
        
        **kwargs - any keyword arguments
        
        Returns: dict
        """
    signal = {
              "loaded" : None,
              "unloaded" : None,
              "event" : None,
              "signaller" : None,
              "system" : None,
              }
    signal.update(kwargs)
    
    return signal

class PluginNode:
    """ A node for a plugin in a dependency of plugins """
    # TODO: Add support for parents, not just child.
    def __init__(self, plugin, dependency=[[]]):
        self.plugin = plugin
        self.dependency = dependency
    
class EventManager:
    """ The event manager. It managers all the events"""
    
    def __init__(self, system):
        self.system = system
        self._logger = logging.getLogger("core.EventManager")
            
        self._events = {}
    
    def registerEvent(self, eventname):
        """ Registers a new event in memory. """ 
        if eventname not in self._events:
            self._events[eventname] = []
            self._logger.info("%s event has successfully registered." % eventname)
            return True
        else:
            return False
        
    def unregisterEvent(self, eventname):
        """ Unregister an event from memory. """
        if eventname in self._events:
            del self._events[eventname]
            self._logger.info("%s event has successfully unregistered." % eventname)
            return True
        else:
            return False

    def registerPluginToEvent(self, plugin, eventname, functionname):
        """ registers a plugin to an event. 
        plugin is a plugin instance or a plugin name
        eventname is a name of an event
        functionname is the name of the function under the plugin object that will be called when the event is fired"""
        plugin = self.system.plugins.getPlugin(plugin)
        if plugin and eventname in self._events:
            if plugin in self._events[eventname]:
                self._logger.warning("%s is already associated with %s." % (plugin.name, eventname))
                return True            
            self._events[eventname].append((plugin, functionname))
            self._logger.info("%s.%s() has successfully registered to %s" % (plugin.uniquename, functionname, eventname))
            return True
        self._logger.warning("%s failed to register to %s." % (plugin.uniquename, eventname))
        return False
    
    def unregisterPluginFromEvent(self, plugin, eventname):
        """ unregister a plugin from an event.
        plugin is a Plugin instance or a plugin name"""
        plugin = self.system.plugins.getPlugin(plugin)
        if plugin and eventname in self._events:
            if plugin not in self._events[eventname]:
                self.logger.warning("%s is not associated with %s in the first place." % (plugin.name, eventname))
                return True
            count = 0
            for i in xrange(len(self._events[eventname])):
                if self._events[eventname][i][0] == plugin:
                    count += 1
                    self._events[eventname].pop(i)
                    
            self._logger.info("%d %s plugin(s) unregistered from %s." % (count, plugin.uniquename, eventname))
            return True
        self._logger.warning("%s failed to unregister to %s." % (plugin.uniquename, eventname))
        return False
          
    def getEventPlugins(self, eventname):
        """ Get the list of plugins associated with the event """
        return self._events.get(eventname, None)
        
    def fire(self, eventname, signalAll=False, **kwargs):
        """ Fires an event and all it's plugins. """
        if eventname in self._events:
            kwargs["event"] = eventname
            self._logger.info("Firing event %s. signalAll: %d" % (eventname, int(signalAll)))
            returnStatus = [True, {}]
            for plugin, functionname in self._events[eventname]:
                if self.system.plugins.isInactive(plugin.uniquename):
                    continue
                
                func = getattr(plugin, functionname)
                status = func(kwargs)
                returnStatus[1][plugin.uniquename] = status
                if not status:
                    returnStatus[0] = False
                
            if signalAll:
                signaller = kwargs.get("signaller", None)
                self.system.plugins.signalAll(event=eventname, system=self.system, signaller=signaller)
            self._logger.info("%s status: %s" % (eventname, str(returnStatus)))
            return returnStatus
        else:
            self._logger.info("Event, %s, doesn't exist." % eventname)
            return False

class PluginManager:
    """ Manages plugins """
    def __init__(self, system):
        self._logger = logging.getLogger("core.PluginManager")
        
        self._activePlugins = {} 
        self._inactivePlugins = {}
        self._preloadedPlugins = {}
        self._optimalLoadOrder = []
        self.system = system
    
    def getPluginGivenLocation(self, plugin, location):
        if isinstance(plugin, str): 
            if plugin in location:
                return location[plugin]
            else:
                return None
        else:
            if plugin in location.values():
                return plugin
            else:
                return None
    
    def getPlugin(self, plugin):
        """ Gets a plugin from the active list only. plugin can either be an uniquename or the instance """
        return self.getPluginGivenLocation(plugin, self._activePlugins)
    
    def getInactivePlugin(self, plugin):
        """ Gets a plugin from the inactive list. plugin can either be an uniquename or the instance """
        return self.getPluginGivenLocation(plugin, self._inactivePlugins)
    
    def importPlugins(self, plugindir, byFile=False, byFileStartsWith="plugin_", byDirFileName="main", pluginsAttributeName="plugins"):
        if os.path.isdir(plugindir):
            if plugindir not in sys.path:
                sys.path.append(plugindir)
            for filename in os.listdir(plugindir):
                path = os.path.join(plugindir, filename)
                _temp = False
                if byFile:
                    if os.path.isfile(path) and filename.startswith(byFileStartsWith) and filename.endswith(".py"):
                        _temp = __import__(os.path.splitext(filename)[0], fromlist=[pluginsAttributeName])
                else:
                    if os.path.isdir(path) and ("%s.py" % byDirFileName) in os.listdir(path):
                        _temp = __import__(filename+"."+byDirFileName, fromlist=[pluginsAttributeName])
                if _temp:
                    plugins = getattr(_temp, pluginsAttributeName)
                    for plugin in plugins:
                        self.preloadPlugin(plugin)
                                
                                
            self.buildOptimalLoadOrder()
            for i in xrange(len(self._optimalLoadOrder)):
                self.loadPlugin(self._optimalLoadOrder[i])
        else:
            raise TypeError("%s is not a directory." % plugindir)
                
    def preloadPlugin(self, plugin):
        """ Preloads the plugin, put it into a node with dependency mappings """
        try:
            _temp = __import__(plugin, fromlist=["plugin"])
            plugin = _temp.plugin
        except TypeError: # Occurs if plugin is actually a plugin instance
            pass
        
        if hasattr(plugin, "dependency"):
            self._preloadedPlugins[plugin.uniquename] = PluginNode(plugin, plugin.dependency)
        else:
            self._preloadedPlugins[plugin.uniquename] = PluginNode(plugin)
            
    def buildOptimalLoadOrder(self):
        # Comments needed.
        self._optimalLoadOrder = []
        for pluginname in self._preloadedPlugins:
            plugin = self._preloadedPlugins[pluginname]
            _tempplugins = self.findLowestPlugin(plugin)
            for p in _tempplugins:
                if p not in self._optimalLoadOrder:
                    self._optimalLoadOrder.append(p)
    
    def findLowestPlugin(self, plugin):
        # Comments needed.
        satisfiedDependency = False
        # Initializes an empty list for the dependencies
        dep = []
        # Initializes an empty list for plugins that's not available
        naPlugin = []
        
        # Loop through the different dependencies.
        for dep in plugin.dependency:
            # Assumes that this dependency satisfies.
            thisSatisfies = True
            
            # Loop through the unique names in each dependencies
            for name in dep:
                # Check if they are in the preloadedPlugins.
                if name not in self._preloadedPlugins:
                    thisSatisfies = False
                    naPlugin.append(name)
            
            # If this dependencies, than this whole dependencies is satisfied for this plugin.
            # Break
            if thisSatisfies:
                satisfiedDependency = True
                break
        
        # If this satisfies and the dependencies is not an empty list.
        if satisfiedDependency and dep:
            plugins = []
            # Find the dependencies for each plugin in the dependencies
            for name in dep:
                _tempplugins = self.findLowestPlugin(self._preloadedPlugins[name])
                for p in _tempplugins:
                    if p not in plugins:
                        plugins.append(p)
                        
            # Add the plugin itself to the end of the list.
            if plugin.plugin not in plugins:
                plugins.append(plugin.plugin)
                
            return plugins
        elif not dep: # If there's no dependencies needed for this plugin
            return [plugin.plugin]
        else: # Other wise. Dependencies is not satisfied.
            critical = getattr(plugin.plugin, "critical", False)
            if critical:
                raise DependencyNotSatisfiedError("Critical plugin, %s, cannot be loaded due to the a not satisfied dependency. Missing plugins: %s" % (plugin.plugin.uniquename, str(naPlugin)))
            self._logger.warning("%s cannot be loaded due to %s not being available." % (plugin.plugin.uniquename, str(naPlugin)))
            return []
    
    def isInactive(self, pluginname):
        return pluginname in self._inactivePlugins
    
    def isActive(self, pluginname):
        return pluginname in self._activePlugins
    
    def isRegistered(self, pluginname):
        return pluginname in self._inactivePlugins or pluginname in self._activePlugins
    
    def loadPlugin(self, plugin):
        """ Loads a plugin.
        plugin is the instance of a plugin"""        
        if plugin.uniquename in self._activePlugins:
            return True
        
        if plugin.load(self.system): # If loading returned False, puts to inactive.
            if plugin.uniquename in self._inactivePlugins:
                del self._inactivePlugins[plugin.uniquename]
            
            self._activePlugins[plugin.uniquename] = plugin
            self.signalAll(loaded=plugin.uniquename, signaller=self, system=self.system)
            self._logger.debug("Loaded: %s" % plugin.uniquename)
            return plugin.prepare(self.system)
        else:
            if plugin.uniquename not in self._inactivePlugins:
                self._inactivePlugins[plugin.uniquename] = plugin
                self._logger.debug("%s put to inactive" % plugin.uniquename)
                return False
    
    def unloadPlugin(self, plugin):
        """ Unloads a plugin
        plugin is a plugin instance or plugin uniquename """
        if plugin in self._activePlugins:
            if not self._activePlugins[plugin].unload(self.system): # If unloading fails, don't unload
                return False
            
            del self._activePlugins[plugin]
            return True
        elif plugin in self._activePlugins:
            del self._activePlugins[plugin]
            return True
        else:
            if plugin.uniquename in self._inactivePlugins:
                del self._inactivePlugins[plugin.uniquename]
                return True
            
            if plugin.uniquename in self._activePlugins:           
                if self._activePlugins[plugin.uniquename].unload(self.system):
                    del self._activePlugins[plugin.uniquename]
                    return True
                else:
                    return False
            else:
                return False
             
    def signalAll(self, inactive=True, **kwargs):
        """ Signals all plugins """
        for plugin in self._activePlugins.values():
            self.signal(plugin, **kwargs)
            
        if inactive:
            for plugin in self._inactivePlugins.values():
                self.signal(plugin, **kwargs)
        
        self._logger.info("Signalled all plugins with data: " + str(kwargs))

    def signal(self, plugin, **kwargs):
        """ Sends a signal to a plugin.
        plugin can either be an unique name or a plugin instance"""
        if plugin in self._activePlugins:
            plugin = self._activePlugins[plugin]
        elif plugin in self._inactivePlugins:
            plugin = self._inactivePlugins[plugin]
        
        plugin.signal(constructSignalArguments(**kwargs))
        
    def getOptimalLoadOrder(self):
        return tuple(self._optimalLoadOrder)
    
class Plugin:
    """ This is an empty class for now. Other features may be developed in the future.
    Required attribute:
        .name
        .uniquename - alphanumeric only.
    Required method:
        .load(system) - Executes upon loading into the system. system is the system reference.
        .unload(system) - Executes upon unloading from the system.
        .signal(args) - This is used to signal plugins of events.
        .prepare(system) - This is performed right after loading. Hook into the system Events here.
    Plugin file format: Python file with whatever you want in it. However, only instance will be imported.
    Make sure it has a .plugin attribute at the module level with an instance of your plugin setup to go."""

    def __init__(self):
        self.name = "Plugin Base"
        self.uniquename = "plugin"
    
    def load(self, system):
        return True
    
    def unload(self, system):
        return True
    
    def signal(self, args):
        pass
    
    def prepare(self, system):
        return True
    
    def __repr__(self):
        return "<Plugin:" + self.uniquename + ">"

class System(Plugin):
    """ The system itself. It's also a plugin, technically, only it regulates everything """
    def __init__(self, plugindirs=[], defaultsetdirs=[], autoStart=True, **kwargs):
        self.name = "Core System"
        self.uniquename = "core"
        
        self.plugindirs = plugindirs
        self.defaultsetdirs = defaultsetdirs
        
        self.events = EventManager(self)
        self.plugins = PluginManager(self)
        
        self.byFile = (kwargs.get("byFile", False), kwargs.get("byFileStartsWith", "plugin_"))
        self.byDirFileName = kwargs.get("byDirFileName", "main")
        
        self.pluginsAttributeName = kwargs.get("pluginsAttributeName", "plugins")
        
        self.started = False
        if autoStart:
            self.start()
        
    def start(self):
        """ System starts. Loads plugins and etc. Fires SystemInit event """
        if not self.started:
            self.started = True
            self.events.registerEvent("SystemInit")
            self.plugins.loadPlugin(self)
            
            for defaultsetdir in self.plugindirs:
                self.plugins.importPlugins(defaultsetdir, self.byFile[0], self.byFile[1], self.byDirFileName, self.pluginsAttributeName)
            
            for plugindir in self.plugindirs:
                self.plugins.importPlugins(plugindir, self.byFile[0], self.byFile[1], self.byDirFileName, self.pluginsAttributeName)
            
            self.events.fire("SystemInit")
        else:
            raise RuntimeError("System has already been started.")
    
    def unload(self, system):
        return False

class PluggableImports:
    def __init__(self, plugindirs=[], defaultsetdirs=[], autoStart=True, **kwargs):
        self._plugindirs = plugindirs
        self._defaultsetdirs = defaultsetdirs
        
        self._logger = logging.getLogger("core.PluggableImports")
        
        self._byFile = (kwargs.get("byFile", True), kwargs.get("byFileStartsWith", "imports_"))
        self._byDirFileName = kwargs.get("byDirFileName", "main")
        
        self._importsAttributeName = kwargs.get("importsAttributeName", "imports")
        
        self._imports = {}
        if autoStart:
            self.importAll()
    
    def importDir(self, directory):
        if os.path.isdir(directory):
            self._logger.info("Importing directory %s" % directory)
            if directory not in sys.path:
                sys.path.append(directory)
            imports = {}
            for filename in os.listdir(directory):
                path = os.path.join(directory, filename)
                _temp = False
                if self._byFile[0]:
                    if os.path.isfile(path) and filename.startswith(self._byFile[1]) and filename.endswith(".py"):
                        _temp = __import__(os.path.splitext(filename)[0], fromlist=[self._importsAttributeName, "flags"])
                else:
                    if os.path.isdir(path) and ("%s.py" % self._byDirFileName) in os.listdir(path):
                        _temp = __import__(filename+"."+self._byDirFileName, fromlist=[self._importsAttributeName, "flags"])
                
                if _temp:
                    newRawImports = getattr(_temp, self._importsAttributeName)
                    newImports = {}
                    
                    flags = getattr(_temp, "flags", False)
                    if flags:
                        if flags.get("autoGenerateNames", False) or flags.get("listBased"):
                            for item in newRawImports:
                                try:
                                    newImports[item.__name__] = item
                                except AttributeError:
                                    raise AttributeError("%s (under %s) doesn't have an __name__ attribute for list based imports" % (item, filename))
                        else:
                            newImports = newRawImports
                        
                        prefix = flags.get("prefix", False)
                        
                        if prefix:
                            tempDict = {}
                            for key in newImports:
                                tempDict[prefix+key] = newImports[key]
                            newImports = tempDict
                    else:
                        newImports = newRawImports
                        
                    imports.update(newImports)
                    
            self._logger.info("Imported: " + str(imports))
            return imports
        else:
            raise TypeError("%s is not a directory." % directory)
    
    def updateImports(self, d):
        self._imports.update(d)
        
    def delImport(self, name):
        del self._imports[name]
    
    def importAll(self):
        self._imports = {}
        for defaultsetdir in self._defaultsetdirs:
            self._imports.update(self.importDir(defaultsetdir))
            
        for plugindir in self._plugindirs:
            self._imports.update(self.importDir(plugindir))
        
    def get(self, name, default=placeholder):
        try:
            return self._imports[name]
        except KeyError:
            if default == placeholder:
                raise ImportError("%s is not imported." % name)
            return default
        