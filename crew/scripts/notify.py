#!/usr/bin/env python3
"""macOS 알림을 띄운다. macOS가 아니면 터미널에만 출력한다.

사용: notify.py "제목" "내용"
"""
import subprocess
import sys

SCRIPT = """on run argv
display notification (item 2 of argv) with title (item 1 of argv) sound name "Glass"
end run"""


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip())
        return 1
    title, message = sys.argv[1], sys.argv[2]
    print(f"[알림] {title}: {message}")
    if sys.platform == "darwin":
        r = subprocess.run(["osascript", "-e", SCRIPT, "--", title, message],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"알림 실패: {r.stderr.strip()}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
