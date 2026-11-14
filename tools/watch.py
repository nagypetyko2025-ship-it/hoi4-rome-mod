"""Session watcher: records everything the game logs while you play, then writes a report for the team.

    python tools/watch.py                 waits for hoi4.exe, follows the logs until the game closes
    python tools/watch.py --once          reads the current logs once and writes the report (game not needed)

Follows Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log and game.log while the game runs
(a restart of the game - the logs start again - is noticed), and at the end looks for a new crash folder.
Writes docs/session_logs/<date_time>_session.md (and _events.csv), refreshed every minute, so a report exists
even if the game or the watcher dies:
  - errors that point at OUR files (common/..., events/... that exist in this mod), grouped, during load vs. play
  - base-game lines that mention our content (ante_*, ROM_ ...) and a count of the base game's own noise
  - the in-game event log (ANTE| lines from tools/eventlog.py and the focus log of tools/content.py):
    wars, peace, capitulations, annexations, puppets, factions, governments, focuses, monthly figures
  - a crash, with the first lines of exception.txt
Personal paths and the Windows user name are removed from everything written (the repository is public).
"""
import argparse
import csv
import ctypes
import os
import re
import subprocess
import sys
import time
from collections import Counter, OrderedDict
from datetime import datetime
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
OUT = MOD / "docs" / "session_logs"
PATH_RE = re.compile(r"((?:common|events|history|interface|gfx|localisation|map|portraits|music|sound|tutorial)"
                     r"/[\w/.\- ]+?\.(?:txt|gui|gfx|yml|csv|lua|dds|tga|png|asset|bmp|fxh))")
STAMP_RE = re.compile(r"^\[(\d\d:\d\d:\d\d)\]\[([^\]]*)\]:\s*")
BASE_COPIES = ("common/doctrines/", "common/wargoals/", "common/buildings/00_buildings.txt",
               "common/technology_tags/", "interface/countrytechtreeview.gui")
WATCH_TAGS = {"ROM", "ATH", "LAK", "MKD", "PRS", "CAR", "SEN"}   # the countries with a focus tree of their own
OURS_RE = re.compile(r"\bante_|\bANTE_|\bROM_|_cmd_|\bante\b")


def documents():
    try:
        buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)   # CSIDL_PERSONAL
        if buf.value:
            return Path(buf.value)
    except Exception:
        pass
    return Path.home() / "Documents"


GAME_DOCS = documents() / "Paradox Interactive" / "Hearts of Iron IV"
LOGS = GAME_DOCS / "logs"
CRASHES = GAME_DOCS / "crashes"


def clean(text):
    """remove personal paths and the user name"""
    home = str(Path.home())
    for h in {home, home.replace("\\", "/"), home.replace("\\", "\\\\")}:
        text = text.replace(h, "~")
    user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    if len(user) >= 3:
        text = re.sub(re.escape(user), "<user>", text, flags=re.I)
    return text


def game_running():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq hoi4.exe", "/NH"], capture_output=True, text=True,
                             timeout=20).stdout
        return "hoi4.exe" in out.lower()
    except Exception:
        return False


class Follower:
    """reads what was added to a log file since the last call (handles the file starting again)"""

    def __init__(self, path, from_start):
        self.path, self.pos, self.restarts = path, 0, 0
        if not from_start and path.exists():
            self.pos = path.stat().st_size

    def read(self):
        if not self.path.exists():
            return []
        size = self.path.stat().st_size
        if size < self.pos:          # the game started again and the log began anew
            self.pos, self.restarts = 0, self.restarts + 1
        if size == self.pos:
            return []
        with open(self.path, "rb") as fh:
            fh.seek(self.pos)
            data = fh.read()
        self.pos += len(data)
        return data.decode("utf-8", "replace").splitlines()


class Session:
    def __init__(self):
        self.started = datetime.now()
        self.mod_errors = OrderedDict()       # normalised message -> [count, first seen, phase, example]
        self.related = OrderedDict()
        self.noise = Counter()
        self.events, self.months = [], []
        self.focus_done, self.player = [], None
        self.first_date = self.last_date = None
        self.lines = 0
        self.crash = None

    def add_error(self, line):
        self.lines += 1
        m = STAMP_RE.match(line)
        clock, gdate = (m.group(1), m.group(2)) if m else ("", "")
        msg = line[m.end():] if m else line
        phase = "load" if (not gdate or gdate == "no_game_date") else "play"
        paths = PATH_RE.findall(msg)
        # copies of base-game files (tools/tech.py, ai.py, buildings.py) keep the base game's own complaints: not ours
        ours = any((MOD / p).exists() and not p.startswith(BASE_COPIES) for p in paths)
        key = re.sub(r"\d+", "#", msg)[:300]
        if ours:
            bucket = self.mod_errors
        elif OURS_RE.search(msg):
            bucket = self.related
        else:
            self.noise[paths[0] if paths else "(no file)"] += 1
            return
        if key in bucket:
            bucket[key][0] += 1
            if phase == "play":
                bucket[key][2] = "play"
        else:
            bucket[key] = [1, f"{clock} {gdate}".strip(), phase, msg[:400]]

    def add_game(self, line):
        i = line.find("ANTE|")
        if i < 0:
            return
        f = line[i:].strip().strip('"').split("|")[1:]
        if len(f) < 2:
            return
        date, kind, rest = f[0], f[1], f[2:]
        self.first_date = self.first_date or date
        self.last_date = date
        if kind == "start" and rest:
            self.player = rest[0]
        if kind == "month":
            row = {"date": date, "tag": rest[0] if rest else ""}
            for kv in rest[1:]:
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    row[k] = v
            self.months.append(row)
        elif kind == "rome":
            row = {"date": date, "tag": "ROM*"}
            for kv in rest[1:]:
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    row[k] = v
            self.months.append(row)
        elif kind == "focus":
            self.focus_done.append((date, *rest))
        else:
            self.events.append((date, kind, *rest))

    # ------------------------------------------------------------------ report
    def write(self, final=False):
        OUT.mkdir(parents=True, exist_ok=True)
        stem = self.started.strftime("%Y%m%d_%H%M")
        md = OUT / f"{stem}_session.md"
        dur = datetime.now() - self.started
        L = [f"# Session {self.started:%Y-%m-%d %H:%M} ({'finished' if final else 'still running'})", "",
             f"- watched for {int(dur.total_seconds() // 60)} min, {self.lines} error.log lines",
             f"- player: {self.player or '?'}; game dates seen: {self.first_date or '-'} .. {self.last_date or '-'}",
             f"- errors in our files: {sum(v[0] for v in self.mod_errors.values())} lines, {len(self.mod_errors)} kinds "
             f"({sum(1 for v in self.mod_errors.values() if v[2] == 'play')} kinds during play)",
             f"- base-game lines about our content: {sum(v[0] for v in self.related.values())}; base-game noise: "
             f"{sum(self.noise.values())} lines",
             f"- crash: {'YES - see below' if self.crash else 'no'}", ""]
        if self.crash:
            L += ["## Crash", "", "```", self.crash, "```", ""]

        def table(title, bucket, n):
            out = [f"## {title}", ""]
            if not bucket:
                return out + ["none", ""]
            out += ["| count | first (clock / game date) | when | message |", "|---|---|---|---|"]
            items = sorted(bucket.values(), key=lambda v: (v[2] != "play", -v[0]))[:n]
            for c, first, phase, ex in items:
                out.append(f"| {c} | {first} | {phase} | {ex.replace('|', '/')} |")
            return out + [""]
        L += table("Errors in our files (play first)", self.mod_errors, 80)
        L += table("Base-game lines that mention our content", self.related, 40)
        L += ["## Base-game noise (by file, top 15)", ""] + [f"- {n} x {p}" for p, n in self.noise.most_common(15)] + [""]
        L += ["## Events", ""]
        if self.events:
            kinds = Counter(e[1] for e in self.events)
            L += ["Counts: " + ", ".join(f"{k} {n}" for k, n in kinds.most_common()), ""]
            big = [e for e in self.events if e[1] != "state"]
            L += [f"- {e[0]}: {e[1]} " + " ".join(e[2:]) for e in big[:300]]
            st = [e for e in self.events if e[1] == "state"]
            if st:
                L += ["", f"State changes involving the watched countries ({len(st)}, last 60):", ""]
                L += [f"- {e[0]}: {' '.join(e[2:])}" for e in st[-60:]]
        else:
            L += ["none (no ANTE| lines in game.log yet - was a game started?)"]
        # all countries complete focuses: list those of the player and of the countries with their own tree, count the rest
        mine = [f for f in self.focus_done if f[1:2] and (f[1] in WATCH_TAGS or f[1] == self.player)]
        rest = Counter(f[1] for f in self.focus_done if f not in mine and f[1:2])
        L += ["", "## Focuses completed", ""] + ([f"- {d}: {' '.join(r)}" for d, *r in mine] or ["none"])
        if rest:
            L += ["", f"Other countries: {sum(rest.values())} focuses - most: " +
                  ", ".join(f"{t} {n}" for t, n in rest.most_common(15))]
        L += ["", "## Monthly figures (last of each country)", ""]
        last = OrderedDict()
        for r in self.months:
            last[r["tag"]] = r
        if last:
            keys = sorted({k for r in last.values() for k in r} - {"tag", "date"})
            L += ["| tag | date | " + " | ".join(keys) + " |", "|---" * (len(keys) + 2) + "|"]
            L += [f"| {t} | {r['date']} | " + " | ".join(r.get(k, "") for k in keys) + " |" for t, r in last.items()]
        else:
            L += ["none"]
        md.write_text(clean("\n".join(L)) + "\n", encoding="utf-8", newline="\n")
        if self.months:
            keys = ["date", "tag"] + sorted({k for r in self.months for k in r} - {"tag", "date"})
            with open(OUT / f"{stem}_events.csv", "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, keys)
                w.writeheader()
                w.writerows(self.months)
        return md


def crash_report(before):
    if not CRASHES.exists():
        return None
    new = [d for d in CRASHES.rglob("exception.txt") if d.parent not in before]
    if not new:
        return None
    ex = max(new, key=lambda p: p.stat().st_mtime)
    text = ex.read_text(encoding="utf-8", errors="replace").splitlines()[:40]
    return clean("\n".join(text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="read the logs as they are now and write the report")
    ap.add_argument("--wait", type=int, default=600, help="seconds to wait for the game to start")
    a = ap.parse_args()
    s = Session()
    if a.once:
        for line in Follower(LOGS / "error.log", True).read():
            s.add_error(line)
        for line in Follower(LOGS / "game.log", True).read():
            s.add_game(line)
        print(s.write(final=True).relative_to(MOD))
        return
    t0 = time.time()
    while not game_running():
        if time.time() - t0 > a.wait:
            sys.exit("hoi4.exe did not start")
        time.sleep(3)
    before = {p.parent for p in CRASHES.rglob("exception.txt")} if CRASHES.exists() else set()
    # the game may already have written the start of its logs: read them from the beginning
    err, game = Follower(LOGS / "error.log", True), Follower(LOGS / "game.log", True)
    print(f"watching {clean(str(LOGS))} - the report is refreshed every minute", flush=True)
    last_write, gone_since = 0, None
    while True:
        for line in err.read():
            s.add_error(line)
        for line in game.read():
            s.add_game(line)
        if time.time() - last_write > 60:
            s.write()
            last_write = time.time()
        if err.restarts or game.restarts:
            # the game was started again (its logs began anew): this session is over - start a new watcher for the
            # next one (round 26: three watchers kept running and wrote overlapping reports)
            print("the game was restarted - closing this session's report", flush=True)
            break
        if game_running():
            gone_since = None
        else:
            gone_since = gone_since or time.time()
            if time.time() - gone_since > 15:      # closed (or crashed) - give the crash reporter a moment
                break
        time.sleep(3)
    for line in err.read():
        s.add_error(line)
    for line in game.read():
        s.add_game(line)
    s.crash = crash_report(before)
    md = s.write(final=True)
    print(f"game closed - report: {md.relative_to(MOD)}", flush=True)


if __name__ == "__main__":
    main()
