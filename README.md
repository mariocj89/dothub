[![Build Status](https://travis-ci.org/Mariocj89/dothub.svg?branch=master)](https://travis-ci.org/Mariocj89/dothub)
[![PyPI Version](https://img.shields.io/pypi/v/dothub.svg)](https://pypi.python.org/pypi/dothub/)

# dothub

Stop managing your github configuration through an UI like a mere human
and do everything through beautiful config YAML files.

dothub allows you to declare your configuration in a config file and update it by
just updating the file. This allows you to configure your labels, collaborators,
default repo parameters and other as code and have it version controlled.

# Install

```pip install dothub```

# Usage

The first time you run dothub it will run a wizard to help you configure your credentials.

From now on you can pull the config with:

```dothub repo --organization=org_name --repository=repo_name pull```

```dothub org --name=org_name pull```

And update your configuration from the localfile with

```dothub repo --organization=org_name --repository=repo_name push```

```dothub org --name=org_name push```

If you don't provide owner/organization and repo name it asumes you want it to work with the tracking branch of the current repository.

# Future features

This is justa prototype, dothub aims to be the configuration tool for your whole github
see [here](https://github.com/Mariocj89/dothub/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
for the features that are going to come available soon.
