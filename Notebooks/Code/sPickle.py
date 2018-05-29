'''Streaming pickle implementation for efficiently serializing and
de-serializing an iterable (e.g., list)

Created on 2010-06-19 by Philip Guo

Limitations:

  - Only works with ASCII-based pickles (protocol=0), since s_load reads
  in one line at a time

'''

try:
  from cPickle import dumps, loads
except ImportError:
  from pickle import dumps, loads


def s_dump(iterable_to_pickle, file_obj):
  '''dump contents of an iterable iterable_to_pickle to file_obj, a file
  opened in write mode'''
  for elt in iterable_to_pickle:
    s_dump_elt(elt, file_obj)


def s_dump_elt(elt_to_pickle, file_obj):
  '''dumps one element to file_obj, a file opened in write mode'''
  pickled_elt_str = dumps(elt_to_pickle)
  file_obj.write(pickled_elt_str)
  # record separator is a blank line
  # (since pickled_elt_str might contain its own newlines)
  file_obj.write('x00\x00'.encode())

def bytes_from_file(f, chunksize=8192):
  while True:
    chunk = f.read(chunksize)
    if chunk:
      for b in chunk:
        yield b
    else:
      break

def s_load(file_obj):
  '''load contents from file_obj, returning a generator that yields one
  element at a time'''
  cur_elt = []
  prev_was_null = False
  for b in bytes_from_file(file_obj):
    if b == '\x00'.encode():
      if prev_was_null:
        elt = loads(b''.join(cur_elt[:-1]))
        cur_elt = []
        yield elt
      else:
        prev_was_null = True
    else:
      cur_elt.append(b)
