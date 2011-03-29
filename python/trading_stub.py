# Stubs for debuggin under linux

class MarketListener:
    def __init__(self):
        pass
    def onTableData(self, *args):
        pass
    def onConnected(self): 
        pass
    def onDisconnected(self): 
        pass
    def onTransactionResult(self, *args): 
        pass

class Market:
    def addListener(self, *args):
        pass
    def removeListener(self, *args):
        pass
    def run(self):
        pass
    def stop(self):
        pass
    def connect(self, *args):
        pass
    def disconnect(self):
        pass
    def sendAsync(self, *args):
        pass
    def setDebug(self, *args):
        pass
    def errorMessage(self):
        pass
    def errorCode(self):
        pass

