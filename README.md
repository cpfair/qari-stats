# qari-stats

[Find Qur'an recitations by speed & voice pitch at qaris.cpfx.ca.](http://qaris.cpfx.ca)

## Usage

1. Install `requirements.txt` (Py3k) and ffmpeg
1. Run `python scrape_qari_metadata.py > qari_metadata.json`
1. Download audio files from [QuranicAudio.com](https://quranicaudio.com) - they should all be for the same surah ([qaris.cpfx.ca](http://qaris.cpfx.ca) uses Surah an-Naba). Make sure the MP3s are named according to the keys in `qari_metadata.json`
1. Run `python analyze.py path/to/your/mp3s/*.mp3 > qari_stats.json` to analyze the audio files.
1. Run `python generate_site.py qari_metadata.json qari_stats.json` to generate the website in `site/`

## Licensing and Credits

This project is available under the MIT License. The metadata and recordings used in this project are from [QuranicAudio.com](https://quranicaudio.com), and are licensed separately.
