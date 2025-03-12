import asyncio
from fastapi import FastAPI
import uvicorn
import yaml

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
    with open("log_config.yaml") as f:
        log_config = yaml.safe_load(f)

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=log_config,
        use_colors=True,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main(headless: bool, number_of_retries: int):
    # 別タスクでFastAPIサーバーを起動する
    asyncio.create_task(run_server())

    # 艦サポを実行する
    kansupo.start()
    await kansupo.run(headless=headless, number_of_retries=number_of_retries)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--number_of_retries", type=int, default=3)
    args = parser.parse_args()

    asyncio.run(main(headless=args.headless, number_of_retries=args.number_of_retries))
