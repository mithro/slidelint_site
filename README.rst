**************
Slidelint site
**************

Slidelint site allows users to check theirs presentation with
slidelint(https://github.com/enkidulan/slidelint) through web
interface on-line.


This package contain buildout and sources for slidelint site.

*****************
Package structure
*****************

This package are separated on three parts: users frontend,
server backend with jobs queue and workers that perform presentations
linting with slidelint.


front-end
=========

Allows users to upload presentations files; shows uploading process and
waiting message; shows users check results.

The files related to front-end:
    * slidelint_site/templates/index.pt - main page that loads angular app
    * slidelint_site/static - static resources(images, css, js, ...)
    * slidelint_site/static/js/app.js - angular application that
        implements front-end behavior
    * slidelint_site/static/templates/waiting.html - template for modal
        dialog that shows uploading progress and waiting message



*******************
System requirements
*******************

make sure that following packages are installed on your system:
    * python3-devel
    * libevent-devel
    * zeromq3-devel

or install them with command(for ubuntu):
    ::

        # apt-get install python3-dev libevent-dev zeromq3-dev




*****
Tests
*****

To run backend python test use execute nosetest from bin directory.
