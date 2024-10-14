import magic
import textract
import chardet


class MetaService:
    def __init__(self):
        self.mime = magic.Magic(mime=True)

    def get_file_mimetype(self, file_path: str) -> str:
        return self.mime.from_file(file_path)

    def extract_content(self, file_path: str) -> str:
        try:
            # First, try to extract content using textract
            content = textract.process(file_path)

            # Detect the encoding of the extracted content
            detected = chardet.detect(content)
            encoding = detected["encoding"] if detected["encoding"] else "utf-8"

            # Decode the content using the detected encoding
            return content.decode(encoding, errors="replace")
        except Exception as e:
            print(f"Error extracting content: {str(e)}")

            # If textract fails, try to read the file directly
            try:
                with open(file_path, "rb") as file:
                    content = file.read()
                    detected = chardet.detect(content)
                    encoding = detected["encoding"] if detected["encoding"] else "utf-8"
                    return content.decode(encoding, errors="replace")
            except Exception as e:
                print(f"Error reading file directly: {str(e)}")
                return ""


meta_service = MetaService()
