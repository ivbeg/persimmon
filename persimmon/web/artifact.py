"""Persimmon artifact
http://persimmon-project.org

Persimmon artifact - basic web page object 

"""


__author__ = "Ivan Begtin (ibegtin@gmail.com)"
__version__ = "1.0.1"
__copyright__ = "Copyright (c) 2017 Ivan Begtin"
__license__ = "BSD"



class Artifact:
    """Artifact. Base class represents web page / web site object"""
    def __init__(self, node, uniq=None, attrs=None):
        if not attrs: attrs = {}
        self.node = node
        self.uniq = uniq
        self.attrs = attrs 
        self.__childs = []
    
    def add_child(self, artifact):
        """Adds child to the artifact"""
        self.__childs.append(artifact)
        
        
class List(Artifact):
    """List of artifacts"""
    def __init__(self, node, items, uniq=None, attrs={}):
        Artifact.__init__(node, uniq, attrs)
        self.__items = items
        
    def items(self):
        return self.__items
    
    
class Table(List):
    """Table of objects"""
    def __init__(self, node, items, schema, uniq=None, attrs={}):
        Artifact.__init__(node, uniq, attrs)
        self.__items = items
        self.__schema = schema
                
    def schema(self):
        return self.__schema

class Script(Artifact):
    """Script object"""
    def __init__(self, node, uniq=None, attrs={}):
        Artifact.__init__(node, uniq, attrs)
    
        