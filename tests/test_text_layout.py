from video.text_layout import adaptive_font_size, prepare_display_text, wrap_text


def test_short_text_keeps_size():
    text, size = prepare_display_text("答案：12小时")
    assert text == "答案：12小时"
    assert size == 48


def test_long_text_wraps_and_shrinks():
    text, size = prepare_display_text("这是一个比较长的数学题目，需要自动换行避免文字超出竖屏画布")
    assert "\n" in text
    assert size < 48


def test_wrap_text_limits_lines():
    text = wrap_text("abcdefghijklmnopqrstuvwxyz", max_chars=5)
    assert len(text.split("\n")) <= 4
    assert all(len(line) <= 5 for line in text.split("\n"))
