import cProfile, pstats
import shutil
import os
import logging
import time
import multiprocessing
import timeit
import warnings
import uuid
import sympy

warnings.filterwarnings('ignore')

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

operations = (' ** ', ' * ', ' + ', ' - ', ' / ', '')
neg = ('', '-')
parens = (
    ('', ' ( ', '', ' ( ', '', ' ( ', '', ' ( ', '', ' )))) '),
    ('', ' ( ', '', ' ( ', '', ' (( ', '', '', ' ) ', ' ))) '),
    ('', ' ( ', '', ' (( ', '', '', ' ) ', ' ( ', '', ' ))) '),
    ('', ' ( ', '', ' (( ', '', ' ( ', '', '', ' )) ', ' )) '),
    ('', ' ( ', '', ' ((( ', '', '', ' ) ', '', ' ) ', ' )) '),
    ('', ' (( ', '', '', ' ) ', ' ( ', '', ' ( ', '', ' ))) '),
    ('', ' (( ', '', '', ' ) ', ' (( ', '', '', ' ) ', ' )) '),
    ('', ' (( ', '', ' ( ', '', '', ' )) ', ' ( ', '', ' )) '),
    ('', ' ((( ', '', '', ' ) ', '', ' ) ', ' ( ', '', ' )) '),
    ('', ' (( ', '', ' ( ', '', ' ( ', '', '', ' ))) ', ' ) '),
    ('', ' (( ', '', ' (( ', '', '', ' ) ', '', ' )) ', ' ) '),
    ('', ' ((( ', '', '', ' ) ', ' ( ', '', '', ' )) ', ' ) '),
    ('', ' ((( ', '', ' ( ', '', '', ' )) ', '', ' ) ', ' ) '),
    ('', ' (((( ', '', '', ' ) ', '', ' ) ', '', ' ) ', ' ) '),
    (' ( ', '', ' ) ', ' ( ', '', ' ( ', '', ' ( ', '', ' ))) '),
    (' ( ', '', ' ) ', ' ( ', '', ' (( ', '', '', ' ) ', ' )) '),
    (' ( ', '', ' ) ', ' (( ', '', '', ' ) ', ' ( ', '', ' )) '),
    (' ( ', '', ' ) ', ' (( ', '', ' ( ', '', '', ' )) ', ' ) '),
    (' ( ', '', ' ) ', ' ((( ', '', '', ' ) ', '', ' ) ', ' ) '),
    (' ( ', ' ( ', '', '', ' )) ', ' ( ', '', ' ( ', '', ' )) '),
    (' ( ', ' ( ', '', '', ' )) ', ' (( ', '', '', ' ) ', ' ) '),
    (' (( ', '', ' ) ', '', ' ) ', ' ( ', '', ' ( ', '', ' )) '),
    (' (( ', '', ' ) ', '', ' ) ', ' (( ', '', '', ' ) ', ' ) '),
    (' ( ', ' ( ', '', ' ( ', '', '', ' ))) ', ' ( ', '', ' ) '),
    (' ( ', ' (( ', '', '', ' ) ', '', ' )) ', ' ( ', '', ' ) '),
    (' (( ', '', ' ) ', ' ( ', '', '', ' )) ', ' ( ', '', ' ) '),
    (' (( ', ' ( ', '', '', ' )) ', '', ' ) ', ' ( ', '', ' ) '),
    (' ((( ', '', ' ) ', '', ' ) ', '', ' ) ', ' ( ', '', ' ) '),
    (' ( ', ' ( ', '', ' ( ', '', ' ( ', '', '', ' )))) ', ''),
    (' ( ', ' ( ', '', ' (( ', '', '', ' ) ', '', ' ))) ', ''),
    (' ( ', ' (( ', '', '', ' ) ', ' ( ', '', '', ' ))) ', ''),
    (' ( ', ' (( ', '', ' ( ', '', '', ' )) ', '', ' )) ', ''),
    (' ( ', ' ((( ', '', '', ' ) ', '', ' ) ', '', ' )) ', ''),
    (' (( ', '', ' ) ', ' ( ', '', ' ( ', '', '', ' ))) ', ''),
    (' (( ', '', ' ) ', ' (( ', '', '', ' ) ', '', ' )) ', ''),
    (' (( ', ' ( ', '', '', ' )) ', ' ( ', '', '', ' )) ', ''),
    (' ((( ', '', ' ) ', '', ' ) ', ' ( ', '', '', ' )) ', ''),
    (' (( ', ' ( ', '', ' ( ', '', '', ' ))) ', '', ' ) ', ''),
    (' (( ', ' (( ', '', '', ' ) ', '', ' )) ', '', ' ) ', ''),
    (' ((( ', '', ' ) ', ' ( ', '', '', ' )) ', '', ' ) ', ''),
    (' ((( ', ' ( ', '', '', ' )) ', '', ' ) ', '', ' ) ', ''),
    (' (((( ', '', ' ) ', '', ' ) ', '', ' ) ', '', ' ) ', '')
)


# https://stackoverflow.com/a/6447533
def parenthesized(exprs):
    if len(exprs) == 1:
        yield f'{exprs[0]}.'
    else:
        first_exprs = []
        last_exprs = list(exprs)
        while 1 < len(last_exprs):
            first_exprs.append(last_exprs.pop(0))
            for x in parenthesized(first_exprs):
                if 1 < len(first_exprs):
                    x = f'({x})'
                for y in parenthesized(last_exprs):
                    if 1 < len(last_exprs):
                        y = f'({y})'
                    for op in [' + ', ' - ', ' * ', ' / ', ' ** ']:
                        yield f'{x}{op}{y}'


def parens_permutations():
    parens = [
        r'{a}{op0} ( {b}{op1} ( {c}{op2} ( {d}{op3} ( {e}{op4}{f} ) ) ) )',
        r'{a}{op0} ( {b}{op1} ( {c}{op2} ( ( {d}{op3}{e} ) {op4}{f} ) ) )',
        r'{a}{op0} ( {b}{op1} ( ( {c}{op2}{d} ) {op3} ( {e}{op4}{f} ) ) )',
        r'{a}{op0} ( {b}{op1} ( ( {c}{op2} ( {d}{op3}{e} ) ) {op4}{f} ) )',
        r'{a}{op0} ( {b}{op1} ( ( ( {c}{op2}{d} ) {op3}{e} ) {op4}{f} ) )',
        r'{a}{op0} ( ( {b}{op1}{c} ) {op2} ( {d}{op3} ( {e}{op4}{f} ) ) )',
        r'{a}{op0} ( ( {b}{op1}{c} ) {op2} ( ( {d}{op3}{e} ) {op4}{f} ) )',
        r'{a}{op0} ( ( {b}{op1} ( {c}{op2}{d} ) ) {op3} ( {e}{op4}{f} ) )',
        r'{a}{op0} ( ( ( {b}{op1}{c} ) {op2}{d} ) {op3} ( {e}{op4}{f} ) )',
        r'{a}{op0} ( ( {b}{op1} ( {c}{op2} ( {d}{op3}{e} ) ) ) {op4}{f} )',
        r'{a}{op0} ( ( {b}{op1} ( ( {c}{op2}{d} ) {op3}{e} ) ) {op4}{f} )',
        r'{a}{op0} ( ( ( {b}{op1}{c} ) {op2} ( {d}{op3}{e} ) ) {op4}{f} )',
        r'{a}{op0} ( ( ( {b}{op1} ( {c}{op2}{d} ) ) {op3}{e} ) {op4}{f} )',
        r'{a}{op0} ( ( ( ( {b}{op1}{c} ) {op2}{d} ) {op3}{e} ) {op4}{f} )',
        r'( {a}{op0}{b} ) {op1} ( {c}{op2} ( {d}{op3} ( {e}{op4}{f} ) ) )',
        r'( {a}{op0}{b} ) {op1} ( {c}{op2} ( ( {d}{op3}{e} ) {op4}{f} ) )',
        r'( {a}{op0}{b} ) {op1} ( ( {c}{op2}{d} ) {op3} ( {e}{op4}{f} ) )',
        r'( {a}{op0}{b} ) {op1} ( ( {c}{op2} ( {d}{op3}{e} ) ) {op4}{f} )',
        r'( {a}{op0}{b} ) {op1} ( ( ( {c}{op2}{d} ) {op3}{e} ) {op4}{f} )',
        r'( {a}{op0} ( {b}{op1}{c} ) ) {op2} ( {d}{op3} ( {e}{op4}{f} ) )',
        r'( {a}{op0} ( {b}{op1}{c} ) ) {op2} ( ( {d}{op3}{e} ) {op4}{f} )',
        r'( ( {a}{op0}{b} ) {op1}{c} ) {op2} ( {d}{op3} ( {e}{op4}{f} ) )',
        r'( ( {a}{op0}{b} ) {op1}{c} ) {op2} ( ( {d}{op3}{e} ) {op4}{f} )',
        r'( {a}{op0} ( {b}{op1} ( {c}{op2}{d} ) ) ) {op3} ( {e}{op4}{f} )',
        r'( {a}{op0} ( ( {b}{op1}{c} ) {op2}{d} ) ) {op3} ( {e}{op4}{f} )',
        r'( ( {a}{op0}{b} ) {op1} ( {c}{op2}{d} ) ) {op3} ( {e}{op4}{f} )',
        r'( ( {a}{op0} ( {b}{op1}{c} ) ) {op2}{d} ) {op3} ( {e}{op4}{f} )',
        r'( ( ( {a}{op0}{b} ) {op1}{c} ) {op2}{d} ) {op3} ( {e}{op4}{f} )',
        r'( {a}{op0} ( {b}{op1} ( {c}{op2} ( {d}{op3}{e} ) ) ) ) {op4}{f}',
        r'( {a}{op0} ( {b}{op1} ( ( {c}{op2}{d} ) {op3}{e} ) ) ) {op4}{f}',
        r'( {a}{op0} ( ( {b}{op1}{c} ) {op2} ( {d}{op3}{e} ) ) ) {op4}{f}',
        r'( {a}{op0} ( ( {b}{op1} ( {c}{op2}{d} ) ) {op3}{e} ) ) {op4}{f}',
        r'( {a}{op0} ( ( ( {b}{op1}{c} ) {op2}{d} ) {op3}{e} ) ) {op4}{f}',
        r'( ( {a}{op0}{b} ) {op1} ( {c}{op2} ( {d}{op3}{e} ) ) ) {op4}{f}',
        r'( ( {a}{op0}{b} ) {op1} ( ( {c}{op2}{d} ) {op3}{e} ) ) {op4}{f}',
        r'( ( {a}{op0} ( {b}{op1}{c} ) ) {op2} ( {d}{op3}{e} ) ) {op4}{f}',
        r'( ( ( {a}{op0}{b} ) {op1}{c} ) {op2} ( {d}{op3}{e} ) ) {op4}{f}',
        r'( ( {a}{op0} ( {b}{op1} ( {c}{op2}{d} ) ) ) {op3}{e} ) {op4}{f}',
        r'( ( {a}{op0} ( ( {b}{op1}{c} ) {op2}{d} ) ) {op3}{e} ) {op4}{f}',
        r'( ( ( {a}{op0}{b} ) {op1} ( {c}{op2}{d} ) ) {op3}{e} ) {op4}{f}',
        r'( ( ( {a}{op0} ( {b}{op1}{c} ) ) {op2}{d} ) {op3}{e} ) {op4}{f}',
        r'( ( ( ( {a}{op0}{b} ) {op1}{c} ) {op2}{d} ) {op3}{e} ) {op4}{f}'
    ]
    for p in parens:
        parens_list = list()
        parens_list.append(p[:p.find('{a}')])
        parens_list.append(p[p.find('{op0}') + 5:p.find('{b}')])
        parens_list.append(p[p.find('{b}') + 3:p.find('{op1}')])
        parens_list.append(p[p.find('{op1}') + 5:p.find('{c}')])
        parens_list.append(p[p.find('{c}') + 3:p.find('{op2}')])
        parens_list.append(p[p.find('{op2}') + 5:p.find('{d}')])
        parens_list.append(p[p.find('{d}') + 3:p.find('{op3}')])
        parens_list.append(p[p.find('{op3}') + 5:p.find('{e}')])
        parens_list.append(p[p.find('{e}') + 3:p.find('{op4}')])
        parens_list.append(p[p.find('{f}') + 3:])
        print([x.replace(' ', '') for x in parens_list])


# https://stackoverflow.com/a/312464
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def construct_nice_friedman_expr_list(n, neg0, neg1, neg2, neg3, neg4, neg5, profiling):
    if profiling:
        pr = cProfile.Profile()
        pr.enable()

    expr_list = list()
    strN = str(n)
    zero_in_n = '0' in strN
    n0 = strN[0]
    n1 = strN[1]
    n2 = strN[2]
    n3 = strN[3]
    n4 = strN[4]
    n5 = strN[5]

    count = 0

    # Pre pre prune
    # Remove if -0 exists
    for op0 in operations:
        for op1 in operations:
            for op2 in operations:
                for op3 in operations:
                    for op4 in operations:
                        # Pre prune
                        # Remove if no '**' because expr requires it to be big enough
                        ops = [op0, op1, op2, op3, op4]
                        if ' ** ' not in ops:
                            continue
                        # Remove if too many concatenations (4 or more)
                        if (not bool(op0)) + (not bool(op1)) + (not bool(op2)) + (not bool(op3)) + (not bool(op4)) >= 4:
                            continue
                        # Remove '+ -' and '- -' because it is redundant (equivalent to - and +)
                        # Remove '* -' and '/ -' because it is redundant (Commutative Property)
                        if ((op0 and ' ** ' != op0 and neg1)
                                or (op1 and ' ** ' != op1 and neg2)
                                or (op2 and ' ** ' != op2 and neg3)
                                or (op3 and ' ** ' != op3 and neg4)
                                or (op4 and ' ** ' != op4 and neg5)):
                            continue

                        prelim_expr_list = list()
                        for (p0, p1, p2, p3, p4, p5, p6, p7, p8, p9) in parens:
                            f0 = '.'
                            f1 = '.'
                            f2 = '.'
                            f3 = '.'
                            f4 = '.'
                            f5 = '.'
                            # f'{p0}{neg0}{n0}{f0}{op0}{p1}{neg1}{n1}{f1}{p2}{op1}{p3}{neg2}{n2}{f2}{p4}{op2}{p5}{neg3}{n3}{f3}{p6}{op3}{p7}{neg4}{n4}{f4}{p8}{op4}{neg5}{n5}{f5}{p9}'
                            # Fix expression if concatenation is used
                            move_to_end = ''
                            if not op0:
                                if neg1 or '0' == n0:
                                    continue
                                move_to_end = f'{move_to_end}{p1}'
                                p1 = ''
                                f0 = ''
                            if not op1:
                                if neg2 or (op0 and '0' == n1):
                                    continue
                                move_to_end = f'{move_to_end}{p2}{p3}'
                                p2 = ''
                                p3 = ''
                                f1 = ''
                            if not op2:
                                if neg3 or (op1 and '0' == n2):
                                    continue
                                move_to_end = f'{move_to_end}{p4}{p5}'
                                p4 = ''
                                p5 = ''
                                f2 = ''
                            if not op3:
                                if neg4 or (op2 and '0' == n3):
                                    continue
                                move_to_end = f'{move_to_end}{p6}{p7}'
                                p6 = ''
                                p7 = ''
                                f3 = ''
                            if not op4:
                                if neg5 or (op3 and '0' == n4):
                                    continue
                                move_to_end = f'{move_to_end}{p8}'
                                p8 = ''
                                f4 = ''
                            for c in move_to_end:
                                if c == '(':
                                    p0 = f'( {p0}'
                                elif c == ')':
                                    p9 = f'{p9} )'

                            expr = f'{p0}{neg0}{n0}{f0}{op0}{p1}{neg1}{n1}{f1}{p2}{op1}{p3}{neg2}{n2}{f2}{p4}{op2}{p5}{neg3}{n3}{f3}{p6}{op3}{p7}{neg4}{n4}{f4}{p8}{op4}{neg5}{n5}{f5}{p9}'

                            # Remove divide by 0
                            if zero_in_n:
                                if (op0 == ' / ' and not p1 and '0' == n1
                                        or op1 == ' / ' and not p3 and '0' == n2
                                        or op2 == ' / ' and not p5 and '0' == n3
                                        or op3 == ' / ' and not p7 and '0' == n4
                                        or op4 == ' / ' and '0' == n5):
                                    continue

                            # Add to list
                            prelim_expr_list.append(expr)

                        if prelim_expr_list:
                            count += len(prelim_expr_list)
                            expr_list.append((n, prelim_expr_list, profiling))

    if profiling:
        pr.disable()
        fname = f'{uuid.uuid4()}.pstats'
        pr.dump_stats(f'profilings/{fname}')
    return expr_list, count


def write_exprs_to_file(exprs):
    with open('exprs.txt', 'a') as expr_file:
        for expr in exprs:
            expr_file.write(f'{expr}\n')


def simplify_expression(expr):
    paren_stack = list()
    paren_pairs = list()
    for i in range(len(expr)):
        c = expr[i]
        if c == '(':
            paren_stack.append(i)
        elif c == ')':
            paren_pairs.append((paren_stack.pop(-1), i))
    for i, j in paren_pairs:
        expr_removed_parens = f'{expr[:i]} {expr[i+1:j]} {expr[j+1:]}'
        if eval(expr) == eval(expr_removed_parens):
            expr = expr_removed_parens
    return expr.replace(' ', '').replace('.', '')

def nice_friedman_solve(n, prelim_expr_list, profiling):
    friedman_expr = None
    if profiling:
        pr = cProfile.Profile()
        pr.enable()

    for expr in prelim_expr_list:
        try:
            if abs(n - eval(expr.strip())) < 1e-6:
                expr = simplify_expression(expr)
                logger.info(f'{n} = {expr}')
                friedman_expr = expr
                break

        except ZeroDivisionError:
            pass
        except OverflowError:
            pass

    if profiling:
        pr.disable()
        fname = f'{uuid.uuid4()}.pstats'
        pr.dump_stats(f'profilings/{fname}')

    return friedman_expr


def solve_nice_friedman_multicore(n, profiling=True):
    args = []
    strN = str(n)
    zero_in_n = '0' in strN
    for neg0 in neg:
        for neg1 in neg:
            for neg2 in neg:
                for neg3 in neg:
                    for neg4 in neg:
                        for neg5 in neg:
                            # Skip if -0

                            if zero_in_n:
                                if not (neg0 and strN[0] == '0'
                                        or neg1 and strN[1] == '0'
                                        or neg2 and strN[2] == '0'
                                        or neg3 and strN[3] == '0'
                                        or neg4 and strN[4] == '0'
                                        or neg5 and strN[5] == '0'):
                                    args.append((n, neg0, neg1, neg2, neg3, neg4, neg5, profiling))
                            else:
                                args.append((n, neg0, neg1, neg2, neg3, neg4, neg5, profiling))

    with multiprocessing.Pool(8) as p:
        exprs = []
        num_exprs = 0
        logger.debug(f'Constructing expressions')
        t0 = time.time()
        exprs_chunks = p.starmap(construct_nice_friedman_expr_list, args)
        for expr, count in exprs_chunks:
            exprs.extend(expr)
            num_exprs += count

        logger.debug(f'Evaluating {num_exprs} expressions')
        solns = p.starmap(nice_friedman_solve, exprs)
        results = []
        with open('nice_friedman_numbers.txt', 'a') as num_file:
            for result in solns:
                if result is not None:
                    num_file.write(f'{n} = {result}\n')
                    results.append(result)

    # for _, exprs_list, _ in exprs:
    #     write_exprs_to_file(exprs_list)

    logger.debug(f'Solved all expressions in {round(time.time() - t0, 3)} secs')
    return results


def nice_friedman_solver_multicore():
    nice_friedman_numbers = set()
    guessed_numbers = set()
    try:
        with open('nice_friedman_numbers.txt', 'r') as num_file:
            for line in num_file:
                if line.strip():
                    num = int(line.strip().split(' ')[0])
                    nice_friedman_numbers.add(num)
                    guessed_numbers.add(num)
    except FileNotFoundError:
        pass

    try:
        with open('guessed_numbers.txt') as guess_file:
            for line in guess_file:
                if line.strip():
                    guessed_numbers.add(int(line.strip()))
    except FileNotFoundError:
        pass

    mod = 0
    t0 = time.time()
    for n in range(100000, 1000000):
        if n in guessed_numbers:
            continue
        logger.debug(f'\nChecking n={n}')
        mod += 1
        mod %= 100
        if mod == 0:
            logger.info(f'Checked numbers {n - 100} - {n - 1} in {round(time.time() - t0, 3)} seconds')
            t0 = time.time()
        results = solve_nice_friedman_multicore(n, profiling=False)
        with open('guessed_numbers.txt', 'a') as guess_file:
            guess_file.write(f'{n}\n')
        if results:
            nice_friedman_numbers.add(n)


def main(profiling=True):
    if os.path.exists('profilings/'):
        logger.info('Deleting profilings')
        shutil.rmtree('profilings/')
    if profiling:
        os.mkdir('profilings')

    # construct_nice_friedman_expr_list(123465)
    # solve_nice_friedman_multicore(117660, profiling=profiling)
    nice_friedman_solver_multicore()
    # timeit.timeit("eval_def_1('-1 - (( 1 - (( 7 ** 6 ) / 4 )) * 4 )')", number=100000, setup='from __main__ import eval_def_1')

    if profiling:
        stats = pstats.Stats()
        for root, dirs, files in os.walk('profilings'):
            for filename in files:
                stats.add(pstats.Stats(os.path.join(root, filename)))
        stats.sort_stats('ncalls')
        stats.strip_dirs()
        stats.print_stats()

    if os.path.exists('profilings/'):
        logger.info('Deleting profilings')
        shutil.rmtree('profilings/')
        logger.info('Done!')
