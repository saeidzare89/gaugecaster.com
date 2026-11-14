"""Writes src/index.html: the home page with its drawn pictures of the app
(not screenshots: shapes in the site's own colours, so they follow light
and dark and stay sharp). Run from the site's folder:
    python _tools/index.py && python ../Gauge/tool/make_site.py .
"""
import math
import random
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent


def bars(x0, x1, mid, height, seed, step=6.0, width=3.2, env=None):
    """A clip's waveform: mirrored rounded bars between x0 and x1."""
    rnd = random.Random(seed)
    out = []
    n = max(1, int((x1 - x0 - 6) / step))
    for i in range(n):
        t = i / max(1, n - 1)
        e = env(t) if env else (0.35 + 0.65 * math.sin(math.pi * min(1, t * 1.1)) ** 0.6)
        h = max(2.5, height * e * rnd.uniform(0.35, 1.0))
        x = x0 + 4 + i * step
        out.append(f'<rect x="{x:.1f}" y="{mid - h / 2:.1f}" width="{width}" height="{h:.1f}" rx="1.6"/>')
    return "".join(out)


def clip(x0, x1, y, h, cls, seed, label=None, fade=None, env=None):
    parts = [f'<g class="{cls}"><rect class="clip" x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" rx="10"/>']
    parts.append(f'<g class="wave">{bars(x0, x1, y + h / 2 + 4, h - 26, seed, env=env)}</g>')
    if label:
        parts.append(f'<text class="clip-name" x="{x0 + 9}" y="{y + 16}">{label}</text>')
    if fade == "out":
        parts.append(f'<path class="fade" d="M{x1 - 46} {y + 4} L{x1 - 2} {y + h - 2}"/>')
    if fade == "in":
        parts.append(f'<path class="fade" d="M{x0 + 2} {y + h - 2} L{x0 + 40} {y + 4}"/>')
    parts.append("</g>")
    return "".join(parts)


def studio_svg():
    W, top, lane, gap, left = 1000, 96, 78, 10, 170
    ys = [top + i * (lane + gap) for i in range(3)]
    g = []
    # The bar: title, transport, time, Export.
    g.append('<text class="t-title" x="24" y="40">Night trains</text>')
    g.append('<text class="t-sub" x="24" y="60">3 tracks · 01:08</text>')
    g.append('<circle class="b-play" cx="430" cy="40" r="19"/><path class="b-play-i" d="M424 31 L438 40 L424 49 Z"/>')
    g.append('<circle class="b-rec" cx="478" cy="40" r="19"/><text class="b-rec-t" x="478" y="44.5">REC</text>')
    g.append('<rect class="b-time" x="512" y="22" width="118" height="36" rx="18"/><text class="t-time" x="571" y="46">00:34.2</text>')
    g.append('<rect class="b-export" x="866" y="22" width="110" height="36" rx="18"/><text class="b-export-t" x="921" y="45.5">Export</text>')
    # The ruler and its chapters.
    for x, name in [(left, "Cold open"), (415, "Vienna to Rome"), (735, "Listener question")]:
        g.append(f'<path class="flag" d="M{x - 6} 76 L{x + 6} 76 L{x} 84 Z"/><text class="chapter" x="{x + 9}" y="83">{name}</text>')
        g.append(f'<line class="chapter-line" x1="{x}" y1="86" x2="{x}" y2="{ys[2] + lane}"/>')
    # Track names.
    for y, name, sub, cls in [(ys[0], "Michael", "Shure MV7", "v1"), (ys[1], "Bella", "Rode PodMic", "v2"), (ys[2], "Music", "ducks under voices", "mu")]:
        g.append(f'<g class="{cls}"><rect class="lane-mark" x="24" y="{y + 10}" width="4" height="{lane - 20}" rx="2"/></g>')
        g.append(f'<text class="lane-name" x="40" y="{y + 34}">{name}</text><text class="lane-sub" x="40" y="{y + 54}">{sub}</text>')
    # Clips.
    for x0, x1, s in [(232, 330, 1), (440, 500, 2), (560, 610, 3), (760, 852, 4)]:
        g.append(clip(x0, x1, ys[0] + 4, lane - 8, "v1", s, "Michael" if x1 - x0 > 80 else None))
    for x0, x1, s in [(336, 410, 11), (505, 552, 12), (616, 730, 13), (860, 944, 14)]:
        g.append(clip(x0, x1, ys[1] + 4, lane - 8, "v2", s, "Bella" if x1 - x0 > 70 else None))
    bed = lambda t: 0.55 + 0.45 * abs(math.sin(t * 9))
    g.append(clip(left, 300, ys[2] + 4, lane - 8, "mu", 21, "Music", fade="out", env=bed))
    g.append(clip(870, 990, ys[2] + 4, lane - 8, "mu", 22, "Music", fade="in", env=bed))
    # The playhead, moving.
    g.append(f'<g class="playhead"><path d="M{left} 88 l-7 -8 h14 z"/><line x1="{left}" y1="88" x2="{left}" y2="{ys[2] + lane}"/></g>')
    h = ys[2] + lane + 16
    return (f'<svg class="mock-svg" viewBox="0 0 {W} {h}" role="img" aria-label="A drawing of GaugeCaster\'s Studio: Michael and Bella on their own tracks, music under them, chapters on the ruler.">'
            + "".join(g) + "</svg>")


def track_row(initials, name, sub, cls, seed, clips):
    """A Compact track card: picture, name, microphone, its clips."""
    g = []
    for x0, x1 in clips:
        g.append(f'<rect class="clip" x="{x0}" y="4" width="{x1 - x0}" height="52" rx="12"/>')
        g.append(f'<g class="wave">{bars(x0, x1, 30, 40, seed + x0, step=5.2, width=2.6)}</g>')
    wave = f'<svg class="row-wave" viewBox="0 0 600 60" preserveAspectRatio="none" aria-hidden="true"><g class="{cls}">{"".join(g)}<line class="ph" x1="250" y1="0" x2="250" y2="60"/></g></svg>'
    return (f'<div class="row {cls}"><span class="avatar">{initials}</span>'
            f'<span class="who"><b>{name}</b><small>{sub}</small></span>{wave}</div>')


def compact_big():
    return f'''<figure class="mock mock-compact mock-hero-shot reveal" role="img" aria-label="A drawing of GaugeCaster's Compact view: four steps, Michael, Bella and the music on their own tracks, and the player with REC.">
  <div class="bar"><span class="title"><b>Night trains</b><small>3 tracks · 01:08</small></span><span class="views"><span class="on">Compact</span><span>Studio</span></span><span class="export">Export</span></div>
  <div class="steps"><span class="on">1 Record</span><span>2 Tidy up</span><span>3 Sound better</span><span>4 Share</span></div>
  {track_row("MI", "Michael", "Shure MV7", "v1", 31, [(40, 150), (200, 236), (300, 360), (470, 540)])}
  {track_row("BE", "Bella", "Rode PodMic", "v2", 32, [(150, 196), (240, 296), (364, 466), (544, 590)])}
  {track_row("MU", "Music", "Ducks under voices", "mu", 33, [(0, 120), (500, 600)])}
  <div class="recbar"><span class="rec-time">00:34</span><span class="play-btn" aria-hidden="true"></span><span class="rec-btn">REC</span></div>
</figure>'''


def record_html():
    return f'''<div class="mock mock-record" role="img" aria-label="A drawing of two microphones recording at once, each to its own track.">
    <div class="mic v1"><span class="avatar">MI</span><span class="who"><b>Michael</b><small>Shure MV7</small></span><span class="level"><i style="--l:72%"></i></span></div>
    <div class="mic v2"><span class="avatar">BE</span><span class="who"><b>Bella</b><small>Rode PodMic</small></span><span class="level"><i style="--l:58%"></i></span></div>
    <div class="recbar"><span class="rec-btn">REC</span><span class="rec-note">Recording 2 tracks together</span></div>
  </div>'''


def sound_html():
    rnd = random.Random(5)
    noisy, clean = [], []
    for i in range(110):
        t = i / 109
        voice = max(0.0, math.sin(t * 22) * math.sin(t * 3.1 + 0.5))
        v = voice * rnd.uniform(0.5, 1.0)
        n = rnd.uniform(0.10, 0.22) + (0.25 if i % 17 == 0 else 0)
        x = 6 + i * 5.4
        hn = max(3, 64 * max(v, n))
        hc = max(1.5, 64 * v * 0.92)
        noisy.append(f'<rect x="{x:.1f}" y="{40 - hn / 2:.1f}" width="2.8" height="{hn:.1f}" rx="1.4"/>')
        clean.append(f'<rect x="{x:.1f}" y="{40 - hc / 2:.1f}" width="2.8" height="{hc:.1f}" rx="1.4"/>')
    return f'''<div class="mock mock-sound" role="img" aria-label="A drawing of GaugeCaster's sound check: a noisy waveform before, a clean one after, and the fixes it made.">
    <div class="ab"><span class="ab-label">Before</span><svg viewBox="0 0 600 80" aria-hidden="true"><g class="noisy">{"".join(noisy)}</g></svg></div>
    <div class="ab"><span class="ab-label">After</span><svg viewBox="0 0 600 80" aria-hidden="true"><g class="clean">{"".join(clean)}</g></svg></div>
    <div class="chips"><span>✓ Background noise</span><span>✓ 60 Hz hum</span><span>✓ Harsh S sounds</span><span>✓ Pops</span></div>
  </div>'''


def publish_html():
    rows = "".join(f'<li><span class="tick">✓</span><span class="at">{t}</span>{n}</li>' for t, n in [("00:00", "Cold open"), ("00:18", "Vienna to Rome"), ("00:47", "Listener question"), ("00:57", "Goodnight")])
    return f'''<div class="mock mock-publish" role="img" aria-label="A drawing of GaugeCaster's Publish card: the show's picture, the episode, its chapters and Upload to Podbean.">
    <div class="ep"><span class="art"><i></i><b>Small<br>Hours</b></span><span class="ep-text"><small>Small Hours · S2 E12</small><b>Night trains</b><small class="lufs">−16.0 LUFS ✓</small></span></div>
    <ul class="chapters">{rows}</ul>
    <div class="upload"><span class="up-btn">Upload to Podbean</span><span class="up-alt">Save as draft</span></div>
  </div>'''


page = f'''<!-- GaugeCaster | GaugeCaster records, edits and publishes podcasts and narration on Windows, Android and Linux. | home -->
<section class="hero">
  <div>
    <h1>Record it, clean it up, <em>put it out.</em></h1>
    <p class="lede">GaugeCaster is a recording studio for podcasts and narration. Each voice gets its own track, a few clicks make it sound better, and the finished episode goes to your podcast host at the right loudness, with its picture and chapters.</p>
    <span class="status">In pre-release testing</span>
    <div class="platforms"><span>Windows</span><span>Android</span><span>Linux</span><span>iPhone and Mac later</span></div>
  </div>
  <div class="hero-art">
    <div class="meter">
      {Path(SITE / "_tools" / "wave.svg").read_text(encoding="utf-8").strip()}
      <div class="row-m"><span>Episode 12 · mixed</span><span class="lufs-big">−16.0 LUFS</span></div>
      <div class="row-m"><span>Podcast target</span><span>−1.0 dBTP peak</span></div>
    </div>
  </div>
</section>

{compact_big()}

<section class="split reveal">
  <div class="split-text">
    <span class="tag">Record</span>
    <h2>Every voice on its own track</h2>
    <p>Two microphones, three, or the inputs of one interface: each voice records onto its own track, kept in step, so you can fix one person without touching the other.</p>
  </div>
  {record_html()}
</section>

<section class="split flip reveal">
  <div class="split-text">
    <span class="tag">Sound</span>
    <h2>Cleaner in a click</h2>
    <p>GaugeCaster listens to each take and finds what is wrong: room noise, mains hum, harsh S sounds, pops. Fix all takes care of them; every stage can be set by hand.</p>
  </div>
  {sound_html()}
</section>

<section class="split reveal">
  <div class="split-text">
    <span class="tag">Publish</span>
    <h2>From the last edit to your feed</h2>
    <p>Your markers become chapters. The MP3 comes out at podcast loudness with the title, picture and chapters inside, and goes straight to your host.</p>
    <p class="muted">Podbean, Buzzsprout and Transistor; any other host takes the exported file.</p>
  </div>
  {publish_html()}
</section>

<h2 class="section-title reveal">And also</h2>
<div class="features">
  <div class="feature reveal" style="--d:0">
    <span class="tag">Edit</span>
    <h3>Compact or Studio</h3>
    <p>Compact walks you from recording to sharing in four steps. Studio is a full timeline: split, trim, fade, markers, a mixer, undo for everything.</p>
  </div>
  <div class="feature reveal" style="--d:1">
    <span class="tag">Read</span>
    <h3>From a script</h3>
    <p>A teleprompter that scrolls with you, a take per paragraph, the best take of each laid out in order.</p>
  </div>
  <div class="feature reveal" style="--d:2">
    <span class="tag">Play</span>
    <h3>A sound pad</h3>
    <p>Intros, stings and applause on keys 1 to 9 while you record; music beds duck under your voice by themselves.</p>
  </div>
</div>

<section class="band reveal">
  <div>
    <h2>Your recordings stay yours</h2>
    <p>No account, no cloud, no tracking. Projects live in a folder on your own device, and nothing leaves it unless you export, share or upload it. <a href="/privacy.html">Privacy</a></p>
  </div>
  <a class="button" href="/support.html">Ask to try it</a>
</section>
'''
(SITE / "src" / "index.html").write_text(page, encoding="utf-8", newline="\n")
print("src/index.html written")
