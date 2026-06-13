from __future__ import annotations

import re
import sys
from collections.abc import Sequence

SIGNOFF_RE = re.compile(
    r'^Signed-off-by: (?P<name>.+?) <(?P<email>.+?)>$',
    re.MULTILINE,
)


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print('check-dco: missing commit message filename', file=sys.stderr)
        return 1

    filename = argv[0]
    with open(filename) as f:
        message = f.read()

    if not message.strip():
        print('check-dco: commit message is empty', file=sys.stderr)
        return 1

    signoffs = SIGNOFF_RE.findall(message)

    if not signoffs:
        print(
            'check-dco: missing required Signed-off-by line. '
            'Use git commit -s to add one automatically.',
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
