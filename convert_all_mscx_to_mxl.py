import subprocess
import os

if __name__ == "__main__":
    root = "scores-modified"
    for f in os.listdir(root):
        print(f)
        path = os.path.join(root, f)
        fn, ext = os.path.splitext(f)
        if ext == ".mscx":
            subprocess.run(["/mnt/c/Program Files/MuseScore 3/bin/MuseScore3.exe", path, "-o", f"{root}/{fn}.mxl"])
            # subprocess.run(["python3", "-m", "converter21", "-f", "musicxml", "-t", "humdrum", path, f"allimages/{fn}.krn"])
