def calc_page_select_process(
    current_page: int,
    page_number: int,
    max_page: int,
):
    """対象ページまでに選択すべきボタン(左から何番目か)を算出する
    Args:
        page_number (int): ページ番号(1スタート)
    """
    answer: list[int] = []

    while current_page != page_number:
        # まずは選択中のページが左から何番目かを調べる
        from_the_left = None  # 1スタート
        if current_page < 3:
            from_the_left = current_page
        elif current_page > max_page - 2:
            from_the_left = 5 - (max_page - current_page)
        else:
            from_the_left = 3

        if current_page < page_number:
            # 右に進む場合
            if page_number - current_page <= 5 - from_the_left:
                # 直接選択できる場合
                answer.append(page_number - current_page + from_the_left)
                current_page = page_number
            else:
                # 直接選択できない場合
                answer.append(5)
                current_page += 5 - from_the_left
        else:
            # 左に戻る場合
            if current_page - page_number <= from_the_left - 1:
                # 直接選択できる場合
                answer.append(from_the_left - (current_page - page_number))
                current_page = page_number
            else:
                # 直接選択できない場合
                answer.append(1)
                current_page -= from_the_left - 1

    return answer
