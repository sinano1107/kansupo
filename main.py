import asyncio
from fastapi import FastAPI
import uvicorn
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed

from kansupo import KanSupo

app = FastAPI()
kansupo = KanSupo()


@app.post("/start")
def start():
    return kansupo.start()


@app.post("/stop")
def stop():
    return kansupo.stop()


async def run_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()


async def main(headless: bool):
    # 別タスクでFastAPIサーバーを起動する
    asyncio.create_task(run_server())
    await kansupo.run(headless=headless)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--retry_count", type=int, default=1)
    args = parser.parse_args()

    retryer = AsyncRetrying(
        stop=stop_after_attempt(args.retry_count), wait=wait_fixed(1), reraise=True
    )
    asyncio.run(retryer(main, args.headless))
