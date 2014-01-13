"""
zmq based producer and results collector jobs queuing manager
"""
import threading
import queue
import uuid
import zmq
from .utils import save_file

import logging
LOGGER = logging.getLogger(__name__)

QUEUE_IS_FULL_MESSAGE = {'error': 'The queue is full now, try later',
                         'status_code': 423}


class JobsManager(threading.Thread):
    """
    add new jobs to queue, also push jobs from queue to the workers
    and collect results
    it takes:
        * producer_addr, collector_addr - zmq addresses for producer and
                                          collector
        * work_dir - base to save posted files data
        * queue_size - size of queue
    """
    def __init__(self, producer_addr, collector_addr, work_dir, queue_size=5):
        super(JobsManager, self).__init__(daemon=True)
        self.work_dir = work_dir

        self.queue = queue.Queue(maxsize=queue_size)
        self.results = {}

        # initializing zmq
        self.context = zmq.Context()

        # creating zmq based results receiver
        self.results_receiver = self.context.socket(zmq.PULL)
        self.results_receiver.bind(collector_addr)
        LOGGER.info("Started results receiver on %s", collector_addr)

        # creating zmq based jobs producer
        self.jobs_producer = self.context.socket(zmq.PUSH)
        self.jobs_producer.bind(producer_addr)
        LOGGER.info("Started jobs sender on %s", producer_addr)

        # making sender jobs sender work as a daemon thread
        self.sender = threading.Thread(target=self._jobs_sender, daemon=True)
        self.sender.start()

        # starting itself
        self.start()

    def _jobs_sender(self):
        """
        Takes jobs from queue and pushes them to workers
        """
        while True:
            # this cycle should work at any circumstances
            try:
                job = self.queue.get()
                self.jobs_producer.send_json(job)
                LOGGER.debug("Job '%s' was sent to worker", job['uid'])
            except Exception as exp:  # pylint: disable=W0703
                LOGGER.error("Got exception while pushing new job to "
                             " the worker: '%s'", exp)

    def add_new_job(self, file_object, checking_rule):
        """
        Add new job to queue. Takes file like object and checking rule.
        In case if job was added returns:
           {'msg': 'Job was added to the jobs queue',
            'uid': uid,
            'status_code': 200}
        In case if queue is full returns:
           {'error': 'The queue is full now, try later',
            'status_code': 423}
        """
        if self.queue.full():
            LOGGER.debug('queue is full, first')
            return QUEUE_IS_FULL_MESSAGE
        uid = uuid.uuid4().hex
        # IDEA: moving file uploading process to the worker side
        # would guaranty that "queue.Full" don't appear after comping file
        # uploading
        file_path = save_file(file_object, uid, self.work_dir)
        try:
            self.queue.put_nowait(
                {"file_path": file_path,
                 "checking_rule": checking_rule,
                 "uid": uid})
            LOGGER.debug('added to queue')
        except queue.Full:
            LOGGER.debug('queue is full, second')
            return QUEUE_IS_FULL_MESSAGE
        return {'msg': 'Job was added to the jobs queue',
                'uid': uid,
                'status_code': 200}

    def run(self):
        """
        Receives results from workers and add them to results dictionary.
        The key is job uid.
        """
        while True:
            # this cycle should work at any circumstances
            try:
                result = self.results_receiver.recv_json()
                LOGGER.debug("result received: '%s'", result['uid'])
                self.results[result['uid']] = result
            except Exception as exp:  # pylint: disable=W0703
                LOGGER.error("Got exception while receiving message from"
                             " worker: '%s'", exp)
