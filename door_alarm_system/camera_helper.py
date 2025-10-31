"""
Camera Helper Module for eDOMOS Door Alarm System
Supports both USB webcams and Raspberry Pi Camera Module
Auto-detects available camera and provides graceful fallback
"""

import os
import cv2
import hashlib
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CameraManager:
    """
    Unified camera manager supporting USB webcam and Pi Camera
    """
    
    def __init__(self, config=None):
        """
        Initialize camera manager
        
        Args:
            config: Dictionary with camera configuration
                {
                    'enabled': True/False,
                    'required': True/False,
                    'type': 'usb' or 'picamera',
                    'device_index': 0 (for USB),
                    'resolution': (1920, 1080),
                    'quality': 85,
                    'storage_path': 'static/captures',
                    'auto_detect': True
                }
        """
        self.config = config or {}
        self.camera = None
        self.camera_available = False
        self.camera_type = None
        
        # Default configuration
        self.enabled = self.config.get('enabled', True)
        self.required = self.config.get('required', False)
        self.type = self.config.get('type', 'usb')
        self.device_index = self.config.get('device_index', 0)
        self.resolution = self.config.get('resolution', (1920, 1080))
        self.quality = self.config.get('quality', 85)
        self.storage_path = self.config.get('storage_path', 'static/captures')
        self.auto_detect = self.config.get('auto_detect', True)
        
        # Ensure storage directory exists
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize camera if enabled
        if self.enabled:
            self.initialize_camera()
    
    def initialize_camera(self):
        """Initialize camera based on type and availability"""
        try:
            if self.type == 'usb':
                self._initialize_usb_camera()
            elif self.type == 'picamera':
                self._initialize_pi_camera()
            else:
                logger.warning(f"Unknown camera type: {self.type}")
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            if self.required:
                raise
            else:
                logger.info("Continuing without camera (non-critical)")
    
    def _initialize_usb_camera(self):
        """Initialize USB webcam using OpenCV"""
        try:
            logger.info(f"Attempting to initialize USB camera on device {self.device_index}")
            
            # Try to open camera
            self.camera = cv2.VideoCapture(self.device_index)
            
            if not self.camera.isOpened():
                logger.warning(f"USB camera {self.device_index} not available")
                self.camera = None
                self.camera_available = False
                return
            
            # Set resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
            # Test capture
            ret, frame = self.camera.read()
            if ret:
                self.camera_available = True
                self.camera_type = 'usb'
                logger.info(f"✅ USB camera initialized successfully at {self.resolution}")
            else:
                logger.warning("USB camera opened but cannot capture frames")
                self.camera.release()
                self.camera = None
                self.camera_available = False
                
        except Exception as e:
            logger.error(f"USB camera initialization error: {e}")
            self.camera_available = False
            self.camera = None
    
    def _initialize_pi_camera(self):
        """Initialize Raspberry Pi Camera Module using picamera2"""
        try:
            logger.info("Attempting to initialize Pi Camera Module")
            
            # Import picamera2 (only when needed)
            from picamera2 import Picamera2
            
            self.camera = Picamera2()
            
            # Configure camera
            camera_config = self.camera.create_still_configuration(
                main={"size": self.resolution}
            )
            self.camera.configure(camera_config)
            self.camera.start()
            
            self.camera_available = True
            self.camera_type = 'picamera'
            logger.info(f"✅ Pi Camera initialized successfully at {self.resolution}")
            
        except ImportError:
            logger.warning("picamera2 library not installed. Install with: pip install picamera2")
            self.camera_available = False
        except Exception as e:
            logger.error(f"Pi Camera initialization error: {e}")
            self.camera_available = False
            self.camera = None
    
    def capture_image(self, event_type="door_event", event_id=None):
        """
        Capture an image from the camera
        
        Args:
            event_type: Type of event (for filename)
            event_id: Optional event ID
            
        Returns:
            Dictionary with capture info or None if failed
            {
                'success': True/False,
                'filename': 'door_open_2025-10-29_17-30-45.jpg',
                'path': 'static/captures/door_open_2025-10-29_17-30-45.jpg',
                'hash': 'sha256_hash',
                'timestamp': datetime object,
                'size_bytes': 12345,
                'resolution': (1920, 1080)
            }
        """
        if not self.enabled:
            logger.debug("Camera disabled in configuration")
            return None
        
        if not self.camera_available:
            logger.debug("Camera not available, skipping capture")
            return None
        
        try:
            # Generate filename with timestamp
            timestamp = datetime.now()
            timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{event_type}_{timestamp_str}.jpg"
            filepath = os.path.join(self.storage_path, filename)
            
            # Capture based on camera type
            if self.camera_type == 'usb':
                success = self._capture_usb_image(filepath)
            elif self.camera_type == 'picamera':
                success = self._capture_pi_image(filepath)
            else:
                logger.error("Unknown camera type")
                return None
            
            if not success:
                return None
            
            # Calculate file hash for blockchain verification
            file_hash = self._calculate_file_hash(filepath)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            logger.info(f"📸 Image captured: {filename} ({file_size} bytes)")
            
            return {
                'success': True,
                'filename': filename,
                'path': filepath,
                'hash': file_hash,
                'timestamp': timestamp,
                'size_bytes': file_size,
                'resolution': self.resolution
            }
            
        except Exception as e:
            logger.error(f"Image capture failed: {e}")
            return None
    
    def _capture_usb_image(self, filepath):
        """Capture image from USB webcam"""
        try:
            # CRITICAL: Clear buffer by reading and discarding old frames
            # USB webcams buffer multiple frames, so we need to flush the buffer
            # to get the most recent frame
            logger.info("📸 Flushing camera buffer to get fresh frame...")
            for i in range(5):  # Read and discard 5 buffered frames
                ret, frame = self.camera.read()
                if not ret:
                    logger.warning(f"Failed to read buffer frame {i+1}/5")
            
            # Now capture the fresh frame
            ret, frame = self.camera.read()
            
            if not ret or frame is None:
                logger.error("Failed to capture frame from USB camera")
                return False
            
            logger.info(f"✅ Fresh frame captured, saving to {filepath}")
            
            # Save image with quality setting
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
            
            return True
            
        except Exception as e:
            logger.error(f"USB camera capture error: {e}")
            return False
    
    def _capture_pi_image(self, filepath):
        """Capture image from Pi Camera"""
        try:
            # Capture to file
            self.camera.capture_file(filepath)
            return True
            
        except Exception as e:
            logger.error(f"Pi Camera capture error: {e}")
            return False
    
    def _calculate_file_hash(self, filepath):
        """Calculate SHA-256 hash of image file for verification"""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Hash calculation error: {e}")
            return None
    
    def test_camera(self):
        """Test camera capture and return test image info"""
        logger.info("Testing camera capture...")
        result = self.capture_image(event_type="camera_test")
        
        if result and result['success']:
            logger.info(f"✅ Camera test successful!")
            logger.info(f"   File: {result['filename']}")
            logger.info(f"   Size: {result['size_bytes']} bytes")
            logger.info(f"   Hash: {result['hash'][:16]}...")
            return True
        else:
            logger.warning("❌ Camera test failed")
            return False
    
    def get_status(self):
        """Get camera status information"""
        return {
            'enabled': self.enabled,
            'available': self.camera_available,
            'type': self.camera_type,
            'resolution': self.resolution,
            'quality': self.quality,
            'storage_path': self.storage_path
        }
    
    def cleanup_old_images(self, days=90):
        """
        Delete images older than specified days
        
        Args:
            days: Number of days to retain images
            
        Returns:
            Number of files deleted
        """
        try:
            import time
            
            logger.info(f"Cleaning up images older than {days} days...")
            
            storage_dir = Path(self.storage_path)
            if not storage_dir.exists():
                return 0
            
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            deleted_count = 0
            for image_file in storage_dir.glob("*.jpg"):
                file_time = image_file.stat().st_mtime
                if file_time < cutoff_time:
                    image_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old image: {image_file.name}")
            
            if deleted_count > 0:
                logger.info(f"🗑️ Deleted {deleted_count} old images")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Image cleanup error: {e}")
            return 0
    
    def close(self):
        """Release camera resources"""
        if self.camera:
            try:
                if self.camera_type == 'usb':
                    self.camera.release()
                elif self.camera_type == 'picamera':
                    self.camera.stop()
                logger.info("Camera released")
            except Exception as e:
                logger.error(f"Error releasing camera: {e}")
            finally:
                self.camera = None
                self.camera_available = False


# Global camera manager instance (initialized later with config)
camera_manager = None

def initialize_camera_manager(config):
    """Initialize global camera manager"""
    global camera_manager
    camera_manager = CameraManager(config)
    return camera_manager

def get_camera_manager():
    """Get global camera manager instance"""
    return camera_manager

def capture_event_image(event_type, event_id=None):
    """
    Convenience function to capture image for an event
    
    Args:
        event_type: Type of event (door_open, door_close, etc.)
        event_id: Optional event ID
        
    Returns:
        Capture result dictionary or None
    """
    if camera_manager:
        return camera_manager.capture_image(event_type, event_id)
    return None


if __name__ == "__main__":
    # Test the camera module
    print("=" * 60)
    print("eDOMOS Camera Module Test")
    print("=" * 60)
    
    # Test with USB camera configuration
    test_config = {
        'enabled': True,
        'required': False,
        'type': 'usb',  # Change to 'picamera' for Pi Camera
        'device_index': 0,
        'resolution': (1280, 720),
        'quality': 85,
        'storage_path': 'static/captures',
        'auto_detect': True
    }
    
    cam = CameraManager(test_config)
    
    print("\nCamera Status:")
    status = cam.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if cam.camera_available:
        print("\nTesting image capture...")
        cam.test_camera()
    else:
        print("\n⚠️  No camera detected. This is OK - system will work without camera.")
        print("   Plug in USB webcam or connect Pi Camera and restart to enable.")
    
    cam.close()
    print("\nTest complete!")
