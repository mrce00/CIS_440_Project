import subprocess
import sys

import urllib.request

def download_get_pip():
    url = "https://bootstrap.pypa.io/get-pip.py"
    filename = "get-pip.py"
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
        out_file.write(response.read())
    return filename

def install_pip():
    get_pip_script = download_get_pip()
    subprocess.check_call([sys.executable, get_pip_script])

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install pip if not installed
try:
    import pip
except ImportError:
    install_pip()

# Example: Install Flask-WTF
install('Flask-WTF')