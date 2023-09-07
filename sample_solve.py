from nice_friedman_solver import *

if __name__ == '__main__':
    try:
        logger.info('Starting...')
        # main(profiling=False)
        solve_nice_friedman_multicore(156253, profiling=False)
    except Exception as e:
        raise e
