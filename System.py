class System (object):

    def __init__(self, SystemName):

        self.Name = SystemName
        self.Lens = [];

    def rename (self, newName):
    	self.Name = newName

    def addLens (self, lensName):
    	self.Lens.append(lensName)
