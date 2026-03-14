from app.camera import CameraStatus


def test_camera_status_defaults_to_stopped():
    status = CameraStatus()

    assert status.running is False
    assert status.last_error == ""


def test_camera_status_marks_running():
    status = CameraStatus(running=True, frame_size=(640, 480))

    assert status.running is True
    assert status.frame_size == (640, 480)
