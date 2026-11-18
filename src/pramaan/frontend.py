"""Frozen SSL frontend.

Pascu et al. (Interspeech 2024): freeze wav2vec2/XLS-R, train <2,000 parameters on top,
30.9% -> 8.8% mean OOD EER. Nothing here trains. Nothing here needs a GPU.

Measured on this machine (eval/results/d1_rtf.json): RTF 0.0246 on MPS fp32 at a 4 s window.
"""
import threading
import numpy as np
import torch

from .config import SSL_MODEL, SSL_LAYER, DEVICE, DTYPE, SR, MAX_CONTEXT_S

_LOCK = threading.Lock()
_CACHE = {}


def _resolve_device(device):
    if device == "mps" and not torch.backends.mps.is_available():
        return "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        return "cpu"
    return device


class Frontend:
    """Frozen XLS-R. Emits one fixed-width embedding per audio prefix.

    IMPORTANT: variable-length input, never tile-padded. rs-10257178 shows that
    repeating a short prefix to fill a fixed window manufactures ~83% of the apparent
    streaming advantage. XLS-R takes variable length, so we simply do not pad.
    """

    def __init__(self, model_name=SSL_MODEL, layer=SSL_LAYER, device=DEVICE, dtype=DTYPE):
        self.model_name = model_name
        self.layer = layer
        self.device = _resolve_device(device)
        self.torch_dtype = torch.float16 if dtype == "fp16" else torch.float32
        key = (model_name, self.device, dtype)
        with _LOCK:
            if key not in _CACHE:
                from transformers import AutoModel
                m = AutoModel.from_pretrained(model_name)
                m.eval()
                m.to(device=self.device, dtype=self.torch_dtype)
                for p in m.parameters():
                    p.requires_grad_(False)
                _CACHE[key] = m
            self.model = _CACHE[key]
        self.dim = self.model.config.hidden_size * 2   # mean and std pooled

    @torch.inference_mode()
    def embed(self, wav, sr=SR):
        """wav: 1-D float32 at 16 kHz. Returns a (dim,) float32 numpy vector."""
        x = np.asarray(wav, dtype=np.float32)
        if x.ndim > 1:
            x = x.mean(axis=-1)
        # XLS-R's conv stack needs a minimum receptive field; below this there is no
        # honest feature to extract, and we refuse rather than pad.
        if len(x) < int(0.4 * sr):
            raise ValueError(f"prefix too short to embed: {len(x)/sr:.2f}s (min 0.40s)")
        if len(x) > int(MAX_CONTEXT_S * sr):
            x = x[-int(MAX_CONTEXT_S * sr):]          # trailing context window
        # per-utterance normalisation, the wav2vec2 convention
        x = (x - x.mean()) / (x.std() + 1e-7)
        t = torch.from_numpy(x)[None].to(device=self.device, dtype=self.torch_dtype)
        out = self.model(t, output_hidden_states=True)
        h = out.hidden_states[self.layer][0].float()   # (frames, hidden)
        v = torch.cat([h.mean(0), h.std(0)], dim=-1)
        return v.cpu().numpy().astype(np.float32)

    @torch.inference_mode()
    def embed_batch(self, wavs, sr=SR):
        return np.stack([self.embed(w, sr) for w in wavs])
