"""Send a saved trace to the open viewer.

    python3 -m viewer.show labs/01-reach-search/examples            # list the traces in a folder
    python3 -m viewer.show labs/01-reach-search/examples/7          # play the one starting with "7"
    python3 -m viewer.show traces/01-reach-search/L3-simulated-annealing.json
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def describe(path):
    d = json.loads(path.read_text())
    lv = d["level"]
    return f"Level {lv['number']} · {d['algo']}" + (f"  ({d['note']})" if d.get("note") else "")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    arg = Path(sys.argv[1])
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
    data["id"] = f"show-{arg.stem}-{__import__('time').time():.3f}"   # make the viewer reload even if it was shown before
    (out / "latest.json").write_text(json.dumps(data, separators=(",", ":")))
    print(f"sent {arg.name} to the viewer: {describe(arg)}")


if __name__ == "__main__":
    main()
