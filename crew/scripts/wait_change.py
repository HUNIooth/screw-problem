#!/usr/bin/env python3
"""파일이 바뀔 때까지 기다렸다가 바뀐 파일과 새로 붙은 줄만 출력한다.

--state를 주면 마지막으로 본 내용을 기억해, 기다리지 않은 사이에 바뀐 것도 바로 알려 준다.

사용:
  wait_change.py [--state S.json] [--timeout 600] [--interval 3] [--max-lines 200] FILE [FILE ...]

끝 코드: 0 바뀜, 2 시간 초과
"""
import argparse
import hashlib
import json
import os
import sys
import time


def read_lines(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return None


def digest(lines):
    return hashlib.sha1("\n".join(lines).encode("utf-8")).hexdigest()


def fingerprint(path):
    lines = read_lines(path)
    if lines is None:
        return None
    return {"lines": len(lines), "sha": digest(lines)}


def load_state(path, files):
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            saved = json.load(f)
        return {p: saved.get(p) for p in files}
    return {p: fingerprint(p) for p in files}


def save_state(path, state):
    if not path:
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)


def report(path, old, max_lines):
    lines = read_lines(path)
    print(f"== {path}")
    if lines is None:
        print("(파일 없음)")
        return None
    if old and old["lines"] <= len(lines) and digest(lines[: old["lines"]]) == old["sha"]:
        new = lines[old["lines"]:]
        label = f"새 줄 {len(new)}개"
    else:
        new = lines
        label = f"새로 쓰임, 전체 {len(new)}줄"
    if len(new) > max_lines:
        print(f"({label}, 앞 {len(new) - max_lines}줄 생략)")
        new = new[-max_lines:]
    else:
        print(f"({label})")
    print("\n".join(new))
    return {"lines": len(lines), "sha": digest(lines)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--state")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--interval", type=float, default=3)
    ap.add_argument("--max-lines", type=int, default=200)
    a = ap.parse_args()

    state = load_state(a.state, a.files)
    end = time.time() + a.timeout
    while True:
        changed = [p for p in a.files if fingerprint(p) != state[p]]
        if changed:
            time.sleep(1)  # 쓰는 중일 수 있으니 잠깐 더 기다린다
            for p in changed:
                state[p] = report(p, state[p], a.max_lines)
            save_state(a.state, state)
            return 0
        if time.time() >= end:
            save_state(a.state, state)
            print(f"시간 초과: {a.timeout}초 동안 변화 없음")
            return 2
        time.sleep(a.interval)


if __name__ == "__main__":
    sys.exit(main())
