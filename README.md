## Installation

`pip install -r requirements.txt`

## Usage

```
$ ./CAM-interpreter.py -h
usage: CAM-interpreter.py [-h] [--lc LC] [--cc CC] [-l] [-f] [-o] [-p]
                          [--without_steps] [--no_result] [--log LOG]
                          [-v {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

CAM-interpreter and compiler from lambda-code

optional arguments:
  -h, --help            show this help message and exit
  --lc LC, --l_code LC  Code to be executed on CAM-machine in lambda-notation
  --cc CC, --c_code CC  Code to be executed on CAM-machine in CAM-notation
  -l, --library         Choose code from library
  -f, --fast            Use fast CAM-machine realization. Steps can't be saved
                        in this mode
  -o, --opt             Use betta-optimization
  -p, --parallel        Multi-thread computations for <code> constructions.
                        Alpha version, result not guaranteed
  --without_steps       Do not save execution steps
  --no_result           Do not show final result after fast execution
  --log LOG             Log file path
  -v {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --verbose {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level
```

## Example

```
$ ./CAM-interpreter.py --library -o -v INFO
1) x + y = <Λ(<Snd, <x, y>>ε),Λ(Snd+)>ε
2) x + y * z = <Λ(Snd+),<x,<Λ(Snd*),<y,z>>ε>>ε
3) n! = <<Y(if<Snd,'0>=br('1,<Snd,<FstSnd,<Snd,'1>->ε>*))>Λ(if<Snd,'0>=br('1,<Snd,<FstSnd,<Snd,'1>->ε>*))><Snd,'n>ε
4) t + u * t = ((\x.\f.+[x,f x])t)(\x.*[u,x])
5) t + u = (\f.\x.f x)(\x.+[t,x])u
6) t! = (\g.g t)(Y(\f.\n.if(=[n,0])then(1)else(*[n,f(-[n,1])])))

Enter library code number: 1
Enter arguments split by space: 1 2
2016-05-03 13:02:42,825 - INFO - Code before optimization: <Λ(<Snd,<'1,'2>>ε),Λ(Snd+)>ε
2016-05-03 13:02:42,825 - INFO - Optimized code: <Λ(Snd+)><Snd,<'1,'2>>ε
Execution started
+-----+--------------------+---------------------------+----------------------------+
|  №  |        Term        |           Code            |           Stack            |
+=====+====================+===========================+============================+
| 0   |                 () |   <Λ(Snd+)><Snd,<'1,'2>>ε |                         [] |
+-----+--------------------+---------------------------+----------------------------+
| 1   |                 () |    Λ(Snd+)><Snd,<'1,'2>>ε |                       [()] |
+-----+--------------------+---------------------------+----------------------------+
| 2   |           Snd+: () |           ><Snd,<'1,'2>>ε |                       [()] |
+-----+--------------------+---------------------------+----------------------------+
| 3   |     ((), Snd+: ()) |            <Snd,<'1,'2>>ε |                         [] |
+-----+--------------------+---------------------------+----------------------------+
| 4   |     ((), Snd+: ()) |             Snd,<'1,'2>>ε |           [((), Snd+: ())] |
+-----+--------------------+---------------------------+----------------------------+
| 5   |           Snd+: () |                ,<'1,'2>>ε |           [((), Snd+: ())] |
+-----+--------------------+---------------------------+----------------------------+
| 6   |     ((), Snd+: ()) |                 <'1,'2>>ε |                 [Snd+: ()] |
+-----+--------------------+---------------------------+----------------------------+
| 7   |     ((), Snd+: ()) |                  '1,'2>>ε | [Snd+: (), ((), Snd+: ())] |
+-----+--------------------+---------------------------+----------------------------+
| 8   |                  1 |                    ,'2>>ε | [Snd+: (), ((), Snd+: ())] |
+-----+--------------------+---------------------------+----------------------------+
| 9   |     ((), Snd+: ()) |                     '2>>ε |              [Snd+: (), 1] |
+-----+--------------------+---------------------------+----------------------------+
| 10  |                  2 |                       >>ε |              [Snd+: (), 1] |
+-----+--------------------+---------------------------+----------------------------+
| 11  |             (1, 2) |                        >ε |                 [Snd+: ()] |
+-----+--------------------+---------------------------+----------------------------+
| 12  | (Snd+: (), (1, 2)) |                         ε |                         [] |
+-----+--------------------+---------------------------+----------------------------+
| 13  |       ((), (1, 2)) |                      Snd+ |                         [] |
+-----+--------------------+---------------------------+----------------------------+
| 14  |             (1, 2) |                         + |                         [] |
+-----+--------------------+---------------------------+----------------------------+
| 15  |                  3 |                           |                         [] |
+-----+--------------------+---------------------------+----------------------------+
Execution ended, took 0.000922918319702 s
```

## More info

Wiki: [Categorical abstract machine](https://en.wikipedia.org/wiki/Categorical_abstract_machine)
