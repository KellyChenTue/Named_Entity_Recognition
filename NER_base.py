import nltk

from nltk.chunk import conlltags2tree, tree2conlltags
from pprint import pprint

from spacy import displacy
# python -m spacy download en_core_web_sm

import en_core_web_sm


def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

def chunking(sent):
    pattern = 'NP: {<DT>?<JJ>*<NN>}'
    cp = nltk.RegexpParser(pattern)
    cs = cp.parse(sent)
    return cp, cs

def iob_tags(chunk_sent):
    iob = tree2conlltags(chunk_sent)
    pprint(iob)
    return iob

def get_NER(nlp, text):
    doc = nlp(text)
    sentences = [x for x in doc.sents]
    entities = [x for x in doc.ents]
    labels = [x.label_ for x in doc.ents]
    """for ent in doc.ents:
        labels = ent.label_
     """


    return sentences, entities, labels
def visulize_NER(text):
    # visualize in server
    displacy.serve(nlp(str(text)), style='ent')

if __name__ == '__main__':
    # Basic information from nltk
    ex = 'European authorities fined Google a record $5.1 billion on Wednesday for abusing its power in the mobile phone market and ordered the company to alter its practices'
    ex2 = 'WASHINGTON — Defense Secretary Mark T. Esper demanded the resignation of the Navy’s top civilian leader on Sunday, an abrupt move aimed at ending an extraordinary dispute between President Trump and his own senior military leadership over the fate of a SEAL commando in a war crimes case. In a statement, Mr. Esper said he had lost trust in the Navy secretary, Richard V. Spencer, because his private statements about the case differed from what he advocated in public. Mr. Esper added that he was “deeply troubled by this conduct.” A senior Defense Department official and a senior White House official said on Sunday night that Mr. Spencer was trying to cut a side deal with the White House to let the commando remain in the elite unit, even as he pushed both publicly and with Pentagon officials for a disciplinary hearing.'
    ex3 = "Hi, I'm Kelly. My boyfriend is Max. This is 2019. I'm in Tuebingen."
    ex4 = "Hi, I'm Chen. I'd like to fly from Stuttgart to Taipei, from 15.12 to 31.12, how much is the flight ticket?"
    ex5 = "from 2019-12-20 to 2019-12-30."
    sent = preprocess(ex4)
    chunk_parse, chunk_sent = chunking(sent)
    iob_tagged = iob_tags(chunk_sent)
    #print(iob_tagged)
    # Pre-trained Model - Spacy
    # load pre-trained model
    nlp = en_core_web_sm.load()
    sentence, entity, labels = get_NER(nlp,ex5)
    print("ENTITIY: "+ str(entity))
    print("LABEL: " + str(labels))

    #visulize_NER(sentence)