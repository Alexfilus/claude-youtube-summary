# youtube-summary

A [Claude Code](https://claude.com/claude-code) skill. Paste a YouTube link and Claude reads the transcript and replies with a structured summary: main thesis first, key sections, bolded numbers, and an independent "My analysis" at the end. Optionally the summary is also sent to your Telegram.

- Works in the language you write in; falls back to the English track and translates.
- Flags ads, auto-subtitle errors and unsupported claims instead of repeating them.
- No Telegram setup needed: without credentials it only replies in chat.

## Install

You need [uv](https://docs.astral.sh/uv/) (or pipx) and Claude Code.

```bash
# 1. Transcript tool
uv tool install youtube-transcript-api

# 2. The skill
git clone https://github.com/Alexfilus/claude-youtube-summary.git ~/claude-youtube-summary
mkdir -p ~/.claude/skills
ln -s ~/claude-youtube-summary/youtube-summary ~/.claude/skills/youtube-summary
```

Restart Claude Code. To update later: `git -C ~/claude-youtube-summary pull`.

Without a symlink, copy the folder instead: `cp -R ~/claude-youtube-summary/youtube-summary ~/.claude/skills/`.

For one project only, put it in `<project>/.claude/skills/youtube-summary` instead.

## Use

Send a link, with or without a question:

```
https://www.youtube.com/watch?v=VIDEO_ID
```

Or invoke it by name: `/youtube-summary <link>`.

## Optional: Telegram

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Send any message to your bot, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` and copy `chat.id`.
3. Export both variables where Claude Code starts, for example in `~/.zshrc`:

```bash
export TELEGRAM_BOT_TOKEN="123456:ABC..."
export TELEGRAM_CHAT_ID="123456789"
```

Or put them in `~/.claude/settings.json`:

```json
{ "env": { "TELEGRAM_BOT_TOKEN": "123456:ABC...", "TELEGRAM_CHAT_ID": "123456789" } }
```

Messages use Telegram's `sendRichMessage` (Bot API 10.2+) so markdown headings, bold and tables render as is. Long summaries are split by bytes. Check the splitter with `python3 youtube-summary/send_telegram.py --self-check`.

## Troubleshooting

- **`youtube_transcript_api: command not found`** — make sure `~/.local/bin` is in `PATH`.
- **Blocked IP / "Could not retrieve a transcript"** — YouTube blocks some cloud and VPN addresses; try from a home connection.
- **No subtitles** — the skill says so and falls back to the title and description.
- **Skill not found** — check that `~/.claude/skills/youtube-summary/SKILL.md` exists and restart Claude Code.

## License

MIT
