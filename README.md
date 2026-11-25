# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/zonawallets-cell/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/zonawallets-cell/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A one-page newspaper front page summing up Thursday 26 November 2026's world news in a single 1024×1024 image — led by two oil tankers hitting naval mines and burning in the Strait of Hormuz, with nine more verified stories of the day, a world map with numbered pins, and an ALSO TODAY band — rendered from real 26 November 2026 news.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program is pure Python standard library: it copies the `entry.png` beside it to `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR`). `render.py` is the build-time renderer that drew the image from the day's news.

---

<sub>Entered on [make.fun](https://make.fun/?ref=891cqs0k&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
