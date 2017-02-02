def frange(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step


Dfac = []
for i in frange(start=0.5, stop=1.5, step=0.05):
    Dfac.append(0)
    print i

print len(Dfac)
