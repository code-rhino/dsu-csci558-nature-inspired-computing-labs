"""Send a saved trace to the open viewer.

    python3 -m viewer.show labs/00-start-here/examples            # list the traces in a folder
    python3 -m viewer.show labs/00-start-here/examples/7          # play the one starting with "7"
    python3 -m viewer.show traces/00-start-here/F1-random-search.json
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def describe(path):
    d = json.loads(path.read_text())
    farm = d["farm"]
    return f"Farm {farm['number']} · {d['algo']}" + (f"  ({d['note']})" if d.get("note") else "")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    arg = Path(sys.argv[1])
    if not arg.is_absolute() and not arg.exists() and not arg.parent.exists():
        arg = ROOT / arg                    # also accept paths written from the repo root
    if arg.is_dir():
        files = sorted(arg.glob("*.json"))
        for f in files:
            print(f"  {f.stem:<32} {describe(f)}")
        print(f"\nplay one:  python3 -m viewer.show {arg}/<name or number>")
        return
    if not arg.exists():
        matches = sorted(arg.parent.glob(arg.name + "*.json"))
        if len(matches) != 1:
            sys.exit(f"no single trace matches {arg} ({len(matches)} found)")
        arg = matches[0]
    out = ROOT / "traces"
    out.mkdir(exist_ok=True)
    data = json.loads(arg.read_text())
    data["id"] = f"show-{arg.stem}-{time.time():.3f}"   # make the viewer reload even if it was shown before
    tmp = out / "latest.tmp"
    tmp.write_text(json.dumps(data, separators=(",", ":")))
    tmp.replace(out / "latest.json")
    print(f"sent {arg.name} to the viewer: {describe(arg)}")


if __name__ == "__main__":
    main()
