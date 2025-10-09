from typing import MutableMapping, Any, Callable, Awaitable, TypeAlias

Scope: TypeAlias = MutableMapping[str, Any]
Message: TypeAlias = MutableMapping[str, Any]
Receive: TypeAlias = Callable[[], Awaitable[Message]]
Send: TypeAlias = Callable[[Message], Awaitable[None]]

total_connections = 0


async def handle_lifespan(scope: Scope, receive: Receive, send: Send):
    print("LIFESPAN handler started")
    while True:
        message: Message = await receive()
        print(f"LIFESPAN received: {message}")

        if message["type"] == "lifespan.startup":
            print("→ Startup event")
            await send({"type": "lifespan.startup.complete"})
        elif message["type"] == "lifespan.shutdown":
            print("→ Shutdown event")
            await send({"type": "lifespan.shutdown.complete"})
            break



async def _send_response(send: Send, status: int, body: bytes):
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            [b"content-type", b"text/plain; charset=utf-8"],
        ],
    })
    await send({
        "type": "http.response.body",
        "body": body,
        "more_body": False,
    })


async def hello_endpoint(scope: Scope, receive: Receive, send: Send):
    await _send_response(send, 200, b"Hello, world!")

async def goodbye_endpoint(scope: Scope, receive: Receive, send: Send):
    await _send_response(send, 200, b"Goodbye, world...")

async def not_found_endpoint(scope: Scope, receive: Receive, send: Send):
    await _send_response(send, 404, b"Not Found")


async def handle_http(scope: Scope, receive: Receive, send: Send):
    print(f"HTTP handler: {scope.get('method')} {scope.get('path')}")
    disconnected = False
    body_chunks: list[bytes] = []


    while True:
        message: Message = await receive()
        print(f"HTTP received: {message}")

        if message["type"] == "http.request":
            chunk = message.get("body", b"")
            if chunk:
                body_chunks.append(chunk)
            if not message.get("more_body", False):
                break

        elif message["type"] == "http.disconnect":
            print("→ Client disconnected")
            disconnected = True
            break

    if disconnected:
        return

    path = scope.get("path", "/")
    method = scope.get("method", "GET")

    if method == "GET" and path == "/hello":
        await hello_endpoint(scope, receive, send)
    elif method == "GET" and path == "/goodbye":
        await goodbye_endpoint(scope, receive, send)
    else:
        await not_found_endpoint(scope, receive, send)


async def app(scope: Scope, receive: Receive, send: Send):
    global total_connections
    total_connections += 1
    current_connection = total_connections
    print(f"Connection {current_connection}: Scope: {scope}")

    if scope["type"] == "lifespan":
        await handle_lifespan(scope, receive, send)
    elif scope["type"] == "http":
        await handle_http(scope, receive, send)

    print(f"Connection {current_connection}: Completed")


def main():
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000,
        log_level="info",
        use_colors=False,
    )


if __name__ == "__main__":
    main()
