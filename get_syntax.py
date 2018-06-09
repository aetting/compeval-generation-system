import nltk
from nltk.grammar import *
from nltk.tree import Tree
from nltk import CFG
from nltk.sem.logic import Variable
from copy import *
from random import *

#this is where we will add new verb frames, or larger embedding structures?
def get_starts(main_frame,main_voice,main_verb_lemma,main_aspect,main_pol):

    if main_frame == 'transitive':
        if main_voice == 'active':
            start = """
            S[FRAME = 'transitive',VOICE = 'active'] -> NP[ROLE='agent',NUM=?nagent] VP[VOICE = 'active',ASPECT = '%s', NUM=?nagent,HEAD='%s',POL='%s'] NP[ROLE='patient']
            """%(main_aspect,main_verb_lemma,main_pol)
        elif main_voice == 'passive':
            start = """
            S[FRAME = 'transitive',VOICE = 'passive'] -> NP[ROLE='patient',NUM=?npatient] VP[VOICE = 'passive', ASPECT = '%s', NUM=?npatient,HEAD='%s',POL='%s'] NP[ROLE='agent']
            """%(main_aspect,main_verb_lemma,main_pol)
    elif main_frame == 'intransitive':
        start = """
        S[FRAME = 'intransitive',VOICE = 'active'] -> NP[ROLE='agent',NUM=?nagent] VP[VOICE = 'active',ASPECT = '%s', NUM=?nagent,HEAD='%s',POL='%s']
        """%(main_aspect,main_verb_lemma,main_pol)
    elif main_frame == 'which':
        start = """
        S[FRAME = 'which',VOICE = 'active'] -> NP[ROLE='agent',NUM=?nagent] VP[VOICE = 'active',ASPECT = '%s', NUM=?nagent,HEAD='%s',POL='%s'] WP
        """%(main_aspect,main_verb_lemma,main_pol)


    return start

def get_wp_rules(reltype,wpevent,inflections):
    wpverb = wpevent.name
    wpframe = wpevent.frame
    wpaspect = wpevent.aspect
    wppol = wpevent.pol
    wppolx = wpevent.polx
    wptense = wpevent.tense
    wpvoice = wpevent.voice
    wpag = wpevent.participants['agent']
    wppat = wpevent.participants['patient']
    wps = ''
    if wpframe == 'intransitive':
        wps += "WP -> W NP[ROLE='wpagent'] VP[VOICE='active',ASPECT = '%s',NUM=?nwpagent,HEAD='%s',POL='%s']\n"\
        %(wpaspect,wpverb,wppol)
    else:
        wps += get_np_rules_norc('wppatient',wppat,inflections)
        if wpvoice == 'active' and reltype == 'src':
            wps += "WP -> W N[ROLE='wpagent'] VP[VOICE='active',ASPECT = '%s',NUM=?nwpagent,HEAD='%s',POL='%s'] NP[ROLE='wppatient']\n"\
            %(wpaspect,wpverb,wppol)
        elif wpvoice == 'active' and reltype == 'orc':
            wps += "WP -> W N[ROLE='wppatient'] NP[ROLE='wpagent'] VP[VOICE='active',ASPECT = '%s',NUM=?nwpagent,HEAD='%s',POL='%s']\n"\
            %(wpaspect,wpverb,wppol)
        elif wpvoice == 'passive' and reltype == 'src':
            wps += "WP -> W N[ROLE='wppatient'] VP[VOICE='passive',ASPECT = '%s',NUM=?nwppatient,HEAD='%s',POL='%s'] NP[ROLE='wpagent']\n"\
            %(wpaspect,wpverb,wppol)
        elif wpvoice == 'passive' and reltype == 'orc':
            wps += "WP -> W N[ROLE='wpagent'] NP[ROLE='wppatient'] VP[VOICE='passive',ASPECT = '%s',NUM=?nwppatient,HEAD='%s',POL='%s'] \n"\
            %(wpaspect,wpverb,wppol)
    wps += get_np_rules_norc('wpagent',wpag,inflections)

    wps += get_vp_rules(wpverb,wptense,wppol,wppolx,wp=True)
    wps += get_verb_rules(wpverb,inflections)

    return wps

def get_vp_rules(verb_lemma,tense,pol,polx,rel_index=None, wp=False):
    if rel_index:
        numstring = "?nrc%s"%rel_index
        numlist = [numstring]*5
    elif wp:
        numlist = ['?nwpagent','?nwpagent','?nwppatient','?nwpagent','?nwppatient']
    else:
        numlist = ['?nagent','?nagent','?npatient','?nagent','?npatient']
    if polx:
        polxstr = "NX[HEAD='%s']"%verb_lemma
    else:
        polxstr = ''
    vps = """
    VP[VOICE = 'active',ASPECT = 'neut',NUM=%s,HEAD='%s',POL='pos'] -> V[NUM=%s,TENSE='%s',INF='tensed',HEAD='%s']
    VP[VOICE = 'active',ASPECT = 'neut',NUM=%s,HEAD='%s',POL='neg'] -> DS[NUM=%s,TENSE='%s',POL='neg'] %s V[INF='bare',HEAD='%s']
    VP[VOICE = 'passive',ASPECT = 'neut',NUM=%s,HEAD='%s',POL='%s'] -> COP[NUM=%s,TENSE='%s',POL='%s'] %s V[INF='pastpart',HEAD='%s'] B
    VP[VOICE = 'active',ASPECT = 'prog',NUM=%s,HEAD='%s',POL='%s'] -> COP[NUM=%s,TENSE='%s',POL='%s'] %s V[INF='prespart',HEAD='%s']
    VP[VOICE = 'passive',ASPECT = 'prog',NUM=%s,HEAD='%s',POL='%s'] -> COP[NUM=%s,TENSE='%s',POL='%s'] %s COP[TENSE='bare',INF='prespart'] V[INF='pastpart',HEAD='%s'] B
    """%(numlist[0],verb_lemma,numlist[0],tense,verb_lemma,
    numlist[1],verb_lemma,numlist[1],tense,polxstr,verb_lemma,
    numlist[2],verb_lemma,pol,numlist[2],tense,pol,polxstr,verb_lemma,
    numlist[3],verb_lemma,pol,numlist[3],tense,pol,polxstr,verb_lemma,
    numlist[4],verb_lemma,pol,numlist[4],tense,pol,polxstr,verb_lemma)

    vps += """
    NX[HEAD='%s'] -> '%s'
    """%(verb_lemma,polx)


    return vps

def get_verb_rules(verb_lemma,inflections):

    inflec_dict = inflections[verb_lemma]
    vs = """
    V[INF='bare',HEAD='%s'] -> '%s'
    V[TENSE='past',INF='tensed',HEAD='%s'] -> '%s'
    V[NUM='sg',TENSE='pres',INF='tensed',HEAD='%s'] -> '%s'
    V[NUM='pl',TENSE='pres',INF='tensed',HEAD='%s'] -> '%s'
    V[INF = 'prespart',HEAD='%s'] -> '%s'
    """%(verb_lemma,verb_lemma,
    verb_lemma,inflec_dict['tensed']['past'],
    verb_lemma,inflec_dict['tensed']['pressg'],
    verb_lemma,inflec_dict['tensed']['prespl'],
    verb_lemma,inflec_dict['prespart'])
    if 'pastpart' in inflec_dict:
        vs += "V[INF = 'pastpart',HEAD='%s'] -> '%s'\n"%(verb_lemma,inflec_dict['pastpart'])
    return vs

def get_np_rules_norc(role,participant,inflections):

    if not participant.surface: participant.get_surface(inflections)
    participant_name = participant.surface
    participant_num = participant.num

    ns = """
    N[ROLE='%s'] -> '%s'
    """%(role,participant_name)

    if 'adj' in participant.attributes:
        adjP = "AP[ROLE='%s']"%role
        ns += """
        AP[ROLE='%s'] -> '%s'
        """%(role,participant.attributes['adj'])
    else: adjP = ' '

    ns += """
    NP[ROLE='%s'] -> D %s N[ROLE='%s']
    """%(role,adjP,role)

    return ns

def get_np_rules(role,participant,rc_index,bindings,inflections):

    if not participant.surface: participant.get_surface(inflections)
    participant_name = participant.surface
    participant_num = participant.num
    participant_det = participant.det

    ns = """
    N[ROLE='%s'] -> '%s'
    D[ROLE='%s'] -> '%s'
    """%(role,participant_name,role,participant_det)

    if 'adj' in participant.attributes:
        adjP = "AP[ROLE='%s']"%role
        ns += """
        AP[ROLE='%s'] -> '%s'
        """%(role,participant.attributes['adj'])
    else: adjP = ' '

    if 'rc' in participant.attributes:
        rcP = "RC[ROLE='%s']"%role
        rc = participant.attributes['rc']
        rcstring,rc_index,bindings = get_rc_rules(rc,role,participant_num,rc_index,bindings,inflections)
        ns += rcstring
    else: rcP = ' '

    ns += """
    NP[ROLE='%s'] -> D[ROLE='%s'] %s N[ROLE='%s'] %s
    """%(role,role,adjP,role,rcP)

    return ns,rc_index,bindings


def get_rc_rules(rc,mainrole,mainnum,rc_index,bindings,inflections):
    s = ''
    rtype = rc['rtype']
    relrole = rc['role']
    relevent = rc['event'].name
    reltense = rc['event'].tense
    relpol = rc['event'].pol
    relpolx = rc['event'].polx
    relaspect = rc['event'].aspect
    if relrole == 'patient':
        if 'agent' in rc['event'].participants:
            ag = rc['event'].participants['agent']
            nps,rc_index,bindings = get_np_rules('%srelagent'%mainrole,ag,rc_index,bindings,inflections)
            s+= nps
        if rtype == 'src':
            s += "RC[ROLE='%s']-> T VP[VOICE='passive',ASPECT = '%s',NUM=?nrc%s,HEAD='%s',POL='%s'] NP[ROLE='%srelagent']\n"\
            %(mainrole,relaspect,rc_index,relevent,relpol,mainrole)
            rcnum = mainnum
        elif rtype == 'orc':
            s += "RC[ROLE='%s']-> T NP[ROLE='%srelagent'] VP[VOICE='active',ASPECT = '%s',NUM=?nrc%s,HEAD='%s',POL='%s']\n"\
            %(mainrole,mainrole,relaspect,rc_index,relevent,relpol)
            rcnum = ag.num
    elif relrole == 'agent':
        if 'patient' in rc['event'].participants:
            pa = rc['event'].participants['patient']
            nps,rc_index,bindings = get_np_rules('%srelpatient'%mainrole,pa,rc_index,bindings,inflections)
            s+= nps
            if rtype == 'src':
                s += "RC[ROLE='%s']-> T VP[VOICE='active',ASPECT = '%s',NUM=?nrc%s,HEAD='%s',POL='%s'] NP[ROLE='%srelpatient']\n"\
                %(mainrole,relaspect,rc_index,relevent,relpol,mainrole)
                rcnum = mainnum
            elif rtype == 'orc':
                s += "RC[ROLE='%s']->T NP[ROLE='%srelpatient'] VP[VOICE='passive',ASPECT='%s',NUM=?nrc%s,HEAD='%s',POL='%s'] \n"\
                %(mainrole,mainrole,relaspect,rc_index,relevent,relpol)
                rcnum = pa.num
        elif rc['event'].frame == 'intransitive':
            s += "RC[ROLE='%s']-> T VP[VOICE='active',ASPECT = '%s',NUM=?nrc%s,HEAD='%s',POL='%s']\n"\
            %(mainrole,relaspect,rc_index,relevent,relpol)
            rcnum = mainnum

    vps = get_vp_rules(relevent,reltense,relpol,relpolx,rel_index=rc_index)
    s += vps

    vrs = get_verb_rules(relevent,inflections)
    s += vrs

    bindings[Variable('?nrc%s'%rc_index)] = rcnum
    rc_index += 1

    return s,rc_index,bindings

def unfold_tree_feature(grammar,node,bindings):
    #choose a production rule from the options
#     print('\n')
#     print('NODE',node)
#     print('BINDINGS',bindings)
    # print(node)
    prod_options = copy(grammar.productions(lhs=node))
#     print('OPTIONS',prod_options)
    for option in grammar.productions(lhs=node):
#         print('CHEKING OPTION',option)
        for feat in node:
#             print('FEAT',feat)
            if feat in option.lhs() and option.lhs().substitute_bindings(bindings)[feat] != node[feat]:
#                 print('REMOVE')
                prod_options.remove(option)
                break
#     print(prod_options)
    selected_rule = choice(prod_options)
#     print('SELECTED',selected_rule)
    bound_ls = selected_rule.lhs().substitute_bindings(bindings)
    bound_rs = []
    for e in selected_rule.rhs():
        if isinstance(e,nltk.grammar.FeatStructNonterminal):
#             print('YES')
            bound_rs.append(e.substitute_bindings(bindings))
        else: bound_rs = selected_rule.rhs()
    bound_rule = Production(bound_ls,bound_rs)
#     print('BOUND_RULE',bound_rule)
    child_trees = []
    for child in bound_rule.rhs():
        if isinstance(child,Nonterminal):
            child_trees.append(Tree(child,unfold_tree_feature(grammar,child,bindings)))
        else:
            child_trees.append(child)
    t = Tree(node,child_trees)
    return t

def import_grammar(filename):
    with open(filename) as file:
        gram = file.read()
    return gram
