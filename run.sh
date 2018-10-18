#!/bin/bash

set -euo pipefail

python3 /home/leon/github/vertretungsplan/pull_plan.py
python3 /home/leon/github/vertretungsplan/convert.py
python3 /home/leon/github/vertretungsplan/vp_bot.py
