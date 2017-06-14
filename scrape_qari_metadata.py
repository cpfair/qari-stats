import requests
import json
import sys
import re

# We just take the regular API result and change it into a dict by "qari key."
# ...since when I was building this, "abdul_basit_murattal.wav" was more helpful than "45.wav."

qari_info = {}
qari_list = requests.get("https://quranicaudio.com/api/qaris/")
for qari_item in qari_list.json():
    qari_key = qari_item["relative_path"].split("/")[0]
    # Sometimes a recitation has some modifier attribute, eg 'taraweeh 14xx'.
    mod_match = re.search(r"(14\d\d|hidayah)", qari_item["relative_path"].partition("/")[2])
    if mod_match:
        qari_key += "_" + mod_match.group(1)
    qari_info[qari_key] = qari_item

json.dump(qari_info, sys.stdout)
