# import json
from threading import Thread
from queue import Queue
import time
import pickle
from typing import Any
from websocket import create_connection, WebSocketConnectionClosedException

class MessageBusClient:

    def __init__(self):
        self.stop = True
        self.error = None
        self.ws = None
        self.thread = None
        self.message_queue = Queue()
        self.url = f"ws://localhost:8888"

    def _start(self):
        """
        launch websocket listener
        """
        def _go():
            self._connect()
            self._listen()
            self._disconnect()
        self.stop = False
        self.thread = Thread(target=_go)
        self.thread.start()

    def _connect(self):
        """
        establish connection to Alpaca
        """
        self.ws = create_connection(self.url)

    def _listen(self):
        """
        check for message from websocket. handle message with on_message method
        """
        print("client listening...")
        while not self.stop:
            try:
                msg = self.ws.recv()
                # msg = json.loads(data)
            except Exception as e:
                self._on_error(e)
            else:
                self._on_message(msg)
        
        # restart this loop 
        self._listen()

    def _disconnect(self):
        """
        disconnect from websocket
        """
        try:
            if self.ws:
                print("closing websocket")
                self.ws.close()
        except WebSocketConnectionClosedException as e:
            pass

    def close(self):
        """
        disconnect and close listener thread
        """
        self.stop = True
        self._disconnect()
        self.thread.join()

    def _on_message(self, msg):
        """
        pass message data (order request) to order schema
        """
        self.message_queue.put(pickle.loads(msg))

    def _on_error(self, e, data=None):
        """
        error handling
        """
        self.stop = True
    
    def publish(self, msg):
        if self.ws:
            self.ws.send(pickle.dumps(msg))
        
    def read(self) -> Any:
        """
        blocking function call to read a message from the message bus
        """
        msg = self.message_queue.get(block=True)
        # deserialize the message
        return pickle.loads(msg)
