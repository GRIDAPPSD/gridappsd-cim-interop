import jsons
class Device(object):
    '''
    represents an end device
    '''

    def __init__(self, mRID=None, name=None, isSmartInverter=None, usagePoint=None, **kwargs):
        self.mRID = mRID
        self.name = name
        self.isSmartInverter = isSmartInverter
        self.usagePoint = usagePoint

    def __repr__(self):
        return jsons.dumps(self.__dict__)