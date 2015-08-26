#!/usr/bin/python
# Telnet handler concrete class using green threads

import gevent, gevent.queue
from enum import Enum

from .telnetsrvlib import TelnetHandlerBase, command

class deQueue(gevent.queue.Queue):
    '''A subclass of :class:`Queue` that add the possibility to put an item back in the queue.'''
    
    class Side(Enum):
        NORMAL, BACK = range(2)

    def _put(self, item):
        if isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], self.Side):
            if item[0] == self.Side.BACK:
                self.queue.appendleft(item[1])
            else:
                self.queue.append(item[1])
        else:
            self.queue.append(item)

class TelnetHandler(TelnetHandlerBase):
    "A telnet server handler using Gevent"
    def __init__(self, request, client_address, server):
        # Create a green queue for input handling
        self.cookedq = deQueue()
        # Call the base class init method
        TelnetHandlerBase.__init__(self, request, client_address, server)
        
    def setup(self):
        '''Called after instantiation'''
        TelnetHandlerBase.setup(self)
        # Spawn a greenlet to handle socket input
        self.greenlet_ic = gevent.spawn(self.inputcooker)
        # Note that inputcooker exits on EOF
        
        # Sleep for 0.5 second to allow options negotiation
        gevent.sleep(0.5)
        
    def finish(self):
        '''Called as the session is ending'''
        TelnetHandlerBase.finish(self)
        # Ensure the greenlet is dead
        self.greenlet_ic.kill()


    # -- Green input handling functions --

    def getc(self, block=True):
        """Return one character from the input queue"""
        try:
            return self.cookedq.get(block)
        except gevent.queue.Empty:
            return ''

    def ungetc(self, char, block=True):
        """Put one character back to the input queue"""
        self.cookedq.put((self.cookedq.Side.BACK, char), block)

    def inputcooker_socket_ready(self):
        """Indicate that the socket is ready to be read"""
        return gevent.select.select([self.sock.fileno()], [], [], 0) != ([], [], [])

    def inputcooker_store_queue(self, char):
        """Put the cooked data in the input queue (no locking needed)"""
        if type(char) in [type(()), type([]), type("")]:
            for v in char:
                self.cookedq.put(v)
        else:
            self.cookedq.put(char)

