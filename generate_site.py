from __future__ import division
import json
import math
import sys
import htmlmin

template = """
<html>
<head>
    <link href="site.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=EB+Garamond" rel="stylesheet">
    <script type="text/javascript" src="app.js"></script>
    <script src="https://use.fontawesome.com/8a3e800a96.js"></script>
    <meta name="viewport" content="width=device-width">
    <meta name="viewport" content="initial-scale=1.0">
    <meta name="description" content="Sort Qur'an reciters by reading speed and voice pitch. Find qaris with low (or high) voices, or with slow (or fast) recitations.">
    <title>Qari Stats - Find Qur'an reciters by reading speed and voice pitch</title>
</head>
<body>
<div class="container content-sizing">
    <div class="item header"><div class="content-sizing">
        <div class="speed" id="sort-speed">
            &larr; Speed
            <i id="sort-speed-icon" class="fa fa-sort-asc sort-icon"></i>
        </div>
        <div class="controls"><h1>Qari Stats</h1></div>
        <div class="register" id="sort-register">
            <i class="fa fa-sort sort-icon" id="sort-register-icon"></i>
            Pitch &rarr;
        </div>
    </div></div>
    <div class="item header-clear">&nbsp;</div>
    <div id="qari-list">
        {items}
    </div>
    <div class="footer">
        Recitations from <a href="https://quranicaudio.com">QuranicAudio.com</a>
        &nbsp;&bull;&nbsp;
        <a href="https://github.com/cpfair/qari-stats">GitHub</a>
    </div>
</div>
<script type="text/javascript">var qari_stats = {qari_stats};</script>
</body>
</html>
"""

# We don't output items with these in their qari_keys.
blacklist = (
    "makkah_",
    "madinah_",
    "_w_",
    "_with_",
    "_and_",
)

if len(sys.argv) < 3:
    sys.stderr.write("%s qari_metadata.json qari_stats.json\n" % sys.argv[0])
    sys.exit(1)

qari_metadata = json.load(open(sys.argv[1]))
stats = json.load(open(sys.argv[2]))
stats = {k: v for k, v in stats.items() if not any(x in k for x in blacklist)}

min_register = min(x["register"] for x in stats.values())
max_register = max(x["register"] for x in stats.values())
min_time = min(x["time"] for x in stats.values())
max_time = max(x["time"] for x in stats.values())

# We cajole the datapoints to be evenly spread out using log/exp scales.
# hz_exp_factor = 2.5
# vt_exp_factor = 0.6
hz_exp_factor = vt_exp_factor = 1
min_score = 10
for qari_key, qstats in stats.items():
    # NB we switch to "speed" here from "time."
    qstats["speed_score"] = min_score + \
        math.pow((1 - (qstats["time"] - min_time) / (max_time - min_time)) * 100, hz_exp_factor) \
        / math.pow(100, hz_exp_factor) * (100 - min_score)
    qstats["register_score"] = min_score + \
        math.pow(((qstats["register"] - min_register) / (max_register - min_register)) * 100, vt_exp_factor) \
        / math.pow(100, vt_exp_factor) * (100 - min_score)

items = []
qari_stats_lite = {}
for qari_key, qstats in sorted(stats.items(), key=lambda x: x[1]["speed_score"]):
    name = qari_metadata[qari_key]["name"]

    # Mangle name to separate attributes like riwayah, "Taraweeh 14xx", etc.
    sub = None
    for cut, strip in ((" - ", None), ("[", "]"), ("(", ")")):
        if cut in name:
            name, _, sub = name.partition(cut)
            if strip:
                sub = sub.strip(strip)
    if "Taraweeh" in name:
        name, sub, sub2 = name.partition("Taraweeh")
        sub += sub2
    if sub:
        sub = sub.strip()

    items.append(
        """
<div class="item" qari="{qari_key}">
    <div class="speed"><span style="width: {speed_score}%">&nbsp;</span></div>
    <div class="controls">{name}<span class="control-button-group">
        <a class="fa fa-play-circle control-button audio-player" href="http://download.quranicaudio.com/quran/{rel_path}078.mp3"></a>
        <a class="fa fa-cloud-download control-button" href="https://quranicaudio.com/quran/{id}" target="_blank"></a>
    </span></div>
    <div class="register"><span style="width: {register_score}%">&nbsp;</span></div>
</div>""".format(
            qari_key=qari_key,
            speed_score=qstats["speed_score"],
            name=name + (" <span class=\"sub\">%s</span>" % sub if sub else ""),
            rel_path=qari_metadata[qari_key]["relative_path"],
            id=qari_metadata[qari_key]["id"],
            register_score=qstats["register_score"],
        ))

    qari_stats_lite[qari_key] = {
        "speed": qstats["speed_score"],
        "register": qstats["register_score"],
    }

rendered_site = template.format(
    items="".join(items),
    qari_stats=json.dumps(qari_stats_lite))

minified_site = htmlmin.minify(rendered_site, remove_empty_space=True, remove_optional_attribute_quotes=False)

open("site/index.html", "w").write(minified_site)
