from video.short_video_plan import plan_short_video


def test_short_video_plan_is_bounded():
    plan = plan_short_video("工程问题", 40)
    assert plan.duration == 40
    assert plan.segments[0].key == "hook"
    assert plan.segments[-1].end == 40
    assert all(segment.end > segment.start for segment in plan.segments)


def test_arithmetic_is_faster():
    arithmetic = plan_short_video("四则运算", 40)
    engineering = plan_short_video("工程问题", 40)
    arithmetic_explain = arithmetic.segments[1].end - arithmetic.segments[1].start
    engineering_explain = engineering.segments[1].end - engineering.segments[1].start
    assert arithmetic_explain < engineering_explain
