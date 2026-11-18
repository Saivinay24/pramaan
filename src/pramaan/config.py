"""Single source of truth for every tunable in Pramaan."""
SR = 16000
CLIP_S = 4.0

# frontend
SSL_MODEL = "facebook/wav2vec2-xls-r-300m"
SSL_LAYER = 5
DEVICE = "mps"
DTYPE = "fp32"

# streaming
HOP_S = 0.5
MAX_CONTEXT_S = 8.0
MIN_COMMIT_S = 1.5
STABILITY_WINDOW = 3
STABILITY_TOL = 0.08

# prevention policy
CHALLENGE_AFTER_S = 2.0
CHALLENGE_DEADLINE_S = 8.0
