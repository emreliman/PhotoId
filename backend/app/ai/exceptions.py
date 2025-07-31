
class PhotoProcessingError(Exception):
    """Base exception for all photo processing errors."""
    pass

class FaceNotFoundError(PhotoProcessingError):
    """Raised when no face is detected in the image."""
    pass

class MultipleFacesError(PhotoProcessingError):
    """Raised when multiple faces are detected in the image."""
    pass

class ImageReadError(PhotoProcessingError):
    """Raised when the image file cannot be read or is corrupted."""
    pass
