"""
The workers module. Here is all staff related to worker, including sand-boxing,
slidelint checking and results storing.
"""
import base64
import subprocess
import operator
import os
import json
import itertools
import shutil
import zmq

import logging
logging.basicConfig(level=logging.DEBUG)

HERE = os.path.dirname(os.path.abspath(__file__))


class SlidelintExeption(Exception):
    """
    Maker for SlideLint errors
    """
    pass


def remove_parrent_folder(file_path):
    """
    Cleanup function for worker - removes presentation parent folder.
    All data of new job are stored into directory (images, results, ...)
    so to cleanup we need to remove presentation parent directory.
    """
    parrent = file_path.rsplit(os.path.sep, 1)[0]
    shutil.rmtree(parrent)


def file_to_base64(path):
    """
    Read file data, encode it into base64. Return utf-8 string of base64
    encode data
    """
    return base64.b64encode(open(path, 'rb').read()).decode("utf-8")


def get_pdf_file_preview(path, size='300', timeout=600):
    """ Creates pdf file preview - small images of pdf file pages.
        For transformation pdf to bunch if images it uses pdftocairo, and
        store transformation results near the target pdf file.
        It returns:

    ::

        {'Slide N': base64_encoded_data, ...}

    """
    # making base name for preview images
    dist = path.rsplit(os.path.sep, 1)[0]
    images_base_name = os.path.join(dist, 'preview-page')

    # transforming pdf file in preview images
    cmd = ['pdftocairo', path, images_base_name, '-jpeg', '-scale-to', size]
    retcode = subprocess.call(cmd, timeout=timeout)
    if retcode != 0:
        raise IOError("Can't create presentation preview")

    # collecting pages previews and decode its data into base64
    files = [i for i in os.listdir(dist) if i.startswith('preview-page')]
    files.sort()
    images = {'Slide %s' % (i+1): file_to_base64(os.path.join(dist, n))
              for i, n in enumerate(files)}
    # IDEA: do I need to add here images removing, or just left if for
    # global garbage collector?
    return images


def peform_slides_linting(presentation_path, config_path=None,
                          slidelint='slidelint', timeout=1200):
    """
    function takes:
        * location to pdf file to check with slidelint
        * path to config file fro
        * path to slidelint executable
        * timeout for checking procedure

    function constructs command to lint presentation, executes it, and prepares
    results by grouping it by page:

    ::

         [{'page': page,
           'results': {"msg_name": ,
                       "msg": "",
                       "help": "",
                       "page":"Slide N",
                       "id":""}
            }, ...
         ]

    """
    logging.debug("run slidelint check")
    results_path = presentation_path + '.res'  # where to store check results

    # making command to execute
    cmd = [slidelint, '-f', 'json', '--files-output=%s' % results_path]
    if config_path:
        cmd.append('--config=%s' % config_path)
    cmd.append(presentation_path)

    # running slidelint checking against presentation
    retcode = subprocess.call(cmd, timeout=timeout)
    if retcode != 0:
        # we won't keep silence about errors
        raise SlidelintExeption('ups, "%s" return %s code' % (cmd, retcode))

    # getting checking result and grouping them by pages
    results = json.load(open(results_path, 'r'))
    results.sort(key=operator.itemgetter('page'))
    grouped_by_page = itertools.groupby(
        results, key=operator.itemgetter('page'))
    grouped_by_page = [{'page': page, 'results': list(result)}
                       for page, result in grouped_by_page]
    grouped_by_page.sort(key=operator.itemgetter('page'))

    return grouped_by_page


def worker(producer_chanel, collector_chanel, slidelint_path):
    """
    receives jobs and perform slides linting
    """
    context = zmq.Context()
    # recieve work
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect(producer_chanel)
    # send work
    consumer_sender = context.socket(zmq.PUSH)
    consumer_sender.connect(collector_chanel)
    logging.info("Worker is started on '%s' for receiving jobs"
                 "and on '%s' to send results",
                 producer_chanel, collector_chanel)
    slidelint_config_files_mapping = {
        'simple': os.path.join(HERE, 'slidelint_config_files', 'simple.cfg'),
        'strict': os.path.join(HERE, 'slidelint_config_files', 'strict.cfg')}
    while True:
        job = consumer_receiver.recv_json()
        logging.debug("new job with uid '%s'" % job['uid'])
        result = {'uid': job['uid']}
        try:
            config_file = slidelint_config_files_mapping.get(
                job['checking_rule'], None)
            slidelint_output = peform_slides_linting(
                job['file_path'], config_file, slidelint_path)
            icons = get_pdf_file_preview(job['file_path'])
            result['result'] = slidelint_output
            result['icons'] = icons
            result['status_code'] = 200
            logging.debug("successfully checked uid '%s'" % job['uid'])
        except SlidelintExeption:
            logging.error(
                "slidelint died while working with uid '%s'" % job['uid'])
            result['status_code'] = 500
            result['result'] = 'slidelint was not able to check presentation'
        except Exception as exp:
            logging.error(
                "something went wrong with uid '%s' - '%s'", job['uid'], exp)
            result['status_code'] = 500
            result['result'] = "ups something went wrong"
        finally:
            consumer_sender.send_json(result)
            logging.debug("cleanup for job with uid '%s'" % job['uid'])
            remove_parrent_folder(job['file_path'])


def worker_cli():
    """
    Worker for slidelint site

    Usage:
      slidelint_worker PRODUCER COLLECTOR [options]
      slidelint_worker -h | --help

    Arguments:
      PRODUCER    zmq allowed address for jobs producer
      COLLECTOR   zmq allowed address for results collector

    Options:
      -h --help     Show this screen.
      --slidelint=<slidelint> -s <slidelint>   Path to slidelint executable
                                               [default: slidelint]
    """
    from docopt import docopt
    args = docopt(worker_cli.__doc__)
    worker(args['PRODUCER'], args['COLLECTOR'], args['--slidelint'])
