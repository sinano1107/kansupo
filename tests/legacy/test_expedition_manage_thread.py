from legacy.expedition_manage_thread import ExpeditionManageThread


def test_save_and_load():
    # テスト前にファイルが空であることを確認
    try:
        with open(ExpeditionManageThread.SAVE_DATA_PATH, "r") as f:
            assert f.read() == ""
    except FileNotFoundError:
        print("ファイルが存在しない")

    # 生成時はexpeditioning_dataがNoneであることを確認
    expedition_manage_thread = ExpeditionManageThread(None)
    assert expedition_manage_thread.expeditioning_data == None

    # start_waitでexpeditioning_dataが設定されることを確認
    expedition_manage_thread.start_wait("test", 15)
    assert expedition_manage_thread.expeditioning_data != None
    assert expedition_manage_thread.expeditioning_data.name == "test"

    # saveでend_timeが保存されることを確認
    prev_data = expedition_manage_thread.expeditioning_data
    expedition_manage_thread.save()
    with open(ExpeditionManageThread.SAVE_DATA_PATH, "r") as f:
        assert f.read() != ""

    # 読み込みのためにリセット
    expedition_manage_thread.expeditioning_data = None
    assert expedition_manage_thread.expeditioning_data == None

    # loadでend_timeが読み込まれることを確認
    expedition_manage_thread.load()
    expedition_manage_thread.expeditioning_data == prev_data

    # load後はsave_dataが空になることを確認
    with open(ExpeditionManageThread.SAVE_DATA_PATH, "r") as f:
        assert f.read() == ""
