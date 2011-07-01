import os.path
import core
scriptpath = os.path.dirname(os.path.realpath( __file__ ))
imports = core.PluggableImports([os.path.join(scriptpath, "imports_stuff")])

print imports.get("i.SomeClass")
print imports.get("i.SomeOtherClass")
print imports.get("i.someFunction")

imports.get("i.someFunction")()
imports.get("doesn't exist")