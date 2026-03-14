from __future__ import annotations

from PIL import Image, ImageDraw

from app.detection import LandmarkPoint


CONNECTIONS = [
    ("nose", "hip_center"),
    ("left_shoulder", "left_wrist"),
    ("right_shoulder", "right_wrist"),
]


def render_preview_frame(
    frame,
    landmarks: dict[str, LandmarkPoint],
    actions: set[str],
) -> Image.Image:
    image = Image.fromarray(frame[:, :, ::-1])
    draw = ImageDraw.Draw(image)
    width, height = image.size

    for start_name, end_name in CONNECTIONS:
        start = landmarks.get(start_name)
        end = landmarks.get(end_name)
        if start is None or end is None:
            continue
        draw.line(
            (
                start.x * width,
                start.y * height,
                end.x * width,
                end.y * height,
            ),
            fill=(0, 255, 0),
            width=2,
        )

    for point in landmarks.values():
        x = point.x * width
        y = point.y * height
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 0, 0))

    if actions:
        draw.text((8, 8), ", ".join(sorted(actions)), fill=(255, 255, 0))

    return image
