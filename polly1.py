"""Getting Started Example for Python 2.7+/3.3+"""
from genericpath import exists
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir

VOICES_FILENAME = 'Polly Voices - Sheet1.csv'

root_dir = os.path.dirname(os.path.abspath(__file__))
speech_dir = os.path.join(root_dir, 'speech')

if (not os.path.exists(speech_dir)):
    os.mkdir(speech_dir)
else:
    for f in os.listdir(speech_dir):
        os.remove(os.path.join(speech_dir, f))

text_to_read = os.path.join(root_dir, 'text_to_read.txt')

this_dir = root_dir

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()


def read_csv(filename):
    import csv

    resp = []

    __is__ = False
    
    assert (os.path.exists(filename)) , "ERROR: The file '%s' does not exist." % (filename)
    with open(filename) as csv_file:
        cols = []
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                cols = row
            else:
                line_count += 1
                num_compound = 0
                for i,r in enumerate(row):
                    if ('\n' in r):
                        row[i] = r.split('\n')
                        num_compound += 1
                    elif ('"' in r):
                        row[i] = r.replace('"', '')
                        __is__ = True
                if (num_compound > 0):
                    assert not isinstance(row[0], list), "ERROR: The first column must be a single value."
                    n = max(len(row[i]) for i in range(1,len(row)))
                    rows = []
                    for i in range(n):
                        _row = [row[0]]
                        for j in range(1, len(row)-1):
                            _row.append(row[j][i])
                        rows.append(_row)
                    for _row in rows:
                        resp.append(dict(zip(cols, _row)))
                    __is__ = True
                    continue
                _d_ = dict(list(zip(cols, row)))
                resp.append(_d_)
    return resp, __is__
    
    
def write_csv(filaneme, data):
    import csv

    with open(filaneme, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data[1:])

    
voices, __is__ = read_csv(os.path.join(root_dir, VOICES_FILENAME))

if (__is__):
    if (os.path.exists(os.path.join(root_dir, VOICES_FILENAME.replace('.csv', '.csv.bak')))):
        os.remove(os.path.join(root_dir, VOICES_FILENAME.replace('.csv', '.csv.bak')))
    os.rename(os.path.join(root_dir, VOICES_FILENAME), os.path.join(root_dir, VOICES_FILENAME.replace('.csv', '.csv.bak')))
    write_csv(os.path.join(root_dir, VOICES_FILENAME), voices)
    
# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="vyperlogix")
polly = session.client("polly", region_name='us-west-2')

_text_to_read = read_file(text_to_read) if os.path.exists(text_to_read) else 'Cannot find the text file.'
__text_to_read = _text_to_read
for voice in voices:
    try:
        # Request speech synthesis
        is_standard = str(voice.get('Standard', 'no')).lower() == 'yes'
        is_neural = str(voice.get('Neural', 'no')).lower() == 'yes'
        is_male = str(voice.get('Gender', 'neuter')).lower() == 'male'
        is_female = str(voice.get('Gender', 'neuter')).lower() == 'female'
        assert is_male or is_female, "ERROR: The voice '%s' is not male or female." % (voice.get('voiceid'))
        _text_to_read = __text_to_read
        _text_to_read = _text_to_read.replace('{{gonads}}', 'pussy' if (is_female) else 'asshole')
        if (is_neural):
            response = polly.synthesize_speech(Text=_text_to_read, OutputFormat="mp3", VoiceId=voice.get('voiceid'),
                                                Engine='neural' if str(voice.get('Standard', 'no')).lower() == 'yes' else 'neural')
        elif (is_standard):
            response = polly.synthesize_speech(Text=_text_to_read, OutputFormat="mp3", VoiceId=voice.get('voiceid'))
        else:
            assert is_standard or is_neural, "ERROR: The voice '%s' is not standard or neural." % (voice.get('voiceid'))
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                output = os.path.join(this_dir, "{}{}{}_speech.mp3".format(speech_dir, os.sep, voice.get('voiceid')))

                print('BEGIN: Writing speech to "%s".' % (output))
                file_size = -1
                try:
                    # Open a file for writing the output as a binary stream
                    with open(output, "wb") as file:
                        file.write(stream.read())
                            
                    file_size = os.path.getsize(output)
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)
                    sys.exit(-1)
                print('DONE: Writing speech to "{}" ({}).\n\n'.format(output, file_size))

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)

    # Play the audio using the platform's default player
    if sys.platform == "win32":
        os.startfile(output)
    elif (False):
        # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, output])


assert (os.path.exists(output)) , "ERROR: The file '%s' does not exist." % (output)
print('Done.')