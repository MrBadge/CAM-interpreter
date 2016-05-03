## 

More info here: [Categorical abstract machine interpreter](https://en.wikipedia.org/wiki/Categorical_abstract_machine)

## Installation

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
