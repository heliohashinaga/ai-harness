# 004 — cleaner retest results

model=deepseek-v4-flash provider=opencode (coder output fixed, no coder call)

- B1: STILL-BROKEN (documented check still fails) changed=True latency=52853ms regressions=0
- B2: STILL-BROKEN (documented check still fails) changed=True latency=99443ms regressions=2
- B3: STILL-BROKEN (documented check still fails) changed=True latency=54236ms regressions=0
- B4: STILL-BROKEN (documented check still fails) changed=True latency=23486ms regressions=0
- B5: STILL-BROKEN (documented check still fails) changed=True latency=113559ms regressions=0
- B6: STILL-BROKEN (documented check still fails) changed=True latency=73621ms regressions=0

Fixed 0/6, regressions 2.
## Verdict: 003 verdict STANDS — cleaner stays opt-in (per 004-protocol rule).
