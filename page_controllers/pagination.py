from math import ceil, floor

from .page_controller import ABCMeta, PageController, Rectangle, abstractmethod, sleep


class Pagination(PageController, metaclass=ABCMeta):
    """ページネーションを保持するページを操作するクラス"""

    def __init__(self, contents_count: int):
        self.CONTENTS_PER_PAGE = 10
        self.CONTENTS_COUNT = contents_count
        self.PAGE_COUNT = ceil(contents_count / self.CONTENTS_PER_PAGE)
        self.current_page_index = 0

    @abstractmethod
    def page_button(self, index_from_left: int) -> Rectangle:
        """左からindex番目のページを選択するためボタンを返す"""
        pass

    async def click_page(self, index_from_left: int):
        """左からindex番目のページをクリックする"""
        await self.click(self.page_button(index_from_left))

    async def move_page(self, content_index: int):
        """指定インデックスのコンテンツを選択できるページへ遷移する"""
        index_of_current_pages_first_content = (
            self.current_page_index * self.CONTENTS_PER_PAGE
        )

        # 現在開いているページ内に該当コンテンツが存在する場合はブレイク
        if (
            index_of_current_pages_first_content <= content_index
            and content_index
            < index_of_current_pages_first_content + self.CONTENTS_PER_PAGE
        ):
            return

        # コンテンツが存在するページを選択する
        target_page_index = floor(content_index / self.CONTENTS_PER_PAGE)
        while self.current_page_index != target_page_index:
            # 選択中のページが左から何番目に表示されているかを調べる

            index_from_left = None
            if self.current_page_index < 2:
                index_from_left = self.current_page_index
            elif self.current_page_index > self.PAGE_COUNT - 3:
                index_from_left = 5 - (self.PAGE_COUNT - self.current_page_index)
            else:
                index_from_left = 2

            if self.current_page_index < target_page_index:
                # 右に進む場合
                if target_page_index - self.current_page_index <= 4 - index_from_left:
                    # 直接選択できる場合
                    await self.click_page(
                        index_from_left=target_page_index
                        - self.current_page_index
                        + index_from_left
                    )
                    return

                # 直接選択できない場合
                self.click_page(index_from_left=5)
                self.current_page_index += 4 - index_from_left
            else:
                # 左に戻る場合
                if self.current_page_index - target_page_index <= index_from_left:
                    # 直接選択できる場合
                    await self.click_page(
                        index_from_left=index_from_left
                        - (self.current_page_index - target_page_index)
                    )
                    return

                # 直接選択できない場合
                self.click_page(index_from_left=0)
                self.current_page_index -= index_from_left

            await sleep(1)
