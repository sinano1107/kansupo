from expedition_manage_thread import ExpeditionManageThread


def test_save_and_load():
    # 生成時はend_timeがNoneであることを確認
    expedition_manage_thread = ExpeditionManageThread(None)
    assert expedition_manage_thread.end_time == None

    # set_end_timeでend_timeが設定されることを確認
    expedition_manage_thread.set_end_time(15)
    assert expedition_manage_thread.end_time != None

    # saveでend_timeが保存されることを確認
    prev_load_end_time = expedition_manage_thread.end_time
    expedition_manage_thread.save()
    with open("save_data/expedition_end_time.txt", "r") as f:
        assert f.read() != ""

    # 読み込みのためにリセット
    expedition_manage_thread.end_time = None
    assert expedition_manage_thread.end_time == None

    # loadでend_timeが読み込まれることを確認
    expedition_manage_thread.load()
    expedition_manage_thread.end_time == prev_load_end_time

    # load後はsave_dataが空になることを確認
    with open("save_data/expedition_end_time.txt", "r") as f:
        assert f.read() == ""

    pass
