import magic
from preview_generator.manager import PreviewManager

cache_path = "/tmp/preview_cache"

class MetaService:
    def __init__(self):
        self.manager = PreviewManager(cache_path, create_folder=True)
        self.mime = magic.Magic(mime=True)

    def get_file_mimetype(self, file_path: str) -> str:
        return self.mime.from_file(file_path)

    def get_description(self, file_path: str) -> str:
        if self.manager.has_text_preview(file_path):
            return self.manager.get_text_preview(file_path)
        return ""


meta_service = MetaService()