import cPickle
import os
import random
import string

def str_to_bool(input_str):
    return str(input_str).lower() in ['true', 't', 'yes', 'y', '1']

def create_random_string(length=8):
    char_set = string.ascii_uppercase + string.digits
    return ''.join(random.choice(char_set) for _ in range(length))

def chunk_list(orig_list, chunk_size):
    """
    Source: http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python

    Yield successive n-sized chunks (chunk_size) from orig_list.
    """
    for i in xrange(0, len(orig_list), chunk_size):
        yield orig_list[i:i+chunk_size]

def fork(function, *args, **kwargs):
    """
    Convenience function to wrap forking calls.  It will fork and call a 
    function with the arguments specified.

    Example:

    def add(i, j): return i+j
        d = fork_in_bg(add, i, j)

    @type function: function_pointer
    @param function: The function which will be executed after the fork

    @type *args: list
    @param *args: the argument list to pass to the function

    @type **kwargs: dict
    @param **kwargs: the named argument dict to pass to the function

    @return: dict with {'r': fd, 'pid': pid} where fd is the stdout from a pipe.
    """

    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(r)
        try:
            out = function(*args, **kwargs)
            os.write(w, cPickle.dumps(out))
        finally:
            os.close(w)
            os._exit(0)
    else:
        os.close(w)

    return {'r': r, 'pid': pid}
