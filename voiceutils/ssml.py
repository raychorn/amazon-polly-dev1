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

