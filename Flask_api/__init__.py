
d = {'done':True, 'game': 'first', 'boy':'next'}

def jboolify(d):
  if d.done == True:
    d.done = 'true'
  else:
    d.done = 'false'
  return d

print jboolify(d)


#str.replace("is", "was")