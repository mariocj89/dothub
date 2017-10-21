|Build Status| |PyPI Version| |Code Health| |Coveralls Report|

dothub
======

Stop managing your github configuration through an UI like a mere human
and do everything through beautiful config YAML files.

dothub allows you to declare your configuration in a config file and
update it by just updating the file. This way you can configure your
labels, collaborators, default repo and organization parameters and
other as code and have them version controlled.

If you are not sure how to configure something through the config file
just change it in the UI and sync it locally with your file, you will
see the changes! Next time you wont need to do any clicks!

Install
=======

``pip install dothub``

Usage
=====

The first time you run dothub it will run a wizard to help you configure
your credentials.

Repository configuration
------------------------

Retrieve locally:
^^^^^^^^^^^^^^^^^

.. code:: bash

    $ dothub pull mariocj89/dothub
    .dothub.repo.yml updated

This creates a file that represents your repo configuration

Updating from local changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    dothub push mariocj89/dothub
    Changes:
    + root['collaborators']['dnaranjo89']
    + root['labels']['new-tag']
    C root['hooks']['travis']['active'] (True -> False)
    Apply changes? [Y/n]: Y
    Updated!

You can check the repo configuration in github. dnarnajo89 has been
invited as a collaborator, travis hooks have been disabled and you have
a new awesome "new-tag"

Organization Configuration
--------------------------

Retrieve locally:
^^^^^^^^^^^^^^^^^

``dothub pull <org_name>``

Updating from local changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``dothub push <org_name>``

Updating all repositories within an organization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can update all the repositories of an organization from your
.dothub.repo.yml file.

To make a repo configuration be a template for all the repositories
of your org you can use dothub as follows:

.. code:: bash

    dothub pull <org/repo> .dothub.org.repos.yml
    dothub push --bulk org/*

Note that some repository specific options like the name or the
description will be ignored on the update.


Future features
===============

This is justa prototype, dothub aims to be the configuration tool for
your whole github see
`here <https://github.com/mariocj89/dothub/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement>`__
for the features that are going to come available soon.

FAQ
===

How can I retriger the reconfigure step?
----------------------------------------

Just run dothub configure

How can I use the tool if I am need to provide a custom SSL certificate?
------------------------------------------------------------------------

Pass the envvar REQUESTS\_CA\_BUNDLE=YOURCERTPATH.cer before running
dothub

I don't want the tool to manage a part of the config
----------------------------------------------------

Just remove that part! If there is full section missing (hooks, options,
members, etc.). It will be ignored

.. |Build Status| image:: https://travis-ci.org/mariocj89/dothub.svg?branch=master
   :target: https://travis-ci.org/mariocj89/dothub
.. |PyPI Version| image:: https://img.shields.io/pypi/v/dothub.svg
   :target: https://pypi.python.org/pypi/dothub/
.. |Code Health| image:: https://landscape.io/github/mariocj89/dothub/master/landscape.svg?style=flat
   :target: https://landscape.io/github/mariocj89/dothub/master
.. |Coveralls Report| image:: https://coveralls.io/repos/github/mariocj89/dothub/badge.svg
   :target: https://coveralls.io/github/mariocj89/dothub

