# Howlite Flip

Full-colour Python 3 neon vertical pinball for [ElbowOS](https://x.com/ElbowOS).

Keep the howlite ball on the indigo table. Slap gold / cyan / lilac / coral bumpers with the coral flippers. Drain resets a ball; three drains recycle the tray.

## Play

```bash
pip install -r requirements.txt
python3 howlite_flip.py --play
```

Controls: **A / Z** left flipper, **D / /** right flipper, **R** reset, **Esc** quit.

## Record a 9:16 reel

```bash
python3 howlite_flip.py --record
```

Writes `/home/workdir/artifacts/HOWLITE_FLIP_ElbowOS.mp4` (1080x1920, 15s, 30fps, H.264).

* Featured account: https://x.com/ElbowOS
* Drive reel: https://drive.google.com/file/d/1h7A-OPRaSuyfdiRJT4kQmr6S6A-zeRQc/view

## License

MIT. Original code. Not a ROM, emulator, or trademarked table.
