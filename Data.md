Noise Level Meter
A real-time noise level measurement tool with two versions:

Python script — runs in your terminal, reads your microphone, shows a live bar
HTML file — open in any browser, records mic live with a visual dashboard


Python version
Requirements
Python 3.7+
pip install sounddevice numpy
How to run
bashpython Noise_level.py
Enter the number of seconds to measure, then watch the live bar update in your terminal.
Example output
Seconds to measure: 5

Measuring noise for 5 second(s)...

[##############--------------------------]  -31.4 dB |  Normal

============================================================
  Readings collected :  108
  Average level      :  -31.4 dB  →  Normal
  Quietest moment    :  -52.1 dB
  Loudest moment     :  -18.7 dB
  Suggestion         :  Good for conversation or light work.
============================================================
Classification thresholds
LeveldBFS rangeSuggestionQuiet≤ −35 dBGood for study, reading or focusNormal−35 to −20 dBGood for conversation or workNoisy> −20 dBToo noisy for study

HTML version
No installation needed. Open noise_meter.html in Chrome, Firefox, or Edge.

Click Start recording and allow microphone access
See live dB reading, colour-coded meter bar, and scrolling history chart
Stats (average, quietest, loudest) update in real time
Click Stop to pause, Reset stats to clear history


Notes

Values are in dBFS (decibels relative to full scale), not absolute SPL
Results depend on your microphone gain settings
The Python version requires a working microphone connected to your machine
The HTML version works in any modern browser that supports the Web Audio API


File structure
noise-level-meter/
├── Noise_level.py     # Python terminal version
├── noise_meter.html   # Browser version (no install needed)
└── README.md
