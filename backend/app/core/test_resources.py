"""Centralized test resource management.

This module provides a centralized system for managing test resources,
particularly test images, to avoid hardcoded paths and improve test maintainability.

Usage:
    from app.core.test_resources import TestResources

    # Get path to a test image
    image_path = TestResources.get_image_path("lunch")

    # Encode image to base64
    image_base64 = TestResources.encode_image_to_base64("lunch")

    # List all available test images
    images = TestResources.list_available_images()
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import base64
import json
from dataclasses import dataclass, asdict


@dataclass
class TestImageInfo:
    """Information about a test image."""

    name: str
    path: Path
    size_kb: float
    extension: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": str(self.path),
            "size_kb": round(self.size_kb, 2),
            "extension": self.extension,
            "description": self.description,
            "exists": self.path.exists(),
        }


class TestResources:
    """Centralized management of test resources including images."""

    # Centralized paths
    TEST_ROOT = Path(__file__).parent.parent.parent / "tests"
    MEAL_IMAGES_DIR = TEST_ROOT / "mealimg"

    # Available test images with descriptions
    TEST_IMAGES = {
        "lunch": TestImageInfo(
            name="lunch",
            path=MEAL_IMAGES_DIR / "lunch.jpg",
            size_kb=0,
            extension="jpg",
            description="Sample lunch meal image",
        ),
        "meal3": TestImageInfo(
            name="meal3",
            path=MEAL_IMAGES_DIR / "meal3.png",
            size_kb=0,
            extension="png",
            description="Sample meal image 3",
        ),
        "meal4": TestImageInfo(
            name="meal4",
            path=MEAL_IMAGES_DIR / "meal4.jpg",
            size_kb=0,
            extension="jpg",
            description="Sample meal image 4",
        ),
        "meal5": TestImageInfo(
            name="meal5",
            path=MEAL_IMAGES_DIR / "meal5.jpg",
            size_kb=0,
            extension="jpg",
            description="Sample meal image 5",
        ),
        "meal6": TestImageInfo(
            name="meal6",
            path=MEAL_IMAGES_DIR / "meal6.jpg",
            size_kb=0,
            extension="jpg",
            description="Sample meal image 6",
        ),
    }

    @classmethod
    def _update_image_sizes(cls) -> None:
        """Update image sizes in TEST_IMAGES."""
        for image_info in cls.TEST_IMAGES.values():
            if image_info.path.exists():
                image_info.size_kb = image_info.path.stat().st_size / 1024

    @classmethod
    def get_image_path(cls, image_name: str) -> Path:
        """Get path to test image by name.

        Args:
            image_name: Name of the test image (e.g., "lunch", "meal3")

        Returns:
            Path object to the image file

        Raises:
            ValueError: If image_name is not recognized
            FileNotFoundError: If image file does not exist
        """
        if image_name not in cls.TEST_IMAGES:
            available = list(cls.TEST_IMAGES.keys())
            raise ValueError(
                f"Unknown test image: '{image_name}'. Available images: {available}"
            )

        image_info = cls.TEST_IMAGES[image_name]
        if not image_info.path.exists():
            raise FileNotFoundError(f"Test image file not found: {image_info.path}")

        return image_info.path

    @classmethod
    def encode_image_to_base64(cls, image_name: str) -> str:
        """Encode test image to base64 string.

        Args:
            image_name: Name of the test image

        Returns:
            Base64 encoded string of the image

        Raises:
            ValueError: If image_name is not recognized
            FileNotFoundError: If image file does not exist
            IOError: If there's an error reading the file
        """
        image_path = cls.get_image_path(image_name)

        try:
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()
                return base64.b64encode(image_bytes).decode("utf-8")
        except Exception as e:
            raise IOError(f"Failed to read image '{image_name}': {e}")

    @classmethod
    def list_available_images(cls) -> List[Dict[str, Any]]:
        """List all available test images with metadata.

        Returns:
            List of dictionaries with image information
        """
        cls._update_image_sizes()
        return [image_info.to_dict() for image_info in cls.TEST_IMAGES.values()]

    @classmethod
    def get_image_info(cls, image_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific test image.

        Args:
            image_name: Name of the test image

        Returns:
            Dictionary with image information, or None if not found
        """
        if image_name not in cls.TEST_IMAGES:
            return None

        cls._update_image_sizes()
        return cls.TEST_IMAGES[image_name].to_dict()

    @classmethod
    def validate_test_resources(cls) -> Dict[str, Any]:
        """Validate all test resources and return status.

        Returns:
            Dictionary with validation results
        """
        cls._update_image_sizes()

        validation = {
            "test_root_exists": cls.TEST_ROOT.exists(),
            "test_root_path": str(cls.TEST_ROOT),
            "meal_images_dir_exists": cls.MEAL_IMAGES_DIR.exists(),
            "meal_images_dir_path": str(cls.MEAL_IMAGES_DIR),
            "images": [],
            "summary": {
                "total_images": len(cls.TEST_IMAGES),
                "images_exist": 0,
                "images_missing": 0,
                "total_size_kb": 0,
            },
        }

        for image_info in cls.TEST_IMAGES.values():
            exists = image_info.path.exists()
            image_data = image_info.to_dict()
            image_data["exists"] = exists

            validation["images"].append(image_data)

            if exists:
                validation["summary"]["images_exist"] += 1
                validation["summary"]["total_size_kb"] += image_info.size_kb
            else:
                validation["summary"]["images_missing"] += 1

        # Overall status
        if validation["summary"]["images_missing"] == 0:
            validation["status"] = "all_resources_available"
        elif validation["summary"]["images_exist"] > 0:
            validation["status"] = "partial_resources_available"
        else:
            validation["status"] = "no_resources_available"

        return validation

    @classmethod
    def generate_resource_report(cls) -> str:
        """Generate a human-readable resource report.

        Returns:
            Formatted report string
        """
        validation = cls.validate_test_resources()

        report_lines = [
            "Test Resources Report",
            "=" * 50,
            f"Test Root: {validation['test_root_path']} ({'✓' if validation['test_root_exists'] else '✗'})",
            f"Meal Images Dir: {validation['meal_images_dir_path']} ({'✓' if validation['meal_images_dir_exists'] else '✗'})",
            "",
            "Available Test Images:",
            "-" * 30,
        ]

        for image in validation["images"]:
            status = "✓" if image["exists"] else "✗"
            report_lines.append(
                f"  {status} {image['name']:10} "
                f"{image['extension']:5} "
                f"{image['size_kb']:7.1f} KB  "
                f"{image['description']}"
            )

        report_lines.extend(
            [
                "",
                "Summary:",
                "-" * 30,
                f"  Total Images: {validation['summary']['total_images']}",
                f"  Available: {validation['summary']['images_exist']}",
                f"  Missing: {validation['summary']['images_missing']}",
                f"  Total Size: {validation['summary']['total_size_kb']:.1f} KB",
                "",
                f"Status: {validation['status']}",
                "=" * 50,
            ]
        )

        return "\n".join(report_lines)


# Convenience functions for common operations
def get_test_image_base64(image_name: str = "lunch") -> str:
    """Get base64 encoded test image (defaults to 'lunch').

    Args:
        image_name: Name of the test image

    Returns:
        Base64 encoded string
    """
    return TestResources.encode_image_to_base64(image_name)


def list_test_images() -> List[Dict[str, Any]]:
    """List all test images.

    Returns:
        List of image information dictionaries
    """
    return TestResources.list_available_images()


if __name__ == "__main__":
    # Test the test resource management
    print("Test Resource Management System")
    print("=" * 50)

    # Generate and print report
    report = TestResources.generate_resource_report()
    print(report)

    # Test specific operations
    print("\nTest Operations:")
    print("-" * 30)

    try:
        # Test getting image path
        lunch_path = TestResources.get_image_path("lunch")
        print(f"✓ Lunch image path: {lunch_path}")

        # Test listing images
        images = TestResources.list_available_images()
        print(f"✓ Found {len(images)} test images")

        # Test validation
        validation = TestResources.validate_test_resources()
        print(f"✓ Validation status: {validation['status']}")

    except Exception as e:
        print(f"✗ Error during testing: {e}")
