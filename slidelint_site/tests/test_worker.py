import unittest
from testfixtures import compare, Replacer
import zmq
import threading
import time
import random


def worker(producer_chanel, collector_chanel):
    context = zmq.Context()
    # recieve work
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect(producer_chanel)
    # send work
    consumer_sender = context.socket(zmq.PUSH)
    consumer_sender.connect(collector_chanel)
    while True:
        work = consumer_receiver.recv_json()
        result = {'uid': work, 'worker_id': id}
        time.sleep(random.randint(1, 20)/1000.0)
        consumer_sender.send_json(result)


class WorkerTests(unittest.TestCase):

    messages = []
    producer_chanel = "tcp://127.0.0.1:5558"
    collector_chanel = "tcp://127.0.0.1:5559"

    def setUp1(self):
        self.receiver_instance = threading.Thread(
            target=self.receiver, daemon=True)
        self.receiver_instance.start()
        self.producer_instance = threading.Thread(
            target=self.producer, daemon=True)
        self.producer_instance.start()

    def producer(self):
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.connect(self.producer_chanel)
        for i in range(10):
            zmq_socket.send_json({'path': i, 'rule': i})

    def receiver(self):
        context = zmq.Context()
        consumer_receiver = context.socket(zmq.PULL)
        consumer_receiver.connect(self.collector_chanel)
        while True:
            data = consumer_receiver.recv_json()
            print(data)
            self.messages.append(data)

    def test_worker(self):
        # from slidelint_site.worker import worker
        with Replacer() as r:
            r.replace('slidelint_site.worker.peform_slides_linting', lambda x: x)
            r.replace('slidelint_site.worker.get_pdf_file_preview', lambda x: x)
            worker_instance = threading.Thread(
                target=worker,
                args=(self.producer_chanel, self.collector_chanel),
                daemon=True)
            worker_instance.start()
            self.setUp1()
            time.sleep(0.3)
        compare(self.messages, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
