from nice_friedman_solver import *

logger = logging.getLogger('nice_friedman_solver')
logger.setLevel(logging.ERROR)

def known_nice_friedman_check():
    with open('known_nice_friedmans.txt', 'r') as friedman_file:
        for line in friedman_file:
            error = False
            line = line.strip().replace(' ', '')
            components = line.split('=')
            try:
                if abs(float(components[0]) - eval(components[1])) > 1e-6:
                    error = True
                    print(f'{components[0]} != {components[1]}')
                    new_exprs = solve_nice_friedman_multicore(int(components[0]), profiling=False)
                    print(f'{components[0]} = {new_exprs[0]}')
            except SyntaxError:
                error = True
                print(f'Syntax error for expression {line}')

            if error:
                print()

def new_nice_friedman_check():
    friedmans = set()
    with open('known_nice_friedmans.txt', 'r') as friedman_file:
        for line in friedman_file:
            num = line[:line.find(' = ')]
            friedmans.add(num)

    calculated_friedmans = set()
    with open('nice_friedman_numbers.txt', 'r') as calculated_friedman_file:
        for line in calculated_friedman_file:
            num = line[:line.find(' = ')]
            calculated_friedmans.add(num)

    new_friedmans = calculated_friedmans - friedmans
    if new_friedmans:
        for new_friedman in new_friedmans:
            print(f'New nice friedman number: {new_friedman}')
    else:
        print('No new friedmans')


if __name__ == '__main__':
    # new_nice_friedman_check()
    known_nice_friedman_check()
