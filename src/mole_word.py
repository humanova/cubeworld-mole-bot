import codecs
import random

emo_refs = {"bruh"        : "<bruh:622591578627637250>",
            "hyperBruh"   : "<hyperBruh:622559890916900874>",
            "weirdBruh"   : "<weirdBruh:614530140906717192>",
            "bruhTopHat"  : "<bruhTopHat:620980170907582474>",
            }


def FixEmoRefs(text):
    text = text.replace(":bruh:",       emo_refs["bruh"])
    text = text.replace(":hyperBruh:",  emo_refs["hyperBruh"])
    text = text.replace(":weirdBruh:",  emo_refs["weirdBruh"])
    text = text.replace(":bruhTopHat:", emo_refs["bruhTopHat"])

    return text


def GetRandomMoleWords():

    f = codecs.open("mole-words.txt", "r")
    lines = f.readlines()
    f.close()

    return FixEmoRefs(random.choice(lines))
