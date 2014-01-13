import unittest
from testfixtures import compare
from testfixtures import replace
import zmq
import threading
import time
import socket
import random
from slidelint_site.queue_manager import JobsManager


def add_new_jobs(jobs_manager, jobs_num=4):
    results = []
    for i in range(jobs_num):
        results.append(
            jobs_manager.add_new_job("file_%s" % i, 'rule_%s' % i))
        time.sleep(0.01)  # queue is tricky(buggy?)
    status_codes = [result.get('status_code') for result in results]
    msgs = [result.get('msg', None) for result in results]
    errors = [result.get('error', None) for result in results]
    return status_codes, msgs, errors


def get_free_port():
    """ returns unused port number"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.bind(('', 0))
    sock.listen(socket.SOMAXCONN)
    _, port = sock.getsockname()
    sock.close()
    return str(port)


class JobsManagerTests(unittest.TestCase):

    def setUp(self):
        self.producer_chanel = "tcp://127.0.0.1:%s" % get_free_port()
        self.collector_chanel = "tcp://127.0.0.1:%s" % get_free_port()

    def worker(self, id):
        context = zmq.Context()
        # receive work
        consumer_receiver = context.socket(zmq.PULL)
        consumer_receiver.connect(self.producer_chanel)
        # send work
        consumer_sender = context.socket(zmq.PUSH)
        consumer_sender.connect(self.collector_chanel)
        while True:
            work = consumer_receiver.recv_json()
            result = {'worker_id': id}
            result.update(work)
            time.sleep(random.randint(1, 20)/200.0)
            consumer_sender.send_json(result)

    def start_workers(self, num=10):
        workers = [threading.Thread(target=self.worker,
                                    args=(i,), daemon=True)
                   for i in range(num)]
        [worker.start() for worker in workers]

    @replace('slidelint_site.queue_manager.save_file', lambda *x: x[0])
    def test_jobs_manager_queue_size_limit(self):
        jobs_manager = JobsManager(
            self.producer_chanel, self.collector_chanel, None, queue_size=1)
        status_codes, msgs, errors = add_new_jobs(jobs_manager)
        compare(status_codes, [200, 200, 423, 423])
        compare(msgs, ['Job was added to the jobs queue',
                       'Job was added to the jobs queue',
                       None,
                       None])
        compare(errors, [None,
                         None,
                         'The queue is full now, try later',
                         'The queue is full now, try later'])

    @replace('slidelint_site.queue_manager.save_file', lambda *x: x[0])
    def test_workers(self):
        jobs_manager = JobsManager(
            self.producer_chanel, self.collector_chanel, None, queue_size=10)
        self.start_workers(3)
        status_codes, msgs, errors = add_new_jobs(jobs_manager, 10)
        compare(status_codes, [200] * 10)  # all jobs putted to queue
        time.sleep(0.2)  # time to done all jobs(each worker use random time)
        values = jobs_manager.results.values()
        compare(len(values), 10)
        self.assertNotEqual(
            values,
            sorted(values, key=lambda x: x['worker_id']))
