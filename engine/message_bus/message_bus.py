import asyncio
from typing import Any

class MessageBus:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

    async def _handle_connection(self, reader: Any, writer: Any) -> None:
        while True:
            data = await reader.readline()
            if not data:
                break
            message = data.decode().strip()
            print("Received message:", message)
            response = "Echoing message: " + message
            writer.write(response.encode())
            await writer.drain()

    async def _start_server(self) -> None:
        server = await asyncio.start_server(self._handle_connection, self._host, self._port)
        async with server:
            await server.serve_forever()

    async def _send_message(self) -> None:
        reader, writer = await asyncio.open_connection(self._host, self._port)
        message = "Hello, world!"
        writer.write(message.encode())
        await writer.drain()
        response = await reader.readline()
        print("Received response:", response.decode().strip())

    async def _main(self) -> None:
        asyncio.create_task(self._start_server())
        # asyncio.create_task(self._send_message())
        # await asyncio.sleep(1)

    def start(self) -> None:
        asyncio.run(self._main())
