"""
Experiments for ASL/English bilinguals

Requires Python 2.7
"""
__author__ = "Benjamin Anible (benjamin.anible@gmail.com)"
__copyright__ = "Copyright 2015 Benjamin Anible"
__contributors__ = [
    "Benjamin Anible",
    "Gemma Anible"
]
__license__ = "BSD 3-Clause"
__version__ = "0.0.1"


from .protocol_1 import TranslationRecognition
from .protocol_2_audio import TranslationProductionFromAudio
from .protocol_2_video import TranslationProductionFromVideo
from .protocol_3 import PictureNaming
from .protocol_3_audio import PictureNamingWithAudio
