from PIL import ImageGrab
import os
import time

# brief delay to ensure UI is ready
time.sleep(0.5)

out_dir = os.path.join(os.path.dirname(__file__), '..', 'screenshots')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.abspath(os.path.join(out_dir, 'dashboard_snapshot.png'))

img = ImageGrab.grab()
img.save(out_path)
print(out_path)
