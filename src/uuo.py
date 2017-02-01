import sys
import re
import collections
import os
from functools import reduce

class PList:

  def __init__(self, ls = []):
    self.ls = ls
    
  def get(self, i):
    return self.ls[i]
    
  def set(self, i, v):
    self.ls[i] = v
    
  def __str__(self):
    return str(self.ls)
    
  def length(self):
    return len(self.ls)
    
  def append(self, x):
    self.ls.append(x)

  def drop_head(self):
    head = self.ls[0]
    self.ls = self.ls[1:]
    return head

    
class Atom:
  T_I = 0
  T_D = 1
  T_S = 2
  T_V = 3
  T_Q = 4
  T_L = 5
  
  def __init__(self, value, type_of):
    self.value = value
    self.type_of = type_of
  
  def get(self):
    return self.value
    
  def is_int(self):
    return self.type_of == Atom.T_I
    
  def is_double(self):
    return self.type_of == Atom.T_D
    
  def is_string(self):
    return self.type_of == Atom.T_S
    
  def is_verb(self):
    return self.type_of == Atom.T_V
    
  def is_qverb(self):
    return self.type_of == Atom.T_Q
    
  def is_list(self):
    return self.type_of == Atom.T_L
    
  def __str__(self):
    return "(" + str(self.value) + "|" + str(self.type_of) + ")"
    
  def __repr__(self):
    return self.__str__()
    

class Context:

  def __init__(self, functions):
    self.functions = functions
    self.stack = collections.deque()
    self.location = ("n/a",-1,None)
    
  def push(self, atom):
    self.stack.append(atom)
    
  def pop(self):
    if len(self.stack) == 0:
      print(self.location)
      raise Exception("Stack is empty.")
    return self.stack.pop()
    
  def pop_int(self):
    a = self.pop()
    if not a.is_int():
      raise Exception("Expected I")
    return a
    
  def pop_str(self):
    a = self.pop()
    if not a.is_str():
      raise Exception("Expected S")
    return a
    
  def pop_double(self):
    a = self.pop()
    if not a.is_double():
      raise Exception("Expected D")
    return a
    
  def pop_verb(self):
    a = self.pop()
    if not a.is_verb():
      raise Exception("Expected V")
    return a
    
  def pop_list(self):
    a = self.pop()
    if not a.is_list():
      raise Exception("Expected L")
    return a
    
class Builtins:

  @staticmethod
  def call_helper(context, value):
    if hasattr(Builtins, "b_" + value):
      function = getattr(Builtins, "b_" + value)
      function(context)
    else:
      run(context, to_run = value)

  @staticmethod
  def b_pop(context):
    context.pop()
    
  @staticmethod
  def b_dup(context):
    a = context.pop()
    context.push(a)
    context.push(a)
    
  @staticmethod
  def b_i_add(context):
    b = context.pop_int()
    a = context.pop_int()
    context.push(Atom(a.value+b.value, Atom.T_I))

  @staticmethod
  def b_i_sub(context):
    b = context.pop_int()
    a = context.pop_int()
    context.push(Atom(a.value-b.value, Atom.T_I))

  @staticmethod
  def b_i_mul(context):
    b = context.pop_int()
    a = context.pop_int()
    context.push(Atom(a.value*b.value, Atom.T_I))

  @staticmethod
  def b_i_div(context):
    b = context.pop_int()
    a = context.pop_int()
    context.push(Atom(a.value//b.value, Atom.T_I))

  @staticmethod
  def b_i_equ(context):
    b = context.pop_int()
    a = context.pop_int()
    result = 1 if a.value == b.value else 0
    context.push(Atom(result, Atom.T_I))
    
  @staticmethod
  def b_dump(context):
    a = context.pop()
    print(a)
    
  @staticmethod
  def b_fail(context):
    print(context.stack)
    print(context.location)
    input('moo')
    raise Exception("I had to fail")
    
  @staticmethod
  def b_list(context):
    context.push(Atom(PList([]), Atom.T_L))
    
  @staticmethod
  def b_xs_prepend(context):
    b = context.pop()
    a = context.pop_list()
    a.value.insert(0, b)
    context.push(a)
    
  @staticmethod
  def b_xs_append(context):
    b = context.pop()
    a = context.pop_list()
    a.value.append(b)
    context.push(a)
    
  @staticmethod
  def b_xs_length(context):
    a = context.pop_list()
    context.push(Atom(a.value.length(), Atom.T_I))
    
  @staticmethod
  def b_xs_uncons(context):
    a = context.pop_list()
    if(a.value.length() == 0):
      raise Exception('Empty list.')
    
    head = a.value.drop_head()
    context.push(a)
    context.push(head) 
    
  @staticmethod
  def b_typeof(context):
    a = context.pop()
    context.push(Atom(a.type_of, Atom.T_I))    
      
  @staticmethod
  def b_ifcall(context):
    b = context.pop_verb()
    a = context.pop_int()
    if(a.value != 0):
        Builtins.call_helper(context, b.value)

  @staticmethod
  def b_ifncall(context):
    b = context.pop_verb()
    a = context.pop_int()
    if(a.value == 0):
        Builtins.call_helper(context, b.value)
    
def run(context, to_run = "main"):
  function = context.functions[to_run]
  context.location = (to_run,-1)
  
  i = 0

  for atom in function:
    context.location = (to_run, i, atom)
    if atom.is_verb():
      Builtins.call_helper(context, atom.value)
    elif atom.is_qverb():
      context.push(Atom(atom.value, Atom.T_V))
    else:
      context.push(atom)
    i += 1
    
  
def parse(contents, imports={}):
  global INCLUDE_DIR
  functions = contents.split(";")
  fns = {}
  for function in functions:
    atms = []
    tokens = function.split()
    if(len(tokens) > 0):
      name = tokens[0]
      tokens = tokens[1:]
      for token in tokens:
        if re.match("^@(.*)$", token):
          path = INCLUDE_DIR + token[1:]
          if(path in imports):
            continue
          imports[path] = True
          contents_ = load_contents(path)
          fns.update(parse(contents_, imports))
        elif re.match("^-?[0-9]+$", token):
          atms.append(Atom(int(token,10), Atom.T_I))
        elif re.match("^-?[0-9]+\.[0-9]*$", token):
          atms.append(Atom(float(token), Atom.T_D))
        elif re.match("^\"(.*)\"$", token):
          atms.append(Atom(token[1:-1], Atom.T_S))
        elif re.match("^&[a-zA-Z_]{1}[a-zA-Z_0-9]*$", token):
          atms.append(Atom(token[1:], Atom.T_Q))
        elif re.match("^[a-zA-Z_]{1}[a-zA-Z_0-9]*$", token):
          atms.append(Atom(token, Atom.T_V))
        else:
          raise Exception("Invalid token :D")
      fns[name] = atms
  return fns

def load_contents(path):
  fhndl = open(path,"r")
  lines = []
  for line in fhndl:
    line = line.strip()
    if line.startswith("#"):
      continue
    lines.append(line)
  fhndl.close()
  return reduce(lambda a,b: a + " " + b, lines)
  
def main():
  if(len(sys.argv) != 3):
    print_usage();
    return None
    
  file = sys.argv[1]
  contents = load_contents(file)
  global INCLUDE_DIR
  INCLUDE_DIR = sys.argv[2]
  
  functions = parse(contents)
  run(Context(functions))
  
def print_usage():
  print("Usage: uuo <file> <include dir>")

if __name__ == "__main__":
  main()
