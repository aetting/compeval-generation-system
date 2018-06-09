from dataset_helpers import *

phs = eventStart({'name':'help','frame':'transitive','tense':'pres','aspect':'neut','pol':'pos','voice':'active'})
phs.participants['agent'] = characterStart({'name':'professor','num':'pl'})
phs.participants['patient'] = characterStart({'name':'student','num':'pl'})
wp = {'reltype':'orc','relevent':phs}
testev = eventStart({'name':'follow','frame':'which','tense':'pres','aspect':'neut','pol':'pos','voice':'active','wp':wp})
testev.participants['agent'] = characterStart({'name':'woman','num':'sg'})
testev.bindings[Variable('?nagent')] = 'sg'
testev.bindings[Variable('?nwpagent')] = 'pl'
testev.bindings[Variable('?nwppatient')] = 'pl'

mainList = {'transitive':['help'],'intransitive':[],'noun':['professor']}
main2List = {'transitive':['follow'],'intransitive':[],'noun':['window']}
profList = {'transitive':[],'intransitive':[],'noun':['professor']}

recList = {'transitive':['recommend'],'intransitive':[],'noun':[]}

actneut = eventStart({'voice':'active','aspect':'neut'})
neut = eventStart({'aspect':'neut'})
pas = eventStart({'voice':'passive'})


main = eventStart({'name':'help'})
main.participants['agent'] = characterStart({'name':'professor'})

mainb = eventStart({'name':'help'})
mainb.participants['patient'] = characterStart({'name':'professor'})

mainP = eventStart({'name':'help','tense':'past','aspect':'neut','pol':'pos'})
mainP.participants['agent'] = characterStart({'name':'professor'})

mainbP = eventStart({'name':'help','tense':'past','aspect':'neut','pol':'pos'})
mainbP.participants['patient'] = characterStart({'name':'professor'})

main2 = eventStart({'name':'follow'})
main2.participants['agent'] = characterStart({'name':'window'})

rceventmain1 = eventStart({'pol':'pos','aspect':'prog','voice':'active'})
main3n = eventStart({'name':'help','voice':'active','pol':'neg','aspect':'prog'})
main3n.participants['agent'] = characterStart()
main3n.participants['agent'].attributes['rc'] = {'rtype':None,'role':None,'event':rceventmain1}

rceventmain2 = eventStart({'pol':'neg','aspect':'prog','voice':'active'})
main3p = eventStart({'voice':'active','pol':'pos','aspect':'prog'})
main3p.participants['agent'] = characterStart()
main3p.participants['agent'].attributes['rc'] = {'rtype':None,'role':None,'event':rceventmain2}

rceventmain1 = eventStart({'pol':'neg','aspect':'prog','voice':'active','name':'help'})
main4n = eventStart({'frame':'transitive','voice':'active','pol':'pos','aspect':'prog'})
main4n.participants['patient'] = characterStart()
main4n.participants['patient'].attributes['rc'] = {'rtype':None,'role':None,'event':rceventmain1}

rceventmain2 = eventStart({'pol':'pos','aspect':'prog','voice':'active'})
main4p = eventStart({'frame':'transitive','voice':'active','pol':'neg','aspect':'prog'})
main4p.participants['patient'] = characterStart()
main4p.participants['patient'].attributes['rc'] = {'rtype':None,'role':None,'event':rceventmain2}

#main pos rc neg
rcpos = eventStart({'pol':'pos','aspect':'prog','voice':'active'})
rcneg = eventStart({'pol':'neg','aspect':'prog','voice':'active'})

mainposagrc = eventStart({'voice':'active','pol':'pos','aspect':'prog'})
mainposagrc.participants['agent'] = characterStart()
mainposagrc.participants['agent'].attributes['rc'] = {'rtype':None,'role':None,'event':rcneg}

mainposparc = eventStart({'voice':'active','pol':'pos','aspect':'prog'})
mainposparc.participants['patient'] = characterStart()
mainposparc.participants['patient'].attributes['rc'] = {'rtype':None,'role':None,'event':rcneg}

mainnegagrc = eventStart({'voice':'active','pol':'neg','aspect':'prog'})
mainnegagrc.participants['agent'] = characterStart()
mainnegagrc.participants['agent'].attributes['rc'] = {'rtype':None,'role':None,'event':rcpos}

mainnegparc = eventStart({'voice':'active','pol':'neg','aspect':'prog'})
mainnegparc.participants['patient'] = characterStart()
mainnegparc.participants['patient'].attributes['rc'] = {'rtype':None,'role':None,'event':rcpos}

mainnegpaneg = eventStart({'voice':'active','pol':'neg','aspect':'prog'})
mainnegparc.participants['patient'] = characterStart()
mainnegparc.participants['patient'].attributes['rc'] = {'rtype':None,'role':None,'event':rcneg}

mainnegagneg = eventStart({'voice':'active','pol':'neg','aspect':'prog'})
mainnegparc.participants['agent'] = characterStart()
mainnegparc.participants['agent'].attributes['rc'] = {'rtype':None,'role':None,'event':rcneg}

#main neg rc pos

task2inputs = {
'xy': {
 'pos': {
  'needEv': [],
  'needList': [],
  'avoidEv': None,
  'avoidList':[]
  },
 'neg': {
  # 'needEv': [mainposagrc],
  'needEv': [mainposagrc,mainposparc,mainnegagrc,mainnegparc],
  'needList': [],
  'avoidEv': None,
  'avoidList':[]
  }},
'xy2': {
 'neg': {
  # 'needEv': [mainposagrc],
  'needEv': [mainposagrc,mainposparc,mainnegagrc,mainnegparc],
  'needList': [],
  'avoidEv': [mainnegagneg],
  'avoidList':[]
  }},
'hasprof': {
 'pos': {
  'needEv': None,
  'needList': profList,
  'avoidEv': None,
  'avoidList':[]
  },
 'neg': {
  'needEv': None,
  'needList': [],
  'avoidEv': None,
  'avoidList': profList
  }},
'profhelp': {
 'pos': {
  'needEv': main,
  'needList': [],
  'avoidEv': None,
  'avoidList':[]
  },
 'neg': {
  'needEv': None,
  'needList': mainList,
  'avoidEv': [main],
  'avoidList':[]
  }},
'profhelp2': {
 'pos': {
  'needEv': mainP,
  'needList': [],
  'avoidEv': None,
  'avoidList':[]
  },
 'neg': {
  'needEv': mainbP,
  'needList': [],
  'avoidEv': None,
  'avoidList':[]
  }},
'profhelppat': {
 'pos': {
  'needEv': mainb,
  'needList': [],
  'avoidEv': None,
  'avoidList':[]
  },
 'neg': {
  'needEv': None,
  'needList': mainList,
  'avoidEv': [mainb],
  'avoidList':[]
  }},
'windfoll': {
 'pos': {
  'needEv': main2,
  'needList': [],
  'avoidEv': None,
  'avoidList':[]
  },
 'neg': {
  'needEv': None,
  'needList': main2List,
  'avoidEv': [main2],
  'avoidList':[]
  }},
'neghelp': {
 'pos': {
  'needEv': main3p,
  'needList': [],
  'avoidEv': None,
  'avoidList':[]
  },
 'neg': {
  'needEv': main3n,
  'needList': [],
  'avoidEv': None,
  'avoidList':[]
  }},
'neghelp2': {
 'pos': {
  'needEv': main4p,
  'needList': [],
  'avoidEv': None,
  'avoidList':[]
  },
 'neg': {
  'needEv': main4n,
  'needList': [],
  'avoidEv': None,
  'avoidList':[]
  }}
  }

role_rc_structures_dict = {
'xy' :
{'intransitive':[{'agent':'none'},{'agent':'transitive'},{'agent':'intransitive'}],
'transitive':[{'agent':'none','patient':'none'},{'agent':'none','patient':'transitive'},{'agent':'none','patient':'intransitive'},
        {'agent':'transitive','patient':'none'},{'agent':'intransitive','patient':'none'},
        ]},
'xy2' :
{'intransitive':[{'agent':'none'},{'agent':'transitive'},{'agent':'intransitive'}],
'transitive':[{'agent':'none','patient':'none'},{'agent':'none','patient':'transitive'},{'agent':'none','patient':'intransitive'},
        {'agent':'transitive','patient':'none'},{'agent':'transitive','patient':'transitive'},{'agent':'transitive','patient':'intransitive'},
        {'agent':'intransitive','patient':'none'},{'agent':'intransitive','patient':'transitive'},{'agent':'intransitive','patient':'intransitive'},
        ]},
'neghelp':
{'intransitive':[],
'transitive':[{'agent':'intransitive','patient':'none'},{'agent':'transitive','patient':'none'}]
  },
'neghelp2':
{'intransitive':[],
'transitive':[{'agent':'none','patient':'transitive'}]
  },
'profhelp2' :
{'intransitive':[{'agent':'none'},{'agent':'transitive'},{'agent':'intransitive'}],
'transitive':[{'agent':'none','patient':'none'},{'agent':'none','patient':'transitive'},{'agent':'none','patient':'intransitive'},
        {'agent':'transitive','patient':'none'},{'agent':'intransitive','patient':'none'},
        ]},
'other' :
{'intransitive':[{'agent':'none'},{'agent':'transitive'},{'agent':'intransitive'}],
'transitive':[{'agent':'none','patient':'none'},{'agent':'none','patient':'transitive'},{'agent':'none','patient':'intransitive'},
        {'agent':'transitive','patient':'none'},{'agent':'transitive','patient':'transitive'},{'agent':'transitive','patient':'intransitive'},
        {'agent':'intransitive','patient':'none'},{'agent':'intransitive','patient':'transitive'},{'agent':'intransitive','patient':'intransitive'},
        ]}
}
