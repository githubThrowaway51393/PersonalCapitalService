

def decode_utf8(string):
    return string.replace(u"\u2013","-").replace(u"\u00ae","")