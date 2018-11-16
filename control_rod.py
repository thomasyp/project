#!/home/yangpu/bin/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 10:15:47 2018

@author: Thomas Yang
"""

class ControlRod(object):
    def __init__(self, **kw):   
        try:    
            self.rod = kw['rod']
            self.trCard = kw['trCard']
            self.rodRange = kw['rodRange']
            self.rodXCoordinate = kw['rodXCoordinate']
            self.rodYCoordinate = kw['rodYCoordinate']
        except KeyError:
            print("The input argument rod, trcard, rodCoordinate or rodRange are not found!")
        except Exception as e:
            print("Unexpected Error: {}".format(e))
        
        self.insertPosition = 0
    
    def __iter__(self):
        return(i for i in (self.rod, self.trCard, self.rodRange, self.rodXCoordinate, self.rodYCoordinate))

    def __repr__(self):
        return str(tuple(self))

    def __str__(self):
        return 'Rod {!r} trcard is {!r}. Rod range is {!r}. Rod coordinate is ({!r}, {!r}).'.format(*self)

    def getTrCardNo(self):
        return self.trCard

    def getRod(self):
        return self.rod

    def getRodRange(self):
        return self.rodRange

    def getRodCoordinate(self):
        return self.rodXCoordinate,self.rodYCoordinate

    def setInsertPosition(self, insertposition):
        self.insertPosition = insertposition

    def getInsertPosition(self):
        return self.insertPosition
    
    def ouputforMcnpinp(self):
        return "{:}   {:}   {:}   {:}\n".format(self.trCard, self.rodXCoordinate, self.rodYCoordinate, self.insertPosition)
    


if __name__ == "__main__":
    cr = ControlRod(rod="3#", trCard='tr3', rodRange=180.0, rodXCoordinate=3.4, rodYCoordinate=4.5)
    print(cr)
