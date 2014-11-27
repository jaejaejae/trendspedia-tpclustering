class Cluster(object):
    def __init__(self, seed):
        self.children = set()
        self.elements = set()
        self.parent = None
        self.representation = None
        self.seed = seed
    def addChild(self, cluster):
        self.children.add(cluster)
        cluster.setParent(self)
    def setParent(self, parent):
        self.parent = parent
    def addElements(self, elem):
        self.elements.add(elem)
