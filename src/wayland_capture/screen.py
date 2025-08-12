import subprocess
import re
from utils.get_binary_path import get_binary_path

def get_resolution():
    try:
        # Use the helper to resolve the binary path for wayland-info
        wayland_info_binary = get_binary_path("wayland-info")
        output = subprocess.run([wayland_info_binary], capture_output=True, text=True, check=True)
        match = re.search(r"width: (\d+) px, height: (\d+) px", output.stdout)
        if match:
            return match.group(1), match.group(2)
        else:
            return "Resolution not found"
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print(get_resolution())
