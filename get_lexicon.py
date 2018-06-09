import sys
import os
import json
import gzip


#get lexical vars for generation system from XTAG
def get_inflections():
    inflections = {}
    nouns = []

    f = gzip.open('lexical/morph_english.flat.gz', 'rt')

    all_inflections = {}
    noun_inflections = {}
    for line in f:
        if line[0] == ';': continue
        entry = line.split('\t')
#         pts_of_spch = []
        inflct = entry[0].rstrip()
        main_lemma = entry[2].rstrip()
        pts_of_spch = entry[3:]

        prog_lemmas = []
        for i in range(len(pts_of_spch)):
            if i < len(pts_of_spch)-1:
                div = pts_of_spch[i].split('#')
                lemma = div[1]
                pt_of_spch = div[0].split(' ')
            else:
                lemma = main_lemma
                pt_of_spch = pts_of_spch[i].rstrip().split(' ')

            prog_lemmas.append(lemma)
            if pt_of_spch[0] == 'V':
                # delete -ing to get lemma (works for many)
                if lemma.endswith('ing') and lemma != 'sing':
                    for lem in prog_lemmas:
                        if not lem.endswith('ing'):
                            lemma = lem
                if lemma == 'sung':
                    lemma = 'sing'

                if lemma not in all_inflections:
                    all_inflections[lemma] = {}

                if 'tensed' not in all_inflections[lemma]:
                    all_inflections[lemma]['tensed'] = {}

                if pt_of_spch[1] == 'INF':
                    all_inflections[lemma]['tensed']['prespl'] = inflct

                if pt_of_spch[1] == '3sg':
                    all_inflections[lemma]['tensed']['pressg'] = inflct

                if pt_of_spch[1] == 'PAST':
                    all_inflections[lemma]['tensed']['past'] = inflct

                if pt_of_spch[1] == 'PPART':
                    all_inflections[lemma]['pastpart'] = inflct

                if pt_of_spch[1] == 'PROG':
                    all_inflections[lemma]['prespart'] = inflct

            if pt_of_spch[0] == 'N':
                if lemma not in noun_inflections:
                    noun_inflections[lemma] = {}

                if len(pt_of_spch) < 3:
                    if pt_of_spch[1] == '3sg':
                        noun_inflections[lemma]['sg'] = inflct
                    if pt_of_spch[1] == '3pl':
                        noun_inflections[lemma]['pl'] = inflct

#         line = f.readline()
    f.close()

    return all_inflections,noun_inflections

#load vocab from file
def get_lemmas(vocab):
    # read input file
    nouns = []
    trans = []
    intrans = []
    adverbs = None

    with open(vocab, 'rU') as f:
        vocabdict = json.load(f)
        for word in vocabdict['intransitive']:
            intrans.append(word.strip())
        for word in vocabdict['transitive']:
            trans.append(word.strip())
        for word in vocabdict['noun']:
            nouns.append(word.strip())
        if 'adverbs' in vocabdict:
            adverbs = [word.strip() for word in vocabdict['adverbs']]

    return nouns,trans,intrans,adverbs

def compile_vocab(vocab,out):
    all_inflections,noun_inflections = get_inflections()
    nouns,trans,intrans,adverbs = get_lemmas(vocab)

    lexvars = {}
    remove = {'intrans':[],'trans':[],'noun':[]}
    verbs = {'transitive':[],'intransitive':[]}
    frames = {}

    v_inflct = {} # keep nouns and verb separate at first, to see if all inflections are present
    n_inflct = {}

    past_parts = {}

    for lemma in all_inflections:
        if len(all_inflections[lemma]['tensed']) == 0:
            past_parts[lemma] = lemma

    for past_part in past_parts:
        all_inflections.pop(past_part)

    for lemma in all_inflections:
        if 'pastpart' not in  all_inflections[lemma]:
            if 'past' in all_inflections[lemma]['tensed'] and all_inflections[lemma]['tensed']['past'] in past_parts:
                all_inflections[lemma]['pastpart'] = past_parts[all_inflections[lemma]['tensed']['past']]


    # check if words have all inflections
    for v in trans:
        if v in all_inflections:
            v_inflct[v] = all_inflections[v]
        else:
            remove['trans'].append(v)

    for v in intrans:
        if v in all_inflections:
            v_inflct[v] = all_inflections[v]
        else:
            remove['intrans'].append(v)

    for n in nouns:
        if n in noun_inflections:
            n_inflct[n] = noun_inflections[n]
        else:
            remove['noun'].append(n)

    for l in v_inflct:
        if ('tensed' not in v_inflct[l]) or ('pastpart' not in v_inflct[l]) or ('prespart' not in v_inflct[l]) or (('tensed' in v_inflct[l]) and (('pressg' not in v_inflct[l]['tensed']) or ('prespl' not in v_inflct[l]['tensed']) or ('past' not in v_inflct[l]['tensed']))):
            if l in trans:
                remove['trans'].append(l)
            if l in intrans:
                remove['intrans'].append(l)

    for l in n_inflct:
        if ('sg' not in n_inflct[l]) or ('pl' not in n_inflct[l]):
            remove['noun'].append(l)

    #remove from lists
    trans = [l for l in trans if l not in remove['trans']]
    intrans = [l for l in intrans if l not in remove['intrans']]
    nouns = [l for l in nouns if l not in remove['noun']]

    # remove from inflct
    for l in remove:
        if l in v_inflct:
            v_inflct.pop(l, None)
        if l in n_inflct:
            n_inflct.pop(l, None)

    # build data structures
    for v in trans:
        verbs['transitive'].append(v)

    for v in intrans:
        verbs['intransitive'].append(v)


    for i in verbs:
        for v in verbs[i]:
            frames[v] = i

    inflections = dict(v_inflct)
    inflections.update(n_inflct)

    lexvars['verbs'] = verbs
    lexvars['nouns'] = nouns
    lexvars['frames'] = frames
    lexvars['inflections'] = inflections
    lexvars['nxlist'] = adverbs

    with open(out, 'w') as output:
        json.dump(lexvars,output,indent=1)

    remove_all = remove['trans']+remove['intrans']+remove['noun']
    if len(remove_all) > 0:
        print('\n# The following lemmas were removed:\n%s\n'%'\n'.join(remove_all))


    return nouns,verbs,frames,inflections

if __name__ == "__main__":

    compile_vocab('lexical/vocabulary.json','gensys_lexvars.json')
