[![Build Status](https://travis-ci.org/Mariocj89/dothub.svg?branch=master)](https://travis-ci.org/Mariocj89/dothub)
[![PyPI Version](https://img.shields.io/pypi/v/dothub.svg)](https://pypi.python.org/pypi/dothub/)

# dothub

Stop managing your github configuration through an UI like a mere human
and do everything through beautiful config YAML files.

dothub allows you to declare your configuration in a config file and update it by
just updating the file. This way you can configure your labels, collaborators,
default repo and organization parameters and other as code and have them version controlled.

If you are not sure how to configure something through the config file just change it in
the UI and sync it locally with your file, you will see the changes! Next time you
wont need to do any clicks!

# Install

```pip install dothub```

# Usage

The first time you run dothub it will run a wizard to help you configure your credentials.

## Repository configuration

#### Retrieve locally:

```bash
$ dothub repo pull
.dothub.repo.yml updated
```

This creates a file that represents your repo configuration

#### Updating from local changes:


```bash
dothub repo push
Changes:
+ root['collaborators']['dnaranjo89']
+ root['labels']['new-tag']
C root['hooks']['travis']['active'] (True -> False)
Apply changes? [Y/n]: Y
Updated!
```

You can check the repo configuration in github. dnarnaj89 has been invited as a collaborator,
travis hooks have been disabled and you have a new awesome "new-tag"

## Organization Configuration

#### Retrieve locally:

```dothub org pull```


#### Updating from local changes:

```dothub repo push```

#### Updating all repositories within an organization

You can update all the repositories of an organization from your .dothub.repo.yml file.

You can just do ```dothub repo pull``` from a repo with the default configuration and then
```dothub org repos``` to configure all the repositories. Note that some repository
specific options like the name or the description will be ignored on the update.

## Targeting a different repo from the current workspace

By default dothub will assume you want to work with the repo that your workspace is in
or the organization of repo for the current tracking branch in case of organization
commands but this can be overriden through some parameters.

```dothub repo --organization=org_name --repository=repo_name pull```

```dothub org --name=org_name pull```

```dothub repo --organization=org_name --repository=repo_name push```

```dothub org --name=org_name push```

# Future features

This is justa prototype, dothub aims to be the configuration tool for your whole github
see [here](https://github.com/Mariocj89/dothub/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
for the features that are going to come available soon.
