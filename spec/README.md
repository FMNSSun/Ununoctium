# Ununoctium Language Specification

*DRAFT - 2016y/4m/17d*

## About

Ununoctium (uuo) is an incredibly simple stack-based progamming language. The language was designed so it can
be implemented and extended with minimal efforts. 

## Syntax and Grammar

The core elements of uuo's syntax are Functions consisting of Atoms. Functions are separated by semicolons `;`. Atoms
are separated by whitespaces such as CR, LF, tabs and space. The first Atom of a Function defines its name. Thus the grammar
is simply:

```
functions = { function }
function = atom, atoms, semicolon
atoms = { atom }
atom = int | double | string | verb
int = /[0-9]*/
double = /[0-9]*\.[0-9]/
string = /\"(.*)\"/
verb = /^[a-zA-Z_]{1}[a-zA-Z_0-9]*$/
qverb = /&^[a-zA-Z_]{1}[a-zA-Z_0-9]*$/
```

*/../ indicates regular expressions*

The difference between `verb` and `qverb` is that a `qverb` will result in the verb being pushed
to the stack rather than being called. Thus a `qverb` can be thought of as the address of the function
or a reference to the function.

## Data types

Supported data types are:
 * `I` - integer providing at least the range of a 32 bit two's complement signed integer
 * `D` - double. Floating point double precision.
 * `S` - string. A sequence of characters.
 * `V` - verb. A verb. 
 * `A` - array. An array.
 * `L` - list. A list (may secretly be an array).
 * `M` - map. Key/Value-Storage

Arrays must provide fast element access. 

## Builtins

If not enough arguments are provided or arguments of wrong type execution stops.
Overflows or underflows when doing calculations are undefined behaviour. Out of bounds
access to List or Array elements that do not exist results in a stop of execution. 


### i_add

```
i_add :: int int -> int
Desc: Integer addition. 
```

### i_lt

```
i_lt :: int:A int:B -> int
Desc: Push 1 if A < B else push 0
```

### i_mul

```
i_mul :: int int -> int
Desc: Integer multiplication
```

### ifelsecall

```
ifelsecall :: int verb:A verb:B ->
Desc: If the provided integer is zero call A otherwise call B.
```

### ifcall

```
ifcall :: int verb ->
Desc: Invokes the function if the provided argument is not zero.
```


### dup

```
dup :: a -> a a
Desc: Duplicate the top element.
```

### fail

```
fail ::
Desc: Causes the interpreter to stop execution and indicate error. Use-cases are mostly
test-suites. The program is expected to return a non-zero exit code to indicate the error. 
Error message is expected to use STDERR. The exact exit code or error message is up to the implementation.  
```

### dump

```
dump :: a ->
Desc: Dump the atom to stdout. What exactly is printed on STDOUT is up to the implementation.
```

### pop

```
pop :: a ->
Desc: Pops an element from the stack.
```
