"""
File validation service.
Validates uploaded documents for type (PDF, JPG, PNG) and size (≤5MB).
"""
import os

# Maximum file size: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5,242,880 bytes

# Allowed file extensions (lowercase)
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
}


class FileValidationError(Exception):
    """Raised when a file fails validation."""
    pass


class FileValidator:
    """
    Validates uploaded files for:
    1. File extension (PDF, JPG, JPEG, PNG)
    2. File size (≤ 5MB)
    3. MIME type via content sniffing (when python-magic is available)
    """

    @classmethod
    def validate(cls, uploaded_file):
        """
        Validate an uploaded file.

        Args:
            uploaded_file: Django UploadedFile instance.

        Raises:
            FileValidationError: If validation fails.
        """
        cls._validate_extension(uploaded_file.name)
        cls._validate_size(uploaded_file.size)
        cls._validate_mime_type(uploaded_file)

    @classmethod
    def _validate_extension(cls, filename):
        """Check file extension against whitelist."""
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise FileValidationError(
                f"File type '{ext}' is not allowed. "
                f"Accepted types: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
            )

    @classmethod
    def _validate_size(cls, file_size):
        """Check file does not exceed maximum size."""
        if file_size > MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            raise FileValidationError(
                f"File size ({size_mb:.1f}MB) exceeds the maximum allowed size of 5MB."
            )

    @classmethod
    def _validate_mime_type(cls, uploaded_file):
        """
        Validate MIME type by reading file content.
        Falls back gracefully if python-magic is not installed.
        """
        try:
            import magic
            # Read first 2048 bytes for MIME detection
            uploaded_file.seek(0)
            file_header = uploaded_file.read(2048)
            uploaded_file.seek(0)  # Reset file pointer

            mime_type = magic.from_buffer(file_header, mime=True)
            if mime_type not in ALLOWED_MIME_TYPES:
                raise FileValidationError(
                    f"File content type '{mime_type}' is not allowed. "
                    f"Accepted types: PDF, JPG, PNG."
                )
        except ImportError:
            # python-magic not installed — skip MIME sniffing.
            # Extension validation still protects against basic attacks.
            pass
