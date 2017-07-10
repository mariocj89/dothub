|Build Status| |PyPI Version| |Code Health|

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

    $ dothub repo pull
    .dothub.repo.yml updated

This creates a file that represents your repo configuration

Updating from local changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    dothub repo push
    Changes:
    + root['collaborators']['dnaranjo89']
    + root['labels']['new-tag']
    C root['hooks']['travis']['active'] (True -> False)
    Apply changes? [Y/n]: Y
    Updated!

You can check the repo configuration in github. dnarnaj89 has been
invited as a collaborator, travis hooks have been disabled and you have
a new awesome "new-tag"

Organization Configuration
--------------------------

Retrieve locally:
^^^^^^^^^^^^^^^^^

``dothub org pull``

Updating from local changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``dothub repo push``

Updating all repositories within an organization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can update all the repositories of an organization from your
.dothub.repo.yml file.

You can just do ``dothub repo pull --output_file=.dothub.org.repos.yml``
from a repo with the default configuration and then ``dothub org repos``
to configure all the repositories. Note that some repository specific
options like the name or the description will be ignored on the update.

Targeting a different repo from the current workspace
-----------------------------------------------------

By default dothub will assume you want to work with the repo that your
workspace is in or the organization of repo for the current tracking
branch in case of organization commands but this can be overriden
through some parameters.

``dothub repo --owner=org_name --repository=repo_name pull``

``dothub org --name=org_name pull``

``dothub repo --owner=org_name --repository=repo_name push``

``dothub org --name=org_name push``

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
