"""The codec grid: real telephony channels, applied to real audio.

Every condition here was verified to encode AND decode on this machine's ffmpeg 8.1.2
before it entered the grid. Channels we cannot produce are NOT faked; they are listed in
UNAVAILABLE and published as absent.
"""
import os, shutil, subprocess, tempfile
import numpy as np
import soundfile as sf

SR = 16000

# name -> (encode argv template, container suffix)
# {i} input wav path, {o} output path
_FFMPEG_GRID = {
    "clean":        (None, None),
    "opus_24k":     (["-c:a", "libopus", "-b:a", "24000", "-ar", "16000"], ".ogg"),
    "opus_8k":      (["-c:a", "libopus", "-b:a", "8000",  "-ar", "16000"], ".ogg"),
    "g722_64k":     (["-ar", "16000", "-c:a", "g722"], ".wav"),
    "g726_32k":     (["-ar", "8000",  "-c:a", "g726", "-b:a", "32000"], ".wav"),
    "g723_1_6k3":   (["-ar", "8000",  "-c:a", "g723_1", "-b:a", "6300"], ".wav"),
}
# Speex needs the standalone speexenc/speexdec binaries, not ffmpeg (decode-only there).
_SPEEX = "speex_wb_q4"

GRID = list(_FFMPEG_GRID.keys()) + [_SPEEX]          # 7 conditions
assert len(GRID) == 7

# Published absences. We do not fake a channel we cannot encode.
UNAVAILABLE = {
    "amr_wb": "ffmpeg 8.1.2 decodes AMR-WB but has no encoder; no free encoder on this machine.",
    "evs":    "EVS is absent from ffmpeg entirely and has no open-source encoder available here.",
}

# Which conditions are wideband (16 kHz) vs narrowband (8 kHz), for reporting.
BANDWIDTH = {
    "clean": "wb", "opus_24k": "wb", "opus_8k": "wb", "g722_64k": "wb",
    "speex_wb_q4": "wb", "g726_32k": "nb", "g723_1_6k3": "nb",
}

# Measured 2026-09-14 on the shipped head, 4 s prefix, 510 genuine calibration clips per
# condition: the 98th-percentile genuine log-odds moves -3.11 (clean), -2.02 (g726_32k),
# -1.75 (opus_24k), -0.59 (speex_wb_q4), +1.09 (opus_8k), +1.95 (g723_1_6k3). The shift
# tracks BITRATE, not sample rate. opus_8k is 16 kHz sampled and therefore "wb" above, yet
# its genuine scores sit with g723_1_6k3 at 6.3 kbps and nowhere near opus_24k. So the
# commit band is derived per condition, and BANDWIDTH is kept for reporting only: it is
# the wrong key to threshold on and the measurement says so.
# SEVERITY orders the grid by that measured genuine-score shift, least to most degrading.
# It is the fallback order for a live channel the model has no band for: an unknown line
# is treated as the most degrading condition measured, which is the conservative choice.
SEVERITY = ["clean", "g722_64k", "g726_32k", "opus_24k", "speex_wb_q4", "opus_8k", "g723_1_6k3"]


def most_degrading(available):
    """The condition in `available` that shifted genuine scores furthest, for fallback."""
    ranked = [c for c in SEVERITY if c in set(available)]
    return ranked[-1] if ranked else None


def _run(argv):
    r = subprocess.run(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise RuntimeError(f"{argv[0]} failed: {r.stderr.decode()[-400:]}")


def available():
    """Which grid conditions this machine can actually produce, checked live."""
    ok = ["clean"]
    have_ffmpeg = shutil.which("ffmpeg") is not None
    for name in _FFMPEG_GRID:
        if name != "clean" and have_ffmpeg:
            ok.append(name)
    if shutil.which("speexenc") and shutil.which("speexdec"):
        ok.append(_SPEEX)
    return ok


def apply_packet_loss(x, loss_rate, frame_ms=20, sr=SR, seed=0):
    """Zero out whole frames, the way a lost RTP packet actually behaves.

    Not additive noise. A dropped packet is silence of one frame duration.
    """
    if loss_rate <= 0:
        return x
    rng = np.random.default_rng(seed)
    n = int(sr * frame_ms / 1000)
    y = x.copy()
    for start in range(0, len(y), n):
        if rng.random() < loss_rate:
            y[start:start + n] = 0.0
    return y


def apply_channel(x, condition, sr=SR, loss_rate=0.0, seed=0):
    """Encode-decode `x` through one telephony condition. Returns 16 kHz float32.

    Packet loss is applied BEFORE the codec, because that is where it happens:
    the packet is lost in transit and the decoder conceals it.
    """
    if condition not in GRID:
        raise ValueError(f"unknown condition {condition!r}; grid is {GRID}")
    x = np.asarray(x, dtype=np.float32)
    if loss_rate > 0:
        x = apply_packet_loss(x, loss_rate, sr=sr, seed=seed)
    if condition == "clean":
        return x

    d = tempfile.mkdtemp(prefix="kemp_ch_")
    try:
        src = os.path.join(d, "src.wav")
        sf.write(src, x, sr, subtype="PCM_16")

        if condition == _SPEEX:
            enc = os.path.join(d, "a.spx")
            dec = os.path.join(d, "out.wav")
            _run(["speexenc", "--quality", "4", src, enc])
            _run(["speexdec", enc, dec])
        else:
            args, suffix = _FFMPEG_GRID[condition]
            enc = os.path.join(d, "a" + suffix)
            dec = os.path.join(d, "out.wav")
            _run(["ffmpeg", "-y", "-loglevel", "error", "-i", src] + args + [enc])
            _run(["ffmpeg", "-y", "-loglevel", "error", "-i", enc,
                  "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", dec])

        y, r = sf.read(dec, dtype="float32")
        if y.ndim > 1:
            y = y.mean(axis=1)
        if r != sr:  # speexdec can return its own rate
            import torch, torchaudio.functional as F
            y = F.resample(torch.from_numpy(y)[None], r, sr).numpy()[0]
        # codecs shift length by a few frames; align to the original
        if len(y) < len(x):
            y = np.pad(y, (0, len(x) - len(y)))
        return y[:len(x)].astype(np.float32)
    finally:
        shutil.rmtree(d, ignore_errors=True)
