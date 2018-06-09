import numpy as np
from numpy.random import choice
from copy import *
import nltk, itertools, random
from nltk.sem.logic import Variable
import helper_dicts

def populate_check(avoidEvent,needList,event,max_per_op,num_this_op,lexvar_package,nx=None,dv=False):
    yielded = 0
    nouns,verbs,inflections,nxlist = lexvar_package
    for ev2 in populate_event(event,lexvar_package,nx=nx,dv=dv):
        # if outer_loop_iter > 2 and yielded == 0: break
        safe = 1
        if avoidEvent:
            if not ev2.check_event_to_avoid(avoidEvent):
                safe = 0
#                     print('DID NOT PASS')
        if safe:
            num_this_op += 1
            yielded += 1
            yield(ev2,num_this_op)
        if max_per_op and (num_this_op >= max_per_op):
            break

def populate_check_wadd(avoidEvent,needList,event,max_per_op,num_this_op,lexvar_package,nx=None,dv=False):
    fullstop=False
    _,verbs,_,_ = lexvar_package
    for ev in add_mandatory_words(needList,event,verbs):
        yielded = 0
        for ev2 in populate_event(ev,lexvar_package,nx=nx,dv=dv):
            # if outer_loop_iter > 2 and yielded == 0:
                # break
            safe = 1
            if avoidEvent:
                if not ev2.check_event_to_avoid(avoidEvent): safe = 0
            if safe:
                num_this_op += 1
                yielded += 1
                yield(ev2,num_this_op)
            if max_per_op and (num_this_op >= max_per_op):
                fullstop = True
                break
        if fullstop: break

#takes partially filled input event structure and iterates through available nouns and verbs to fill remaining slots
def populate_event(event_orig,lexvar_package,nx=None,dv=False):
    #currently set so only one event is output for each original input frame (max_evs)
    nouns,verbs,inflections,nxlist = lexvar_package
    max_evs = None
    used_participants,used_events,parts_to_fill,events_to_fill = take_inventory(event_orig,verbs)
    available_nouns = copy(nouns)
    available_nouns = [e for e in available_nouns if e not in used_participants]
    pre_available_verbs = copy(verbs)
    available_verbs = {}
    for f in verbs:
        if f not in events_to_fill: events_to_fill[f] = {}
        if f not in used_events: used_events[f] = {}
    for k in events_to_fill:
#         print('TOFILL',k)
        available_verbs[k] = [e for e in verbs[k] if e not in used_events[k]]
    #get each permutation
    n = len(parts_to_fill)
    iv = len(events_to_fill['intransitive'])
    tv = len(events_to_fill['transitive'])
    i = 0

    if event_orig.voice: avail_voices = [event_orig.voice]
    else: avail_voices = helper_dicts.voices[event_orig.frame]
    if event_orig.aspect: avail_aspects = [event_orig.aspect]
    else: avail_aspects = ['neut','prog']
    if event_orig.tense: avail_tenses = [event_orig.tense]
    else: avail_tenses = ['past','pres']
    if event_orig.pol: avail_pols = [event_orig.pol]
    else: avail_pols = ['pos','neg']

    permns = list(itertools.permutations(range(len(available_nouns)),r = n))
    permts = list(itertools.permutations(range(len(available_verbs['transitive'])),r = tv))
    permis = list(itertools.permutations(range(len(available_verbs['intransitive'])),r = iv))

    # allperms = list(itertools.product(permns,permts,permis,avail_voices,avail_aspects,avail_tenses,avail_pols))
    # for l in permns,permts,permis:
    #     l = None
    # random.shuffle(allperms)

    # for permn,permt,permi,voice,aspect,tense,pol in allperms:
    for permn,permt,permi,voice,aspect,tense,pol in get_rand_prod([permns,permts,permis,avail_voices,avail_aspects,avail_tenses,avail_pols]):
        Ns = [available_nouns[e] for e in permn]
        Ts = [available_verbs['transitive'][e] for e in permt]
        Is = [available_verbs['intransitive'][e] for e in permi]
        eventcopy = deepcopy(event_orig)

        event = fill_slots(eventcopy,parts_to_fill,Ns)
        event = fill_slots(event,events_to_fill['transitive'],Ts)
        event = fill_slots(event,events_to_fill['intransitive'],Is)

        event_inter = deepcopy(event)
        event_inter.aspect = aspect
        event_inter.pol = pol
        event_inter.tense = tense
        event_inter.voice = voice
        event_full = fill_details(event_inter,nxlist,nx=nx,dv=dv)
#                                 print (' '.join(Ns+Ts+Is+[aspect,pol,tense,voice]))
        yield(event_full)

def decode(num,listlengths):

    inds = []
    for i,l in enumerate(listlengths):
        if i == 0:
            ind = num//np.prod(listlengths[1:])
            # permn_ind = num/(lt*li*lv*ltn*la*lp)
        elif i == len(listlengths) - 1:
            ind = num%listlengths[-1]
        else:
            ind = (num%(np.prod(listlengths[i:])))//(np.prod(listlengths[i+1:]))
        inds.append(ind)
    return inds

def get_rand_prod(lists):
    used = []
    listlengths = [len(l) for l in lists]
    numcombs = np.prod(listlengths)
    new = 0
    for i in range(numcombs):
        while new == 0:
            num = np.random.randint(numcombs)
            if num not in used:
                new = 1
        inds = decode(num,listlengths)
        listitems = [lists[i2][ind2] for i2,ind2 in enumerate(inds)]
        # s2 = ' '.join(listitems) + ' --> %s'%num
        used.append(num)
        new = 0
        yield listitems


#loop through identified open slots and designated fillers, and insert
def fill_slots(event,slots,fillers):
    for i in range(len(slots)):
        slot = slots[i]
        slotsplit = slot.split('_')
        if slotsplit[0] == 'rel':
            hostrole = slotsplit[1]
            designation = slotsplit[2]
            subevent = event.participants[hostrole].attributes['rc']['event']
        else:
            designation = slotsplit[0]
            subevent = event
        if designation == 'main':
            subevent.name = fillers[i]


        else:
            subevent.participants[designation].name = fillers[i]
            if slotsplit[0] != 'rel' and 'rc' in subevent.participants[designation].attributes:
                #TODO change so this checks whether this has already been defined
                r = subevent.participants[designation].attributes['rc']['role']
                subevent.participants[designation].attributes['rc']['event'].participants[r].name = fillers[i]
    return(event)

#populate unspecified properties
def fill_details(event_input,nxlist,voice=None,nx=None,dv=False):
    event = deepcopy(event_input)
    if not event.tense: event.tense = choice(['past','pres'])
    if not event.aspect: event.aspect = choice(['prog','neut'],p=[.3,.7])
    if not event.voice:
        if voice: event.voice = voice
        else: event.voice = choice(helper_dicts.voices[event.frame])
    if not event.pol: event.pol = choice(['pos','neg'],p=[.8,.2])
    # if event.pol == 'neg' and nx and not event.polx:
    if nx and not event.polx:
        num_extras = max(0,min(nx,int(round(1*np.random.randn()+1))))
        if num_extras > 0:
            advlist = copy(nxlist)
            random.shuffle(advlist)
            px = ' , '.join(advlist[:num_extras])
            #take the first num_extras of them and add them in order as the content for polx
            event.polx = px

    #TODO remove this line if we take care of populating frame elsewhere
    if not event.frame: event.frame = frames[event.name]
    for part in event.participants:
        if not event.participants[part].num: event.participants[part].num = choice(['sg','pl'])
        if not event.participants[part].det:
            if dv:
                predet = choice(['def','indef'])
                event.participants[part].det = helper_dicts.defnum2det[predet][event.participants[part].num]
            else:
                event.participants[part].det = 'the'
        event.bindings[Variable('?n%s'%part)] = event.participants[part].num
        if 'rc' in event.participants[part].attributes:
            fr =  event.participants[part].attributes['rc']['event'].frame
            if not event.participants[part].attributes['rc']['rtype'] and not event.participants[part].attributes['rc']['event'].voice:
                #for now, try to avoid ORC with hostrole as agent, since eg "the professor that the company was called by" is a bit extreme
                if event.participants[part].attributes['rc']['role'] == 'agent':
                    event.participants[part].attributes['rc']['rtype'] = choice(['orc','src'],p = [.05,.95])
                else:
                    event.participants[part].attributes['rc']['rtype'] = choice(['orc','src'])
                #voice in RC is deterministic from hostrole and rtype, so set that here
                chosen_role = event.participants[part].attributes['rc']['role']
                chosen_rtype = event.participants[part].attributes['rc']['rtype']
                event.participants[part].attributes['rc']['event'].voice = helper_dicts.rolertype2voice[chosen_role][chosen_rtype]
            elif not event.participants[part].attributes['rc']['rtype'] and event.participants[part].attributes['rc']['event'].voice:
                chosen_role = event.participants[part].attributes['rc']['role']
                chosen_voice = event.participants[part].attributes['rc']['event'].voice
                event.participants[part].attributes['rc']['rtype'] = helper_dicts.rolevoice2rtype[chosen_role][chosen_voice]

            rcevent = fill_details(event.participants[part].attributes['rc']['event'],nxlist,nx=nx,dv=dv)
            event.participants[part].attributes['rc']['event'] = rcevent

    return event


#need to have defined ['rc']['role'] before running this, so you know which role in the RC not to count
def take_inventory(event,verbs,rcrole = None):
#     defined_roles = {}
#     [k for (k,val) in event.participants.items() if val]
#     defined_events = []
    used_participants = []
    parts_to_fill = []
#     [val.name for (k,val) in event.participants.items() if val]
    used_events = {}
    events_to_fill = {}
    for f in verbs:
        used_events[f] = []
        events_to_fill[f] = []
    if event.name:
#         defined_events.append('main')
        used_events[event.frame].append(event.name)
    #*****TODO: right now we don't have a way to deal with events where no frame has been specified. definitely need to figure that out.
    else:
        if event.frame not in events_to_fill:events_to_fill[event.frame] = []
        events_to_fill[event.frame].append('main')

#     used_adjs = []
#     defined_roles['main'] = []
    for role in event.participants:
        #ignore role if we are in a relative clause and the role is the one of the participant being modified by the relative clause
        if rcrole and rcrole == role: continue
        part = event.participants[role]
        if part.name:
#             defined_roles['main'].append(role)
            used_participants.append(part.name)
        else:
            parts_to_fill.append(role)
        if 'rc' in part.attributes:

            rc_used_participants,rc_used_events,rc_parts_to_fill,rc_events_to_fill = take_inventory(part.attributes['rc']['event'],verbs,rcrole=part.attributes['rc']['role'])
            used_participants += rc_used_participants
            for k in rc_used_events:
                if k not in used_events: used_events[k] = []
                used_events[k] += rc_used_events[k]
            for k in rc_events_to_fill:
                if k not in events_to_fill: events_to_fill[k] = []
                events_to_fill[k] += ['rel_%s_%s'%(role,e) for e in rc_events_to_fill[k]]
            parts_to_fill += ['rel_%s_%s'%(role,e) for e in rc_parts_to_fill]
#         if 'adj' in part.attributes:
#             used_adjs.append(part.attributes['adj'])
    return used_participants,used_events,parts_to_fill,events_to_fill

def sync_rc_hostrole(event):
#     print('SYNCING')
    #for all participants in event, if has rc and 'role' not defined, choose a role
    #then make sure name of host role and name of linked role in RC are filled and matching
    for part in event.participants:
        if 'rc' in event.participants[part].attributes:
#             print('Participant whose RC this is',part)
#             if not event.participants[part].attributes['rc']['role']:
#                 print('NEW ONE: frame = %s'%event.participants[part].attributes['rc']['event'].frame)
#                 print('ROLES:')
#                 print(roles[event.participants[part].attributes['rc']['event'].frame])
#                 chosen_role = choice(roles[event.participants[part].attributes['rc']['event'].frame])
#                 event.participants[part].attributes['rc']['role'] = chosen_role
#             else: chosen_role = event.participants[part].attributes['rc']['role']
            chosen_role = event.participants[part].attributes['rc']['role']
#             print(chosen_role)
            rcevent = event.participants[part].attributes['rc']['event']
            if event.participants[part].name and not rcevent.participants[chosen_role].name:
                rcevent.participants[chosen_role].name = event.participants[part].name
            elif rcevent.participants[chosen_role].name and not event.participants[part].name:
                event.participants[part].name = rcevent.participants[chosen_role].name
    return event


def add_mandatory_words(mand_words,event_orig,verbs):
    used_participants,used_events,parts_to_fill,events_to_fill = take_inventory(event_orig,verbs)
#     print('INVENTORY')
#     print used_participants
#     print parts_to_fill
#     print used_events
#     print events_to_fill
#     print('\n')
    use = 1
    if 'noun' in mand_words:
        n = len(mand_words['noun'])
        mwn = mand_words['noun']
    else:
        n = 0
        mwn = []
    if 'transitive' in mand_words:
        tv = len(mand_words['transitive'])
        mwt = mand_words['transitive']
    else:
        tv = 0
        mwt = []
    if 'intransitive' in mand_words:
        iv = len(mand_words['intransitive'])
        mwi = mand_words['intransitive']
    else:
        iv = 0
        mwi = []
    if len(parts_to_fill) < len(mwn):
#         print('NOUNS DID IT')
        use = 0
    if len(events_to_fill['transitive']) < len(mwt):
#         print('TRANS DID IT')
        use = 0
    if len(events_to_fill['intransitive']) < len(mwi):
#         print('INTRANS DID IT')
        use = 0
    fillers = [mwn,mwt,mwi]
#     Nperms = [n for n in itertools.product(mand_words['noun'],parts_to_fill)]
#     Tperms = [t for t in itertools.product(mand_words['transitive'],events_to_fill['transitive'])]
#     Iperms = [i for i in itertools.product(mand_words['intransitive'],events_to_fill['intransitive'])]

    permn = [e for e in itertools.permutations(parts_to_fill,r = n)]
    permt = [e for e in itertools.permutations(events_to_fill['transitive'],r = tv)]
    permi = [e for e in itertools.permutations(events_to_fill['intransitive'],r = iv)]
#     print permn
#     print permt
#     print permi
#     print('\n')
    for l in [permn,permt,permi]:
        if len(l) < 1: l.append(None)
    combos = [e for e in itertools.product(permn,permt,permi)]
#     print('COMBOS')
#     print combos
#     print len(combos)
    if use:
        for c in combos:
#             print('THIS COMBO')
#             print(c)
            ev = deepcopy(event_orig)
#             print ev.view()
            for ind in range(len(fillers)):
                ev = fill_slots(ev,c[ind],fillers[ind])
            yield(ev)
#                 print ev.view()
