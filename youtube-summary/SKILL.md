---
name: youtube-summary
description: Summarize a YouTube video from its transcript and optionally send the summary to Telegram. Use whenever the user sends a YouTube link (youtube.com/watch, youtu.be, /shorts/, /live/), with or without a question. A bare link means "summarize this"; do not ask what to do with it.
---

# YouTube → summary

A YouTube link without further instructions is a request for a summary. Fetch the transcript and answer right away.

## 0. Requirements

Check before the first run:

```bash
command -v youtube_transcript_api || echo "missing"
```

If missing, tell the user to install it (`uv tool install youtube-transcript-api` or `pipx install youtube-transcript-api`) and stop. `markitdown` (`uv tool install markitdown`) is optional and only used for metadata when there are no subtitles.

## 1. Settings

Defaults, unless the user or their CLAUDE.md says otherwise:

- **Language:** the language the user writes in.
- **Telegram:** send only if `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set in the environment (`[ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]`). Otherwise reply in chat only and do not mention Telegram.

## 2. Get the video ID

Always 11 characters:

| Form | ID |
|---|---|
| `youtube.com/watch?v=<ID>&t=42` | `<ID>` |
| `youtu.be/<ID>?si=xxx` | `<ID>` |
| `youtube.com/shorts/<ID>` | `<ID>` |
| `youtube.com/live/<ID>` | `<ID>` |

## 3. See what is available

```bash
youtube_transcript_api <ID> --list-transcripts
```

## 4. Fetch the transcript

Prefer a track in the summary language (manual or auto-generated). Write to a scratch directory, not the working tree:

```bash
youtube_transcript_api <ID> --languages <lang> --format text > "$TMPDIR/t.txt"; wc -w "$TMPDIR/t.txt"
```

No track in that language: take any available track, ideally `en`, and either translate with `--translate <lang>` or fetch it as is and translate while summarizing. If YouTube's translation errors out, fall back to the original. Read the file with the Read tool, not `cat`. A long transcript needs several Read calls; read all of it before answering.

## 5. If there is no transcript

- No subtitles at all: say so plainly and do not invent content. Fetch title and description with `markitdown "https://www.youtube.com/watch?v=<ID>"`. Use the full URL: `youtu.be` links return HTML without a transcript.
- Private, unavailable video, or YouTube blocked the IP: report the error as is.

## 6. Answer format

Structure follows the video, not a template:

- **Topic heading and the main thesis first**, the reason the video exists.
- `###` sections for the key blocks. Lists rather than solid text.
- **Bold** for numbers, thresholds, names and conclusions.
- A table only for enumerable facts (factors, comparisons).
- Practical advice in a separate block, if the video has any.
- Leave out ads, sponsor segments, guest introductions and thanks. Name a guest only if the position is unclear without it.
- **End with `### My analysis`:** one paragraph of your own assessment. How convincing the arguments are, where the author oversimplifies, what is missing, what contradicts known data, whether the whole video is worth watching. Your opinion, not a retelling.

Length is proportional to density: a 15-minute explainer is about a screen and a half. Do not pad small talk and do not squeeze dense material into three lines.

## 7. Flag separately

- **Hidden advertising.** If the conclusions steer toward the sponsor's product, say so in the analysis.
- **Auto-subtitle artifacts.** Speech recognition mangles terms, names and numbers. Do not carry typos into the summary. If a name or term the thesis relies on is distorted, say so. Do not state a currency or unit the transcript does not name as fact; mark it as inferred.
- **Medicine, finance, law.** Present as the author's position, not as fact. Keep "talk to a doctor" advice.
- **Unsupported claims.** If the author cites a study without details, write exactly that.
- **Timing.** Transcripts here have no timestamps; do not recommend "watch the first N minutes".

## 8. Send to Telegram (only if configured)

Write the **full** summary to `$TMPDIR/summary.md` with the **video link as the first line**, then:

```bash
python3 "<skill dir>/send_telegram.py" "$TMPDIR/summary.md"
```

The same text goes to chat and to Telegram. Do not send a shortened version: one message holds a detailed summary with a large margin. The script splits by bytes (`LIMIT = 30000`), because Telegram silently truncates above ~35000 bytes and Cyrillic takes two bytes per character. It uses `sendRichMessage`, which renders markdown as is (headings, bold, tables); do not convert to HTML. If the script fails, say so and give the error.
