##
# Example usage methods defined at the end:
#     simple_example_context_manager()
#     simple_example_basic()
#     max_queue_example()
    

# iter_thread
#     Inputs into init:
#         iter_in     :  iterator to be outsourced to a worker thread. 
#                        iterator output will be store in a fifo queue
#         get_timeout :  timeout for getting item out of queue
#         qsize       :  maximum number of items in queue
#         put_timeout :  timeout for putting things into queue 
#                        (comes into play for finite qsize)
        
#         name, daemon, group : arguments passed to threading.Thread.__init__()
            
#     Methods:
#         start()     :  from threading.Thread, will start the worker thread
#         stop()      :  tried to terminate worker thread and empty queue
    
#     Interfaces supported:
#         iterator    :  iterator interface, will return item in same sequence
#                        as was passed to it via iter_in
#         with        :  using with will start()/stop() using context manager
        

import threading
import queue

#iterator that outsources computation to a worker thread
class iter_thread(threading.Thread):
    
    def __init__(self,
                 #iterator to be executed inside a thread 
                 iter_in, 
                 
                 #queue properties           
                 get_timeout = None,
                 
                 #how many objects to buffer in the fifo queue
                 qsize = 0,
                 
                 #might be better to set None if qsize isn't none
                 put_timeout = None,
                 
                 #options passed to threading.Thread init
                 name=None,daemon=None, group=None):
        
        #init Thread
        super().__init__(group=group, 
                         name=name,
                         daemon=daemon)
        
        #get pointer to iterator
        self._iter_in = iter_in 
        
        self.put_timeout = put_timeout
        self.get_timeout = get_timeout
        
        #setup fifo queue
        self.out = queue.Queue(qsize)
        
        
        #setup early termination
        self.early_term = False
        
        #setup thread exception, iterator will 
        #reraise this error if thread is dead
        self.thread_exception = None
        
        #set target
        self._target = self._run
        
        #termination object
        self.termination_object = '__iter_thread__queue__end__'
        
        
        return
    
    #define iterator interface members
    def __iter__(self):
        return self
    
    def __next__(self):
        
        #thread is dead (queue might not be empty though!)
        if not self.is_alive():
            #check if an exception occured in the worker, reraise it
            if self.thread_exception is not None:
                raise self.thread_exception
            #check if queue is empty, this shouldn't happen
            elif self.out.empty():
                raise ValueError("Thread is not alive and queue is empty!")
            
        obj = self.out.get(timeout = self.get_timeout)
        self.out.task_done()
        
        #check for iteration termination 
        if isinstance(obj,type(self.termination_object)) \
           and obj==self.termination_object:
            raise StopIteration 
                  
        #return object
        return obj
    
    def _run(self):
        
        try:        

            #iterate over iterator
            for obj in self._iter_in:

                #check termination flag (read only)
                if self.early_term:
                    break
                
                #batch done, push into queue
                self.out.put(obj, timeout = self.put_timeout)

            #put a termination object in the queue then return
            self.out.put(self.termination_object, timeout = self.put_timeout)
        
        #wraps everything to record to self.thread_exception (only writer)
        except Exception as e:
            self.thread_exception = e
            
        #thread end
        return
    
    #optional stop method, sets early termination to be true
    #once therad is dead, empties the queue
    def stop(self):
        
        #orderly temrinate + join the thread
        self.early_term = True
        self.join(timeout = self.get_timeout)
        
        #empty the queue
        while not self.out.empty():
            self.out.get(timeout = self.get_timeout)
            self.out.task_done()
        
        return
    
    #context manager for the iterator
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return
    
    
#example of taking a regular iterator and outsourcing it to a thread
#uses context manager
def simple_example_context_manager():
    normal_iterator = range(10)
    with iter_thread(normal_iterator) as it:
        for obj in it:
            print(obj)

    return

#example of taking a regular iterator and outsourcing it to a thread
def simple_example_basic():
    normal_iterator = range(10)
    it = iter_thread(normal_iterator)
    it.start()
    for obj in it:
        print(obj)
    it.stop()
    return


#example of taking a regular iterator and outsourcing it to a thread
#uses context manager
def max_queue_example():
    import time
    normal_iterator = range(20)
    with iter_thread(normal_iterator,qsize=10) as it:
        for obj in it:
            time.sleep(1)
            print('Current object: %d, number of objects in queue: %d, is thread alive: %r'%
                  (obj,it.out.qsize(),it.is_alive()))

    return
            
