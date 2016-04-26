#!/usr/bin/env python
# coding=utf-8
import argparse
import logging
import sys
import time
from code_library import print_lib, get_lib_example
import cam_compiler
from core import CAM


def create_parser():
    m = argparse.ArgumentParser(description='CAM-interpreter and compiler from lambda-code', epilog='Have pleasure')

    m.add_argument('--lc', '--l_code', type=str,
                   help='Code to be executed on CAM-machine in lambda-notation')
    m.add_argument('--cc', '--c_code', type=str,
                   help='Code to be executed on CAM-machine in CAM-notation')
    m.add_argument('-l', '--library', action='store_true', help='Choose code from library')
    m.add_argument('-f', '--fast', action='store_true',
                   help='Use fast CAM-machine realization. Steps can\'t be saved in this mode')
    m.add_argument('-o', '--opt', action='store_true', help='Use betta-optimization')
    m.add_argument('--without_steps', action='store_true', help='Do not save execution steps')
    m.add_argument('--no_result', action='store_true', help='Do not show final result after fast execution')

    m.add_argument('--log', type=str, default=None, help='Log file path')
    m.add_argument('-v', '--verbose', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='WARNING',
                   help="Set the logging level")
    return m


def setup_logger(verbosity_level, log_file=None):
    root = logging.getLogger()
    root.handlers = []
    root.setLevel(verbosity_level)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(verbosity_level)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setLevel(verbosity_level)
        fh.setFormatter(formatter)
        root.addHandler(fh)


def main():
    m = create_parser()
    options = m.parse_args()
    setup_logger(options.verbose, log_file=options.log)
    if not (options.lc or options.cc or options.library):
        logging.error('Lambda code, CAM code or on of the library example needed')
        return
    if options.fast:
        options.without_steps = True
    if options.lc:
        c = cam_compiler.compile_expr(options.l_code)
        logging.info('CAM code after compilation: %s' % c)
    elif options.cc:
        c = options.cc
    else:
        print_lib()
        code, _type = get_lib_example(raw_input("Enter library code number: "))
        if not code:
            return
        else:
            c = cam_compiler.compile_expr(code) if _type == 'l' else code

    k = CAM(c, save_history=not options.without_steps, with_opt=options.opt, fast_method=options.fast)
    print 'Execution started'
    start = time.time()
    if options.fast:
        k.evaluate_fast()
    else:
        k.evaluate()
    end = time.time() - start
    k.print_steps(show_result=not options.no_result)
    print 'Execution ended, took %s s\n' % end


if __name__ == "__main__":
    main()

    # C = u"<Snd,<FstSnd,<Snd,'1>->ε>*"
    # B = u"<<Snd,'0>=br('1," + C + u")"
    # fact = u"<<Y(" + B + u")>Λ(" + B + u")><Snd,'%s>ε" % 100000
    # examples = [fact]
    # for example in examples:
    #     print 'EXAMPLE STARTED'
    #     k = CAM(example, save_history=False, with_opt=False)
    #     start = time.time()
    #     k.evaluate_fast()
    #     # factorial(100000)
    #     end = time.time() - start
    #     k.print_steps(show_result=False)
    #     print 'EXAMPLE ENDED, TOOK %s s\n' % end
    #     del k
