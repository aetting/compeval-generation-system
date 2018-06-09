import itertools
import sys,re,nltk
from nltk.grammar import *
from nltk.tree import Tree
from nltk import CFG
from random import *
from copy import *
from nltk.sem.logic import Variable

class characterStart(object):
    def __init__(self,sdict={}):
        if 'name' in sdict: self.name = sdict['name']
        else: self.name = None
        if 'attributes' in sdict:
            self.attributes = {}
            for att in sdict['attributes']:
                if att == 'rc':
                    self.attributes['rc'] = {}
                    if 'event' in sdict['attributes']['rc']:
                        self.attributes['rc']['event'] = eventStart(sdict['attributes']['rc']['event'])
                    else:
                        self.attributes['rc']['event'] = {}
                    for k in ['role','rtype']:
                        if k in sdict['attributes']['rc']:
                            self.attributes['rc'][k] = sdict['attributes']['rc'][k]
                        else:
                            self.attributes['rc'][k] = None
                else:
                    self.attributes[att] = sdict['attributes'][att]
        else: self.attributes = {}
        if 'num' in sdict: self.num = sdict['num']
        else: self.num = None
        if 'surface' in sdict: self.surface = sdict['surface']
        else: self.surface = None
        if 'det' in sdict: self.det = sdict['det']
        else: self.det = None

    def todict(self,inflections):
        outdict = {}
        outdict['name'] = self.name
        outdict['num'] = self.num
        outdict['surface'] = self.surface
        outdict['attributes'] = {}
        if 'adj' in self.attributes:
            outdict['attributes']['adj'] = self.attributes['adj']
        if 'rc' in self.attributes:
            relsubnum = None
            outdict['attributes']['rc'] = {}
            outdict['attributes']['rc']['role'] = self.attributes['rc']['role']
            outdict['attributes']['rc']['role'] = self.attributes['rc']['rtype']
            if self.attributes['rc']['rtype'] == 'src': relsubnum = self.num
            outdict['attributes']['rc']['event'] = self.attributes['rc']['event'].todict(inflections,subnum=relsubnum)

        return outdict

    def get_surface(self,inflections_dict):
        self.surface = inflections_dict[self.name][self.num]

    def absorb(self,ch2):
        if ch2.name:
            if self.name: pass #print('MERGE OVERRIDE (name)')
            else:
                self.name = copy(ch2.name)
        if ch2.num:
            if self.num: pass #print('MERGE OVERRIDE (num)')
            else:
                self.num = copy(ch2.num)
        if ch2.surface:
            if self.surface: pass #print('MERGE OVERRIDE (surface)')
            else:
                self.surface = copy(ch2.surface)
        if 'adj' in ch2.attributes:
            if 'adj' in self.attributes: pass #print('MERGE OVERRIDE (adj)')
            else:
                self.attributes['adj'] = copy(ch2.attributes['adj'])
        if 'rc' in ch2.attributes:
            if 'rc' not in self.attributes:
                self.attributes['rc'] = deepcopy(ch2.attributes['rc'])
            else:
                if 'role' in ch2.attributes['rc'] and ch2.attributes['rc']['role']:
                    if self.attributes['rc']['role']: print('MERGE OVERRIDE (rc role)')
                    else:
                        self.attributes['rc']['role'] = copy(ch2.attributes['rc']['role'])
                if 'rtype' in ch2.attributes['rc'] and ch2.attributes['rc']['rtype']:
                    if self.attributes['rc']['rtype']: print('MERGE OVERRIDE (rc rtype)')
                    else:
                        self.attributes['rc']['rtype'] = copy(ch2.attributes['rc']['rtype'])
                if 'event' in ch2.attributes['rc'] and ch2.attributes['rc']['event']:
                    if 'event' not in self.attributes['rc'] or not self.attributes['rc']['event']:
                        self.attributes['rc']['event'] = deepcopy(ch2.attributes['rc']['event'])
                    else:
                        self.attributes['rc']['event'].absorb(ch2.attributes['rc']['event'])

class eventStart(object):
    #hold event name and participants
    #participants can then hold their own information
    def __init__(self,sdict={}):
        self.participants = {}
        if 'participants' in sdict:
            for part in sdict['participants']:
                self.participants[part] = characterStart(sdict['participants'][part])
        if 'name' in sdict: self.name = sdict['name']
        else: self.name = None
        if 'frame' in sdict: self.frame = sdict['frame']
        else: self.frame = None
        if 'tense' in sdict: self.tense = sdict['tense']
        else: self.tense = None
        if 'aspect' in sdict: self.aspect = sdict['aspect']
        else: self.aspect = None
        if 'pol' in sdict: self.pol = sdict['pol']
        else: self.pol = None
        if 'voice' in sdict: self.voice = sdict['voice']
        else: self.voice = None
        if 'wp' in sdict: self.wp = sdict['wp']
        else: self.wp = None
        if 'polx' in sdict: self.polx = sdict['polx']
        else: self.polx = None

        self.bindings = {}
        self.components = [self.name,self.frame,self.tense,self.aspect,self.pol,self.voice]

    def todict(self,inflections,subnum=None):
        outdict = {}
        self.get_surface(inflections,subnum=subnum)
        outdict['surface'] = self.surface
        outdict['name'] = self.name
        outdict['frame'] = self.frame
        outdict['tense'] = self.tense
        outdict['aspect'] = self.aspect
        outdict['pol'] = self.pol
        outdict['voice'] = self.voice
        outdict['participants'] = {}
        for part in self.participants:
            outdict['participants'][part] = self.participants[part].todict(inflections)

        return outdict

    def get_surface(self,inflections,subnum=None):
        lem = self.name
        inflect_dict = inflections[lem]
        if self.voice == 'passive':
            self.surface = inflect_dict['pastpart']
        elif self.voice == 'active':
            if self.aspect == 'prog':
                self.surface = inflect_dict['prespart']
            elif self.aspect == 'neut':
                if self.pol == 'neg':
                    self.surface =  lem
                elif self.pol == 'pos':
                    if self.tense == 'past':
                        self.surface = inflect_dict['tensed']['past']
                    elif self.tense == 'pres':
                        if not subnum:
                            subnum = self.participants['agent'].num
                        if subnum == 'sg':
                            self.surface = inflect_dict['tensed']['pressg']
                        elif subnum == 'pl':
                            self.surface = inflect_dict['tensed']['prespl']


    def absorb(self,ev2):
        if ev2.name:
            if self.name: pass #print('MERGE OVERRIDE (name)')
            else:
                self.name = copy(ev2.name)
        if ev2.frame:
            if self.frame: pass #print('MERGE OVERRIDE (frame)')
            else:
                self.frame = copy(ev2.frame)
        if ev2.tense:
            if self.tense: pass #print('MERGE OVERRIDE (tense)')
            else:
                self.tense = copy(ev2.tense)
        if ev2.aspect:
            if self.aspect: pass #print('MERGE OVERRIDE (aspect)')
            else:
                self.aspect = copy(ev2.aspect)
        if ev2.voice:
            if self.voice: pass #print('MERGE OVERRIDE (voice)')
            else:
                self.voice = copy(ev2.voice)
        if ev2.pol:
            if self.pol: pass #print('MERGE OVERRIDE (pol)')
            else:
                self.pol = copy(ev2.pol)
        for part in ev2.participants:
            if part in self.participants:
                self.participants[part].absorb(ev2.participants[part])
            else:
                self.participants[part] = deepcopy(ev2.participants[part])

        #TODO add capacity to merge participant w/o RC with RC that has unspecified participant???


    def view(self):
        s = "\nNAME %s \nTENSE %s, ASPECT %s, POL %s, FRAME %s, VOICE %s \n"%(self.name,self.tense,self.aspect,self.pol,self.frame,self.voice)
        s += 'PARTICIPANTS\n'
        for k in self.participants:
            if not self.participants[k]:
                s += '-----------\n %s: \n'%k
            else:
                s += '-----------\n %s: %s (%s, %s)\n'%(k,self.participants[k].name,self.participants[k].num,self.participants[k].surface)
                if 'adj' in self.participants[k].attributes:
                    s += ' ADJ: %s \n'%self.participants[k].attributes['adj']
                if 'rc' in self.participants[k].attributes:
                    evstring = self.participants[k].attributes['rc']['event'].view()
                    evstring = re.sub('\n','\n   ',evstring)
                    s += """ RC \n   ROLE: %s RTYPE: %s \n   EVENT %s
                    """%(self.participants[k].attributes['rc']['role'],self.participants[k].attributes['rc']['rtype'],evstring)
        return (s)

    def check_event_to_avoid(self,other_event):
        checklist = []
        safelist = []
        safe_rel_parallel = 0
        safe_main = 0

#         print self.view()
#         print other_event.view()

        if other_event.name: checklist.append((other_event.name,self.name))
        if other_event.frame: checklist.append((other_event.frame,self.frame))
        if other_event.tense: checklist.append((other_event.tense,self.tense))
        if other_event.aspect: checklist.append((other_event.aspect,self.aspect))
        if other_event.pol: checklist.append((other_event.pol,self.pol))
        if other_event.voice: checklist.append((other_event.voice,self.voice))
        has_rc = 0
        for p in other_event.participants:
            if p not in self.participants:
                checklist.append((0,1))
                continue
            if other_event.participants[p]:
                if other_event.participants[p].name:
                    checklist.append((other_event.participants[p].name,self.participants[p].name))
                if 'adj' in other_event.participants[p].attributes:
                    checklist.append((other_event.participants[p].attributes['adj'],self.participants[p].attributes['adj']))
                if 'rc' in other_event.participants[p].attributes:
                    has_rc = 1
                    if 'rc' in self.participants[p].attributes:
                        other_rc = other_event.participants[p].attributes['rc']
                        self_rc = self.participants[p].attributes['rc']
                        if other_rc['rtype']:
                            checklist.append((other_rc['rtype'],self_rc['rtype']))
                        if other_rc['role']:
                            checklist.append((other_rc['role'],self_rc['role']))
                        if other_rc['event'] and self_rc['event']:
                            safe_rel_parallel = self_rc['event'].check_event_to_avoid(other_rc['event'])
        for it in checklist:
            if it[0] != it[1]:
                safe_main = 1
        if safe_main or safe_rel_parallel: safe_full = 1
        else: safe_full = 0
        safelist.append(safe_full)

        if not has_rc:
            for p in self.participants:
                if 'rc' in self.participants[p].attributes:
                    safe_rel = self.participants[p].attributes['rc']['event'].check_event_to_avoid(other_event)
                    safelist.append(safe_rel)

        safe = 1
        for s in safelist:
            safe *= s

        return safe
