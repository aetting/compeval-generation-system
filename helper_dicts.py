voices = {
    'transitive':['active','passive'],'intransitive':['active']
   }

roles = {
    'transitive':['patient','agent'],'intransitive':['agent'],'none':['none'],'which':['agent']
   }

rolertype2voice = {
    'agent':{'orc':'passive','src':'active'},
    'patient':{'orc':'active','src':'passive'}
   }

rolevoice2rtype = {
    'agent':{'passive':'orc','active':'src'},
    'patient':{'active':'orc','passive':'src'}
   }

defnum2det = {
    'def':{'sg':'the','pl':'the'},
    'indef':{'sg':'a','pl':'some'},
    'no':{'sg':'no','pl':'no'}
   }
