
statedict = {}
f = open('states.csv')
for line in f:
    (code, name) = line.split(':')
    name=name.strip()
    if code != 'Code':
        statedict['US-'+code] = name

countdict = {}        
f = open('code_to_country.csv')
for line in f:
    (code, name) = line.split(':')
    name=name.strip()
    if code != 'Code':
        countdict[code] = name
        
countdict.update(statedict)

S = ''
for k in sorted(countdict.keys()):
    S+= "%s:%s\n" % (k, countdict[k])
    
f = open('states_and_countries.csv','w')
f.write(S.rstrip('\n'))
f.close()
print "file output."

