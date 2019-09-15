import codecs
import random

def GetRandomMoleWords():

    f = codecs.open("mole-words.txt", "r")
    lines = f.readlines()
    f.close()

    return random.choice(lines)
