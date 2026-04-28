"""telegrapher — bidirectional Natural Language ↔ Telegraph English compression.

Public API:

    from telegrapher import Telegrapher

    tg = Telegrapher()                              # default model from HF Hub
    tg = Telegrapher(model="org/te-bidi")           # explicit single bidi model
    tg = Telegrapher(model_in="org/te-compress",
                     model_out="org/te-expand")     # two unidirectional models

    te = tg.compress(text, level="L3")
    nl = tg.expand(te)
    ratio = tg.ratio(text, te)
"""
from telegrapher._version import __version__
from telegrapher.core import Telegrapher

__all__ = ["Telegrapher", "__version__"]
