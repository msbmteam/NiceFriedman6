import timeit

import pandas


def get_big_expr():
    exprs = []
    with open('exprs.txt', 'r') as expr_file:
        for line in expr_file:
            exprs.append(f"({line.strip().replace(' ', '').replace('.', '')})")
    with open('exprs_out.txt', 'w') as out_file:
        out_file.write(' * '.join(exprs))

if __name__ == '__main__':
    with open('exprs.txt', 'r') as expr_file:
        for line in expr_file:
            line = line.strip()
            try:
                eval(line)
            except (OverflowError, ZeroDivisionError):
                pass
