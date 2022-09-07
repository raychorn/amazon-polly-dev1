import os
from genericpath import exists
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing

def request_polly_speak(profile_name=None, region_name=None, voice=None, text_to_read=None, textType=None, output_filename=None):
    session = Session(profile_name=profile_name)
    polly = session.client("polly", region_name=region_name)
    
    textType = 'text' if (not textType in ['ssml', 'text']) else textType

    try:
        # Request speech synthesis
        if (voice):
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
                print('DONE: Writing speech to "{}" ({}).\n\n'.format(output_filename, file_size))
                return output_filename, file_size
            
    return None, -1
