"""Face detection.

Real OpenCV Haar-cascade detector when opencv-python is installed;
deterministic mock detector for the simulated demo otherwise.
"""

from __future__ import annotations

from typing import List, Protocol

import numpy as np

from .schemas import FaceBox

try:
    import cv2  # type: ignore

    _CV2_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on local environment
    cv2 = None  # type: ignore
    _CV2_AVAILABLE = False


class FaceDetector(Protocol):
    def detect(self, frame: np.ndarray) -> List[FaceBox]:
        """Return face bounding boxes found in a BGR frame."""
        ...


class HaarFaceDetector:
    """Real face detector using OpenCV's bundled Haar cascade.

    Works out of the box with `pip install opencv-python` -- no model
    download needed.
    """

    def __init__(self, scale_factor: float = 1.1, min_neighbors: int = 5) -> None:
        if not _CV2_AVAILABLE:
            raise RuntimeError(
                "opencv-python is not installed. Run `pip install -r requirements.txt` "
                "or use MockFaceDetector for the simulated demo."
            )
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._cascade = cv2.CascadeClassifier(cascade_path)
        if self._cascade.empty():
            raise RuntimeError(f"Could not load Haar cascade from {cascade_path}")
        self._scale_factor = scale_factor
        self._min_neighbors = min_neighbors

    def detect(self, frame: np.ndarray) -> List[FaceBox]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._cascade.detectMultiScale(
            gray,
            scaleFactor=self._scale_factor,
            minNeighbors=self._min_neighbors,
        )
        return [FaceBox(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]


class MockFaceDetector:
    """Deterministic mock detector for the simulated demo.

    Returns a single centered face box per frame. Demo only -- clearly
    separated from the real detector so production code never
    accidentally depends on it.
    """

    def __init__(self, box_size: int = 96) -> None:
        self._box_size = box_size

    def detect(self, frame: np.ndarray) -> List[FaceBox]:
        h, w = frame.shape[:2]
        s = min(self._box_size, h, w)
        return [FaceBox((w - s) // 2, (h - s) // 2, s, s)]
