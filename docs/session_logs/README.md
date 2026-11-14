# Session reports (tools/watch.py)

- `20261114_1334_session.md`: Peti, Rome, 245-260 AUC - written by the first watcher, which kept running through
  three restarts of the game (fixed in round 26: a watcher now stops when the game starts again).
- `20261114_1552_session.md`: the last of those games, re-read with `--once` in the new, shorter format.

What they showed (round 26): no errors in our files, no crash; the AI never raised a new division and never spent its
political power (fixed by tools/ai.py); a base-game doctrine file wrote 228,000 'Invalid tech' lines (quietened by
tools/tech.py).
