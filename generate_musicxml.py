import subprocess
import os

museScoreBinary = "musescore-portable"

for root, folders, files in os.walk("scores"):
    for f in files:
        input_path = os.path.join(root, f)
        # root, extension = os.path.splitext(score)
        if f.endswith(".mscx"):
            destination = f.replace(".mscx", ".mxl")
            dest_path = os.path.join(root, destination)
            subprocess.run([museScoreBinary, input_path, "-o", dest_path])
