# Recording Reference

How to produce a clean, repeatable `.cast` file. Most "ugly" terminal recordings come from skipped preflight, not from asciinema itself.

## Preflight checklist

- [ ] **Terminal dimensions.** `--cols 100 --rows 30` for 16:9 decks; `--cols 80 --rows 24` for retro/Beamer.
- [ ] **Clean prompt.** `export PS1='$ '` (zsh: `export PROMPT='$ '`) for the recording shell only.
- [ ] **Dotfile isolation** (optional but recommended). `HOME=$(mktemp -d) bash --noprofile --norc`.
- [ ] **Disable shell history sharing / git-status-in-prompt / autosuggestions** — they leak personal state into the cast.
- [ ] **Set `TERM=xterm-256color`** so colors render consistently in the player.
- [ ] **Clear the screen** before recording (`clear`) so frame 0 is empty.

## Recording commands

```bash
# Interactive recording, save to demo.cast
asciinema rec --cols 100 --rows 30 --idle-time-limit 2 \
              --title "<TITLE>" demo.cast
# (type your demo, then `exit` or Ctrl-D to stop)

# Non-interactive (run a fixed command, capture its output)
asciinema rec --command "<command>" demo.cast

# Overwrite an existing cast without prompting
asciinema rec --overwrite demo.cast
```

## Flag reference

| Flag | Effect |
|---|---|
| `--cols <N>` | Terminal width at record time (embedded in cast) |
| `--rows <N>` | Terminal height at record time |
| `--idle-time-limit <SEC>` | Collapse pauses longer than `SEC` to `SEC` |
| `--title <STR>` | Title metadata stored in cast header |
| `--command <CMD>` | Run `CMD` and record its output; exit when done |
| `--env <VARS>` | Comma-separated env vars to record (default: `SHELL,TERM`) |
| `--quiet` | Suppress the "asciinema started" banner |
| `--overwrite` | Replace destination cast file silently |
| `--stdin` | Record stdin too (paste sequences); off by default |

## Recording with input

For demos that take user input (`vim`, interactive REPLs), `asciinema rec --stdin` records keystrokes including arrow keys. Beware: backspace and arrow-key keystrokes are visible in the cast as control sequences — the *displayed* output looks normal, but if you `jq .` the cast you see the keys.

## Recording a fixed command (CI-friendly)

When the demo is fully scripted, `--command` produces a deterministic cast:

```bash
asciinema rec --cols 100 --rows 30 \
              --command "bash demo-script.sh" \
              demo.cast
```

`demo-script.sh` should contain the entire demo. The cast captures only the output (and any prompts the script renders), so it's reproducible across runs. This is the right path for documentation casts that need to update in CI.

## Wrapper script

`scripts/record-demo.sh` bundles the sane defaults:

```bash
bash scripts/record-demo.sh "<TITLE>" demo.cast
# Equivalent to:
# asciinema rec --cols 100 --rows 30 --idle-time-limit 2 --title "<TITLE>" demo.cast
```

Read the script if you need to tweak the defaults.

## Verifying the cast

```bash
# Play it back to verify
asciinema play demo.cast

# Inspect the cast file (it's JSON-per-line)
head -3 demo.cast
# {"version": 2, "width": 100, "height": 30, ...}
# [0.012345, "o", "$ "]
# [0.987654, "o", "echo hello\r\n"]

# Quick stats
asciinema cat demo.cast | wc -l        # number of output events
jq -s 'last | .[0]' demo.cast          # total duration in seconds (first field of last event)
```

## Re-recording vs editing

Asciinema casts are JSON line-streams of `[timestamp, type, payload]` tuples. They *can* be edited by hand — re-time, trim, splice — but it's almost always faster to re-record. The exception: trimming a long idle at the start/end:

```bash
# Trim the first 2 seconds (a common "warmup" idle)
jq -s '
  .[0] as $header
  | [$header] + (.[1:] | map(select(.[0] >= 2)) | map(.[0] -= 2 | .))
' demo.cast > demo-trimmed.cast
```

(That's brittle. Re-record if you can.)
