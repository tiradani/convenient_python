

def chunk_list(orig_list, chunk_size):
    """ 
    Source: http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python

    Yield successive n-sized chunks (chunk_size) from orig_list.
    """
    for i in xrange(0, len(orig_list), chunk_size):
        yield orig_list[i:i+chunk_size]
