#!/usr/bin/env python3
"""파일이 바뀔 때까지 기다렸다가 읽어야 할 줄 범위를 알려 준다.

내용은 출력하지 않는다. 범위를 직접 읽은 뒤 --done으로 완료를 표시해야 상태가 앞으로 간다.
완료 전에는 다시 실행해도 같은 범위를 또 알려 준다.

사용:
  wait_change.py --state S.json [--timeout 600] [--interval 3] FILE [FILE ...]
  wait_change.py --state S.json --done

끝 코드: 0 바뀜 또는 완료, 2 시간 초과, 3 읽는 사이 바뀐 파일 있음
"""
import argparse
import hashlib
import json
import os
import sys
import time

EMPTY = hashlib.sha1(b"").hexdigest()


def read_lines(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []


def digest(lines):
    return hashlib.sha1("\n".join(lines).encode("utf-8")).hexdigest()


def load_state(path):
    try:
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
        if isinstance(state, dict) and isinstance(state.get("files"), dict):
            return state
    except FileNotFoundError:
        return {"files": {}}
    except (OSError, ValueError):
        pass
    print("상태 파일이 깨져 처음부터 다시 읽는다")
    return {"files": {}}


def save_state(path, state):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def unread(lines, entry):
    """아직 완료 표시하지 않은 범위. 없으면 None."""
    done = entry.get("done", 0)
    if done <= len(lines) and digest(lines[:done]) == entry.get("sha", EMPTY):
        return (done + 1, len(lines), False) if len(lines) > done else None
    return (1, len(lines), True)


def describe(path, start, end, rewritten):
    if rewritten and end == 0:
        return f"== {path}: 비워졌거나 지워짐"
    if rewritten:
        return f"== {path}: 새로 쓰임, 1~{end}행 전체"
    return f"== {path}: 새 줄 {start}~{end}행"


def wait(args):
    state = load_state(args.state)
    files = state["files"]
    deadline = time.time() + args.timeout
    while True:
        if any(unread(read_lines(p), files.get(p, {})) for p in args.files):
            time.sleep(1)  # 쓰는 중일 수 있으니 잠깐 더 기다린다
            reported = False
            for p in args.files:
                lines = read_lines(p)
                entry = files.setdefault(p, {"done": 0, "sha": EMPTY})
                rng = unread(lines, entry)
                if rng:
                    entry["offered"] = {"to": rng[1], "sha": digest(lines[: rng[1]])}
                    print(describe(p, *rng))
                    reported = True
            if reported:
                save_state(args.state, state)
                print("범위를 빠짐없이 읽은 뒤 --done으로 완료를 표시한다.")
                return 0
        if time.time() >= deadline:
            print(f"시간 초과: {args.timeout}초 동안 변화 없음")
            return 2
        time.sleep(args.interval)


def done(args):
    state = load_state(args.state)
    stale = []
    for p, entry in state["files"].items():
        offered = entry.pop("offered", None)
        if not offered:
            continue
        lines = read_lines(p)
        if len(lines) >= offered["to"] and digest(lines[: offered["to"]]) == offered["sha"]:
            entry["done"], entry["sha"] = offered["to"], offered["sha"]
        else:
            stale.append(p)
    save_state(args.state, state)
    for p in stale:
        print(f"읽는 사이 바뀜: {p} (다시 기다리면 새 범위를 알려 준다)")
    if stale:
        return 3
    print("완료 표시함")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--state", required=True)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--interval", type=float, default=3)
    ap.add_argument("--done", action="store_true")
    a = ap.parse_args()
    if a.done:
        return done(a)
    if not a.files:
        ap.error("기다릴 파일을 하나 이상 준다")
    return wait(a)


if __name__ == "__main__":
    sys.exit(main())
