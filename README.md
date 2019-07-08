# iterator_threads

iter_threads is a small class that subclasses threading. 
Thread and can wrap an iterator outsourcing the next(iterator) operation to a worker thread with output being pushed into a queue. 
The iterator returns objects in the same order as the original synchronous iterator.

Supports queue size (so you can buffer a fixed number of objects)
Supports iterator interface (so minimally you can simply pass your regular iterator object to the class)
Supports with statemetn (to start/stop worker thread)


## Example usage methods defined in iter_thread.py:
    simple_example_context_manager()
    simple_example_basic()
    max_queue_example()
    

## iter_thread
    Inputs into init:
        iter_in     :  iterator to be outsourced to a worker thread. 
                       iterator output will be store in a fifo queue
        get_timeout :  timeout for getting item out of queue
        qsize       :  maximum number of items in queue
        put_timeout :  timeout for putting things into queue 
                       (comes into play for finite qsize)
        
        name, daemon, group : arguments passed to threading.Thread.__init__()
            
    Methods:
        start()     :  from threading.Thread, will start the worker thread
        stop()      :  tried to terminate worker thread and empty queue
    
    Interfaces supported:
        iterator    :  iterator interface, will return item in same sequence
                       as was passed to it via iter_in
        with        :  using with will start()/stop() using context manager

