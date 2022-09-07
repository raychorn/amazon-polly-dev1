"""Getting Started Example for Python 2.7+/3.3+"""
import random
from genericpath import exists
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from datetime import datetime
from tempfile import gettempdir

from voiceutils import utils

SPEECH_DIR = 'speech2'
TEXTFILE = 'sample_story.txt'
TEXTTYPE_SSML = 'ssml' # 'ssml' or 'text'
VOICES_FILENAME = 'Polly Voices - Sheet1.csv'

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


speakers = [d for d in voices if (d.get('Language').find('English') > -1) and (str(d.get('Neural')).lower() == 'yes')]

random.seed(int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000))
a_speaker = random.choice(speakers)

_text_to_read = utils.read_file(text_to_read) if os.path.exists(text_to_read) else 'Cannot find the text file.'
__text_to_read = _text_to_read


def text_to_ssml(sometext, pause_secs=PAUSE_SECS):
    from ssml_builder.core import Speech

    speech = Speech()
    
    lines = sometext.split('\n')
    
    for l in lines:
        l = l.strip()
        if (len(l) == 0):
            speech.p(l)
            pass
        else:
            speech.add_text(l)
            #speech.prosody(value=l, volume='loud')
            speech.pause(str(pause_secs) + 's')
    
    return speech.speak()

_text_to_read = text_to_ssml(_text_to_read)


def request_polly_speak(profile_name=None, region_name=None, voice=None, text_to_read=None, textType=None, output_filename=None):
    session = Session(profile_name=profile_name)
    polly = session.client("polly", region_name=region_name)
    
    textType = 'text' if (not textType in ['ssml', 'text']) else textType

    try:
        # Request speech synthesis
        is_standard = str(voice.get('Standard', 'no')).lower() == 'yes'
        is_neural = str(voice.get('Neural', 'no')).lower() == 'yes'
        is_male = str(voice.get('Gender', 'neuter')).lower() == 'male'
        is_female = str(voice.get('Gender', 'neuter')).lower() == 'female'
        assert is_male or is_female, "ERROR: The voice '%s' is not male or female." % (voice.get('voiceid'))
        _text_to_read = text_to_read
        if (is_neural):
            response = polly.synthesize_speech(Text=_text_to_read, OutputFormat="mp3", VoiceId=voice.get('voiceid'),
                                                Engine='neural' if str(voice.get('Standard', 'no')).lower() == 'yes' else 'neural',
                                                TextType=textType)
        elif (is_standard):
            response = polly.synthesize_speech(Text=_text_to_read, OutputFormat="mp3", VoiceId=voice.get('voiceid'), TextType=textType)
        else:
            assert is_standard or is_neural, "ERROR: The voice '%s' is not standard or neural." % (voice.get('voiceid'))
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        return error, -1

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                print('BEGIN: Writing speech to "%s".' % (output_filename))
                file_size = -1
                try:
                    # Open a file for writing the output as a binary stream
                    with open(output_filename, "wb") as file:
                        file.write(stream.read())
                            
                    file_size = os.path.getsize(output_filename)
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)
                    sys.exit(-1)
                print('DONE: Writing speech to "{}" ({}).\n\n'.format(output_filename, file_size))
                return output_filename, file_size
            
    return None, -1

if (0):
    output_filename = os.path.join(this_dir, "{}{}{}_speech.mp3".format(speech_dir, os.sep, a_speaker.get('voiceid')))
    fname, fsize = request_polly_speak(profile_name="vyperlogix", region_name='us-west-2', voice=a_speaker, text_to_read=_text_to_read, textType=TEXTTYPE_SSML, output_filename=output_filename)
    if (not os.path.exists(fname)):
        print(fname)
        print(fsize)
    assert (os.path.exists(fname)) , "ERROR: The file '%s' does not exist." % (fname)
else:
    for a_speaker in speakers:
        output_filename = os.path.join(this_dir, "{}{}{}{}{}{}{}_speech.mp3".format(speech_dir, os.sep, a_speaker.get('Language'), os.sep, a_speaker.get('Gender'), os.sep, a_speaker.get('voiceid')))
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        fname, fsize = request_polly_speak(profile_name="vyperlogix", region_name='us-west-2', voice=a_speaker, text_to_read=_text_to_read, textType=TEXTTYPE_SSML, output_filename=output_filename)
        if (not os.path.exists(fname)):
            print(fname)
            print(fsize)
        assert (os.path.exists(fname)) , "ERROR: The file '%s' does not exist." % (fname)
        
print('Done.')