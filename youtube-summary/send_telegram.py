#!/usr/bin/env python3
"""Send a markdown file to Telegram with sendRichMessage (Bot API 10.2+).

    TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... python3 send_telegram.py summary.md
    python3 send_telegram.py --self-check

Credentials come only from the environment, never from the repo.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Telegram's limit is in BYTES, not characters. Text over ~35000 bytes is
# silently truncated (the API still answers OK), and Latin text over 32768
# characters fails with RICH_MESSAGE_TEXT_TOO_LONG. 30000 bytes is safe for
# any language.
LIMIT = 30000


def size(s):
    return len(s.encode())


def credentials():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat:
        sys.exit('Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to send to Telegram.')
    return f'https://api.telegram.org/bot{token}', chat


def chunks(text, limit=LIMIT):
    """Split on paragraph, then line boundaries, then hard; measured in bytes."""
    if size(text) <= limit:
        return [text]
    for sep in ('\n\n', '\n'):
        if sep not in text:
            continue
        out, cur = [], ''
        for piece in text.split(sep):
            cand = f'{cur}{sep}{piece}' if cur else piece
            if size(cand) <= limit:
                cur = cand
                continue
            if cur:
                out.append(cur)
            sub = chunks(piece, limit)
            out.extend(sub[:-1])
            cur = sub[-1]
        if cur:
            out.append(cur)
        return out
    step = limit // 4  # 4 bytes is the UTF-8 maximum per character
    return [text[i:i + step] for i in range(0, len(text), step)]


def send(md):
    base, chat = credentials()
    parts = chunks(md)
    for i, part in enumerate(parts, 1):
        payload = {'chat_id': chat, 'rich_message': {'markdown': part}}
        req = urllib.request.Request(
            f'{base}/sendRichMessage',
            data=json.dumps(payload).encode(),
            headers={'Content-Type': 'application/json'},
        )
        try:
            urllib.request.urlopen(req, timeout=30).read()
        except urllib.error.HTTPError as e:
            desc = json.load(e).get('description', str(e))
            sys.exit(f'Telegram rejected part {i}/{len(parts)}: {desc}')
    print(f'sent to Telegram: {len(parts)} message(s), {len(md)} chars')


def self_check():
    assert chunks('a' * 100) == ['a' * 100]
    for name, big in [
        ('latin', '\n\n'.join(['x' * 20000] * 3)),
        ('cyrillic', '\n\n'.join(['я' * 20000] * 3)),
        ('emoji', '\n\n'.join(['🔥' * 5000] * 3)),
        ('long paragraph', 'я' * (LIMIT * 2)),
        ('one long line', 'я ' * (LIMIT // 2)),
    ]:
        parts = chunks(big)
        assert all(size(c) <= LIMIT for c in parts), f'{name}: part over limit'
        assert ''.join(parts).replace('\n', '') == big.replace('\n', ''), f'{name}: text lost'
    print('ok')


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else ''
    if arg == '--self-check':
        self_check()
    elif arg:
        send(Path(arg).read_text())
    else:
        sys.exit(__doc__)
