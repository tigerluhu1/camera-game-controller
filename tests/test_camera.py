from app.camera import CameraStatus


def test_camera_status_defaults_to_stopped():
    status = CameraStatus()

    assert status.running is False
    assert status.last_error == ""


def test_camera_status_marks_running():
    status = CameraStatus(running=True, frame_size=(640, 480))

    assert status.running is True
    assert status.frame_size == (640, 480)


def test_camera_open_uses_backend_factory():
    class FakeCapture:
        def isOpened(self):
            return True

    from app.camera import Camera

    camera = Camera(backend_factory=lambda index: FakeCapture())
    status = camera.open()

    assert status.running is True


def test_camera_open_sets_error_when_backend_unavailable():
    from app.camera import Camera

    camera = Camera(backend_factory=lambda index: None)
    status = camera.open()

    assert status.running is False
    assert status.last_error != ""
