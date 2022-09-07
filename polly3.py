"""Getting Started Example for Python 2.7+/3.3+

Polly3 - Scripted support producing one MP3 at a time.

"""
import random
import os
import sys
import subprocess
from datetime import datetime
from tempfile import gettempdir

from voiceutils import utils
from voiceutils import polly

SPEECH_DIR = 'speech3'
TEXTFILE = 'sample_script.txt'
TEXTTYPE_SSML = 'ssml' # 'ssml' or 'text'
VOICES_FILENAME = 'Polly Voices - Sheet1.csv'

PROFILE = 'vyperlogix'
REGION = 'us-west-2'

root_dir = os.path.dirname(os.path.abspath(__file__))
speech_dir = os.path.join(root_dir, SPEECH_DIR)

if (not os.path.exists(speech_dir)):
    os.mkdir(speech_dir)
else:
    for f in os.listdir(speech_dir):
        os.remove(os.path.join(speech_dir, f))

text_to_read = os.path.join(root_dir, TEXTFILE)

PAUSE_SECS = 0.5

this_dir = root_dir
    
voices, __is__ = utils.read_csv(os.path.join(root_dir, VOICES_FILENAME))

if (__is__):
    if (os.path.exists(os.path.join(root_dir, VOICES_FILENAME.replace('.csv', '.csv.bak')))):
        os.remove(os.path.join(root_dir, VOICES_FILENAME.replace('.csv', '.csv.bak')))
    os.rename(os.path.join(root_dir, VOICES_FILENAME), os.path.join(root_dir, VOICES_FILENAME.replace('.csv', '.csv.bak')))
    utils.write_csv(os.path.join(root_dir, VOICES_FILENAME), voices)


#speakers = [d for d in voices if (d.get('Language').find('English') > -1) and (str(d.get('Neural')).lower() == 'yes')]
speakers = [d for d in voices]

_text_to_read = utils.read_file(text_to_read) if os.path.exists(text_to_read) else 'Cannot find the text file.'
__text_to_read = _text_to_read


def script_to_ssml_for_speaker(sometext, pause_secs=PAUSE_SECS, num=0, voices=[]):
    '''
    num is the speaker number from the script.
    '''
    VOICE_TOKEN = '==voice=='
    from ssml_builder.core import Speech

    speech = Speech()
    
    lines = sometext.split('\n')
    
    _num = 0
    __is__ = False
    __has__ = False
    voiceid = None
    speaker = None
    for l in lines:
        l = l.strip()
        if (l.startswith(VOICE_TOKEN + '')):
            _num += 1
            if (not voiceid) and (num == _num):
                voiceid = l.replace(VOICE_TOKEN + ' ', '').strip()
                speaker = [d for d in voices if (str(d.get('voiceid')).lower() == voiceid.lower())]
                assert len(speaker) == 1, "ERROR: The voice '%s' is not in the list of voices." % (voiceid)
        elif (__is__) and (not __has__) and (len(l) == 0):
            speech.pause(str(pause_secs) + 's')
            __has__ = True
        elif (num == _num):
            try:
                speech.add_text(l)
                #speech.voice(value=l, name=voiceid)
            except:
                speech.voice(value='The chosen speaker could not speak due to an error. Please check the valid voice names again and retry.', name='Carla', is_nested=True)
            __is__ = True
    
    return speech.speak(), speaker[0] if (isinstance(speaker, list)) else None, num, __is__

num = 1
__is__ = True
while(__is__):
    current_speech, speaker, num, __is__  = script_to_ssml_for_speaker(__text_to_read, num=num, voices=speakers)
    if (__is__):
        output_filename = os.path.join(this_dir, "{}{}{}_speech_{}.mp3".format(speech_dir, os.sep, speaker.get('voiceid'), num))
        polly.request_polly_speak(profile_name=PROFILE, region_name=REGION, voice=speaker, text_to_read=current_speech, textType=TEXTTYPE_SSML, output_filename=output_filename)
        num += 1


print('Done.')