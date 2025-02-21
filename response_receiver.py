import asyncio
from playwright.async_api import Response

from typing import Coroutine, Dict
from address import Address


class ResponseReceiver:
    # 待機中のURLをキーとして、レスポンスを格納する辞書
    expecting_url_to_response_map: Dict[str, Response] = {}

    @classmethod
    def handle(cls, response: Response):
        """レスポンスを受け取った時のハンドラ"""
        if response.url in cls.expecting_url_to_response_map.keys():
            # レスポンスを待機しているURLの場合は、レスポンスを格納する
            cls.expecting_url_to_response_map[response.url] = response

    @classmethod
    def expect(cls, address: Address | str) -> Coroutine[None, None, Response]:
        """特定のURLからのレスポンスを受け取るまで待機するコルーチンを生成する"""
        if type(address) is Address:
            # Addressオブジェクトの場合は、URLを取得する
            url = address.value
        else:
            # 文字列の場合は、そのままURLとして扱う
            url = address

        # レスポンスを待機するためのフラグを立てる
        cls.expecting_url_to_response_map[url] = None

        async def wait_for_response():
            """レスポンスを受け取るまで待機する"""
            while cls.expecting_url_to_response_map[url] is None:
                await asyncio.sleep(0.1)
            return cls.expecting_url_to_response_map.pop(url)

        # コルーチンを返す
        return wait_for_response
