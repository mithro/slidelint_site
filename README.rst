**************
Slidelint site
**************

Slidelint site allows users to check theirs presentation with
slidelint_ through web interface on-line.

.. _slidelint: https://github.com/enkidulan/slidelint

This package contain buildout and sources for slidelint site.

*****************
How to start site
*****************

Run command:

::

    # bin/circusd circus.ini

*****************
Package structure
*****************


This package are separated on three parts:
    * users front-end
    * server back-end with jobs queue
    * workers that perform presentations linting with slidelint.


Front-end
=========

Allows users to upload presentations files; shows uploading process and
waiting message; shows users check results. Front-end are based on angular_

.. _angular: https://angularjs.org


Files related to front-end:
    * slidelint_site/templates/index.pt - main page that loads angular app
    * slidelint_site/static - static resources(images, css, js, ...)
    * slidelint_site/static/js/app.js - angular application that
        implements front-end behavior
    * slidelint_site/static/templates/waiting.html - template for modal
        dialog that shows uploading progress and waiting message

Workers
=======



Files related to workers:
    * slidelint_site/slidelint_site/worker.py
    * slidelint_site/slidelint_site/utils.py


*******************
System requirements
*******************

Make sure that following packages are installed on your system:
    * python3-devel
    * libevent-devel
    * zeromq3-devel

In ubuntu you can install them with the following command:
    ::

        # apt-get install python3-dev libevent-dev libzmq3-dev



*********************
Errors handling
*********************

In the *var* directory:
    * site_errors.log
    * site.log
    * worker_errors.log
    * workers.log

In case if some sort of error occurred
trace backs of exceptions will be given to a system administrator
 incoming documents which cause issues will be saved to *debug_storage* directory
 for review with details about what happened.
 SMTPHandler
 logging.handlers to notify site administrator about fails


Basically, we have two separated applications - site and slidelint worker, so we
can have different logging handlers for each of them:
* site will send full error trace-back to site administrator
* slidelint worker will save incoming PDF presentation file and send
  to administrator error trace-back with link to presentation.

Person can reports error by provided feedback form.



SMTP logging handler
====================

The message looks like:
2014-02-01 02:44:21,372 - root - ERROR -
    Slidelint process died while trying to check presentation.
    You can access this presentation by link
    http://slidelint.enkidulan.tk/debug/.../presentation.pdf.
    The command: 'slidelint -f json ...' died with the following traceback:

    ::

        Traceback (most recent call last):
        File "slidelint", line 9, in <module>  load_entry_point('slidelint==1.0dev', 'console_scripts', 'slidelint')()
        File "cli.py", line 106, in cli  lint(target_file, config_file, output, enable_disable_ids, msg_info)
        File "cli.py", line 89, in lint  output['files_output'], output['ids'])
        File "outputs.py", line 151, in output_handler  formated_report = formater(rezults)
        File "outputs.py", line 18, in __call__  filtred = [msg for msg in report if msg['id'] not in self.mute_ids]
        File "utils.py", line 88, in __iter__  raise IOError(checker_rez)
        IOError: The function 'wrapped' of 'slidelint.utils' module raised an Exception:
        No /Root object! - Is this really a PDF?

feedback form and view
======================
 I have added feedback form to results page.
 The letters body looks lite that:
 Job id: ddb93ff1750248cdad8292eabd901f3a
 Feedback text:
 some feedback text some feedback text some feedback text some




*******
Linting
*******


Linting process must should include at least three steps:
1. showing visitor a file loading form(also it make sense to check file
2.  type and size on this step)
3. showing awaiting form(and sending file to server, and waiting for results)
4. showing slide linting results
And in case if something goes wrong we should show to user
'try later' message, or something like that




*********************
queuing and worker(s)
*********************

"OMQ" the thing found at http://zeromq.org

Overall, the system works like follows;
    * Website puts something into the queue.
    * Worker gets item from queue and puts results somewhere.
    * Website polls to find out the result.

queue manager
=============

queue manager is here - slidelint_site/queue_manager.py
it's a python queue that use zmq Divide-and-Conquer model http://zguide.zeromq.org/page:all#Divide-and-Conquer to communicate
with its workers.

Right now it uses tcp protocol, so the worker can work separately from the
site, even on other machine.


Worker
======

the code related to worker is here -
slidelint_site/worker.py

worker uses its own configuration file

For our system,

* we want to "throw away" each worker after it has completed a job
* we probably want the possibility of multiple workers running at the same time.

user choose file and fron-end part send it to backend.
Backend downloads this file and add new job to queue.
Free worker takes this job, preform linting and send results to results collector.
Also when job added to queue front-end start asking backend about results and do
 it until receive them.

.. image:: slidelint_site_queue_manager_scheme.jpeg
   :height: 400 px


"throw away" each worker after it has completed a job
=====================================================

added option for worker to preform liting only one time -
https://github.com/enkidulan/slidelint_site/commit/ed554d55b771b04fadcdb1560fb2c738cf189a58
also I using circus for manage workers - http://circus.readthedocs.org/en/latest/
and it allows not only control a number of running processes, but also a lot of
 other things like max_age (https://circus.readthedocs.org/en/0.9.2/configuration/)


we probably want the possibility of multiple workers running at the same time
=============================================================================

It's already done, for now I increased number of same time running
workers(in task ✓ "throw away" each worker after it has completed a job
I make them "die" all the time, so it's a try to balance)
https://github.com/enkidulan/slidelint_sit



**********
Validators
**********

add file size and file type validators to front-end and back-end

dded validators with following commits:
back-end validators:
https://github.com/enkidulan/slidelint_site/commit/9de688d7be51a133043da3a4a370dbd2c871e1c1
front-end validation errors displaing: https://github.com/enkidulan/slidelint_site/commit/3fd468e114660ebb017159d56de38ff8c815ba0c
front-end validators: https://github.com/enkidulan/slidelint_site/commit/77e010cb6a5532f4904c5150e97c2abc4ede9adc… See More
Jan 26 at 1:51pm




**********
Sandboxing
**********

we choose to user docker - https://docker.io/

Done via docker - created docker image slidelint/box where slidelint was installed
 and configuration files was added.
The sandboxed slidelint check look like this:

::

    $ docker run -t -v {presentation_location}:/presentation --networking=false slidelint/box slidelint -f json --files-output=/presentation/{presentation_name}.res /presentation/presentation.pdf

The options description:
    * "-t" - Allocate a pseudo-tty
    * "-v {presentation_location}:/presentation" -
       mounting directory from computer to docker session. All directory content
       will be reachable in "/presentation" directory at docker envirovment.
    * "--networking=false" - disabling network access from running session
    * "slidelint -f json --files-output=/presentation/{presentation_name}.res /presentation/presentation.pdf" - here goes slidelint itself.

Any changes which were made inside session wouldn't be persistent.

*************
Site Settings
*************

You can configure site by editing buildout.cfg. There are actually only two
sections you can be intrested in.

The firs one is mailing configuration:

::

    [mailing_config]
    mailloger_host = localhost
    mailloger_from = notification@example.com
    mailloger_to = manager@example.com
    mailloger_subject = SlideLint: Error has occurred
    # credentials should be written as ", ('name', 'password')"
    mailloger_credentials =
    mail_subject = Slidelint: feedback received
    mail_port = 25

The second is worker config:

::

    [worker_config]
    slidelint = docker run -t -c 4 -v {default_config_path}:/config -v {presentation_location}:/presentation --networking=false slidelint/box slidelint -f json --files-output=/presentation/{presentation_name}.res --config={config_path} /presentation/presentation.pdf
    onetime = true
    debug_url =


