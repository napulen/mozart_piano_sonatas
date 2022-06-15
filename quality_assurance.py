import os
from pprint import pprint

import music21
from natsort import natsorted

root = "mxl"

for f in natsorted(os.listdir(root)):
    # print(f)
    path = os.path.join(root, f)
    fn, ext = os.path.splitext(f)
    fnlower = fn.lower()
    if ext == ".mxl":
        rns = {}
        print(
            f'"mps-{fnlower}": ("rawdata/mozart_piano_sonatas/mxl/{fnlower}.mxl", "rawdata/mozart_piano_sonatas/rntxt/{fnlower}.rntxt"),'
        )
        score = music21.converter.parse(path)
        repeats = [r for r in score.recurse().getElementsByClass("Repeat")]
        score.remove(repeats, recurse=True)
        prev_location = "000-0.00"
        for rn in score.recurse().getElementsByClass(
            "music21.harmony.NoChord"
        ):
            offset = float(rn.offset)
            location = f"{rn.measureNumber:03}-{offset:.2f}"
            curr_rn = rns.get(location, "")
            if location < prev_location:
                print(f"\tweird location {location} for {rn.figure}")
            if curr_rn and (curr_rn != rn.figure):
                print(f"\tcollision at {location}: {curr_rn} vs {rn.figure}")
            else:
                rns[location] = rn.figure
            prev_location = location
        # pprint(rns)
        # break
