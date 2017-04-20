def frange(start, stop, step):
      i = start
      while i < stop:
          yield i
          i += step

for i in frange(0.5, 1.0, 0.1):
          print(i)