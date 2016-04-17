import sys
import re
import collections

class Atom:
  T_I = 0
  T_D = 1
  T_S = 2
  T_V = 3
  
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
    
  def __str__(self):
    return "(" + `self.value` + "|" + `self.type_of` + ")"
    
  def __repr__(self):
    return self.__str__()
    

class Context:

  def __init__(self, functions):
    self.functions = functions
    self.stack = collections.deque()
    
  def push(self, atom):
    self.stack.append(atom)
    
  def pop(self):
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
    
class Builtins:

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
  def b_dump(context):
    a = context.pop()
    print a
    
def run(context, to_run = "main",):
  function = context.functions[to_run]
  
  for atom in function:
    if atom.is_verb():
      if hasattr(Builtins, "b_" + atom.value):
        getattr(Builtins, "b_" + atom.value)(context)
      else:
        run(context, atom.value)
    else:
      context.push(atom)
    
  
def parse(contents, imports={}):
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
          path = token[1:]
          if(path in imports):
            continue
          imports[path] = True
          contents_ = load_contents(path)
          fns.update(parse(contents_, imports))
        elif re.match("^[0-9]*$", token):
          atms.append(Atom(int(token,10), Atom.T_I))
        elif re.match("^[0-9]*\.[0-9]*$", token):
          atms.append(Atom(float(token), Atom.T_D))
        elif re.match("^\"(.*)\"$", token):
          atms.append(Atom(token[1:-1], Atom.T_S))
        else:
          atms.append(Atom(token, Atom.T_V))
      fns[name] = atms
  return fns

def load_contents(path):
  fhndl = open(path,"r")
  data = fhndl.read()
  fhndl.close()
  return data
  
def main():
  if(len(sys.argv) != 2):
    print_usage();
    return None
    
  file = sys.argv[1]
  contents = load_contents(file)
  
  functions = parse(contents)
  run(Context(functions))
  
def print_usage():
  print "Usage: uuo <file>"

if __name__ == "__main__":
  main()