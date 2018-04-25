#send back what the server get 
from twisted.internet import protocol as po
from autobahn.twisted.websocket import WebSocketServerFactory,WebSocketServerProtocol
import sys
from twisted.python import log
import requests
import json
from WXBizDataCrypt import WXBizDataCrypt
from locolProtocol import WxProtocol,ArmServerFactory,ArmServerFactory

def main():
    portwx = 9999
    portarm = 8888
    #log.startLogging(sys.stdout)
    wxfactory = WebSocketServerFactory()
    wxfactory.protocol = WxProtocol
    armfactory = ArmServerFactory()

    from twisted.internet import reactor

    reactor.listenTCP(portwx,wxfactory)     #listening weixin
    reactor.listenTCP(portarm,armfactory)   #listening arm
    reactor.run()

if __name__ == '__main__':
    main()
