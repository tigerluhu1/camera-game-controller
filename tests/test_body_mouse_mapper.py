from app.body_mouse_mapper import BodyMouseMapper


def test_mapper_computes_offset_based_on_shoulder_anchor():
    mapper = BodyMouseMapper(anchor="shoulders")
    landmarks = {"left_shoulder": (0.2, 0.5), "right_shoulder": (0.4, 0.5)}

    delta = mapper.compute_mouse_delta(landmarks, frame_size=(640, 480))

    assert delta != (0, 0)


def test_mapper_uses_head_anchor_when_selected():
    mapper = BodyMouseMapper(anchor="head")
    landmarks = {"nose": (0.75, 0.3)}

    delta = mapper.compute_mouse_delta(landmarks, frame_size=(640, 480))

    assert delta[0] > 0
    assert delta[1] < 0
