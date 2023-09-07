from nice_friedman_solver import *

if __name__ == '__main__':
    try:
        logger.info('Starting...')
        main(profiling=False)
        # solve_nice_friedman_multicore(117662 , profiling=False)
    except Exception:
        logger.error('Exiting...')
