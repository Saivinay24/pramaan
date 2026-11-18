"""Live challenge-response: what Pramaan does when the Gate cannot decide.

A caller is asked to say something that could not have been pre-synthesised: a random digit
string and a random concrete word, in the caller's own language. The response is scored as
a second, fresh observation. A pre-rendered clip cannot answer; a live cloning pipeline
must parse, synthesise and deliver inside human reaction time.
"""
import hashlib, random
from dataclasses import dataclass, asdict

TEMPLATES = {
    "hindi": "कृपया ये अंक बोलिए: {digits}। फिर ये शब्द बोलिए: {word}",
    "tamil": "தயவுசெய்து இந்த எண்களைச் சொல்லுங்கள்: {digits}. பிறகு இந்த சொல்: {word}",
    "telugu": "దయచేసి ఈ అంకెలు చెప్పండి: {digits}. తరువాత ఈ పదం: {word}",
    "english": "Please say these digits: {digits}. Then say this word: {word}",
}
LEXICON = {
    "hindi": ["समुद्र", "खिड़की", "बादल", "पहाड़", "चाबी", "दरवाज़ा", "किताब", "सूरज",
              "नदी", "पत्ता", "घड़ी", "रास्ता", "फूल", "चिड़िया", "बर्तन", "सीढ़ी"],
    "tamil": ["கடல்", "ஜன்னல்", "மேகம்", "மலை", "சாவி", "கதவு", "புத்தகம்", "சூரியன்",
              "ஆறு", "இலை", "கடிகாரம்", "பாதை", "பூ", "பறவை", "பாத்திரம்", "படிக்கட்டு"],
    "telugu": ["సముద్రం", "కిటికీ", "మేఘం", "కొండ", "తాళం", "తలుపు", "పుస్తకం", "సూర్యుడు",
               "నది", "ఆకు", "గడియారం", "దారి", "పువ్వు", "పక్షి", "పాత్ర", "మెట్టు"],
    "english": ["ocean", "window", "cloud", "mountain", "key", "door", "book", "sun",
                "river", "leaf", "clock", "road", "flower", "bird", "vessel", "ladder"],
}
DIGITS = 4
# One task template per language, deliberately. The parent repo carries three
# (digits_then_word, word_then_digits, digits_reversed) and so reports 480,000. Pramaan
# ships one because the demo operator reads the challenge aloud from the console and a
# reversed-digit variant changes what the caller is being asked to do mid-demo. Adding the
# other two is a one-line change here and would take the space to 480,000; it is deferred
# until after the national round rather than landed days before a live demo.
N_TEMPLATES = 1


@dataclass
class Challenge:
    challenge_id: str
    language: str
    text: str
    digits: str
    word: str
    issued_at_s: float
    deadline_s: float
    space: int = 0          # carried so the console never hardcodes the space size
    state: str = "ISSUED"
    p_response: float = None
    verdict: str = None

    def to_dict(self):
        return asdict(self)


def space_size(language="hindi"):
    """Exact count of distinct challenges. Arithmetic, not a claim.

    10^4 digit strings x 16 lexicon words x 1 task template = 160,000. That is what this
    module ships and what every Pramaan artifact quotes. The parent repo's ChallengeBank
    carries three task templates per language and therefore reports 480,000; that is the
    parent repo's number for the parent repo's code and it must never be quoted here.
    """
    return (10 ** DIGITS) * len(LEXICON[language]) * N_TEMPLATES


def draw(language="hindi", now_s=0.0, deadline_s=8.0, rng=None):
    rng = rng or random.Random()
    language = language if language in TEMPLATES else "hindi"
    word = rng.choice(LEXICON[language])
    digits = " ".join(str(rng.randrange(10)) for _ in range(DIGITS))
    text = TEMPLATES[language].format(digits=digits, word=word)
    cid = hashlib.sha256(f"{text}{now_s}{rng.random()}".encode()).hexdigest()[:10]
    return Challenge(cid, language, text, digits, word, float(now_s), float(now_s + deadline_s),
                     space=space_size(language))
