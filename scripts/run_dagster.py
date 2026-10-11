#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import re
import signal
import subprocess
import sys
import webbrowser


URL_PATTERN = re.compile(r"Serving dagster-webserver on (http://\S+)")
dagster = Path(__file__).parent.parent / ".venv" / "bin" / "dagster"


child = subprocess.Popen(
    [str(dagster), "dev"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

interrupted = False


def forward_signal(signum, frame):
    global interrupted
    interrupted = True
    if child.poll() is None:
        child.send_signal(signum)


signal.signal(signal.SIGINT, forward_signal)
signal.signal(signal.SIGTERM, forward_signal)

browser_opened = False

try:
    assert child.stdout is not None
    for line in child.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        match = URL_PATTERN.search(line)
        if match and not browser_opened:
            webbrowser.open_new_tab(match.group(1))
            browser_opened = True
finally:
    returncode = child.wait()
    sys.exit(0 if interrupted else returncode)
