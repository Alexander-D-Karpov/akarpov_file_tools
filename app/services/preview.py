import io
import magic
from math import ceil

import ffmpeg
from PIL import Image, ImageDraw, ImageFont
from preview_generator.manager import PreviewManager

cache_path = "/tmp/preview_cache"
PIL_GRAYSCALE = "L"
PIL_WIDTH_INDEX = 0
PIL_HEIGHT_INDEX = 1
COMMON_MONO_FONT_FILENAMES = [
    "DejaVuSansMono.ttf",
    "Consolas Mono.ttf",
    "Consola.ttf",
]


class PreviewService:
    def __init__(self):
        self.manager = PreviewManager(cache_path, create_folder=True)

    def get_mime_type(self, file_path: str) -> str:
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)

    def create_preview(self, file_path: str) -> bytes:
        if self.manager.has_jpeg_preview(file_path):
            preview_path = self.manager.get_jpeg_preview(file_path, height=500)
            with open(preview_path, "rb") as f:
                return f.read()
        # If we can't get a regular preview, try to create a text-based image
        return self.textfile_to_image(file_path)

    def create_video_preview(self, file_path: str) -> bytes:
        output = io.BytesIO()
        try:
            (
                ffmpeg.input(file_path, ss="00:00:01")  # seek to 1 second
                .filter("scale", 500, -1)  # scale width to 500px, keep aspect ratio
                .output("pipe:", format="rawvideo", pix_fmt="rgb24", vframes=1)
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output.getvalue()
        except ffmpeg.Error as e:
            print(f"Error creating video preview: {e.stderr.decode()}")
            return b""

    def textfile_to_image(self, file_path: str) -> bytes:
        # Parse the file into lines stripped of whitespace on the right side
        with open(file_path, "r", errors="ignore") as f:
            lines = tuple(
                line.rstrip() for line in f.readlines()[:30]
            )  # Limit to first 30 lines

        font = None
        large_font = 20  # get better resolution with larger size
        for font_filename in COMMON_MONO_FONT_FILENAMES:
            try:
                font = ImageFont.truetype(font_filename, size=large_font)
                print(f'Using font "{font_filename}".')
                break
            except OSError:
                print(f'Could not load font "{font_filename}".')
        if font is None:
            font = ImageFont.load_default()
            print("Using default font.")

        def font_points_to_pixels(pt):
            return round(pt * 96.0 / 72)

        margin_pixels = 20

        # Calculate image size
        max_line_height = font_points_to_pixels(font.getbbox(lines[0])[3])
        realistic_line_height = max_line_height * 1.2
        image_height = int(realistic_line_height * len(lines) + 2 * margin_pixels)

        max_line_width = max(
            font_points_to_pixels(font.getbbox(line)[2]) for line in lines
        )
        image_width = int(max_line_width + (2 * margin_pixels))

        # Create the image
        background_color = 255  # white
        image = Image.new(
            PIL_GRAYSCALE, (image_width, image_height), color=background_color
        )
        draw = ImageDraw.Draw(image)

        # Draw the text
        font_color = 0  # black
        horizontal_position = margin_pixels
        for i, line in enumerate(lines):
            vertical_position = int(margin_pixels + (i * realistic_line_height))
            draw.text(
                (horizontal_position, vertical_position),
                line,
                fill=font_color,
                font=font,
            )

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG")
        return img_byte_arr.getvalue()


preview_service = PreviewService()
