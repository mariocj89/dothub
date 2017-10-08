# Overview

`dothub` welcomes contribution, specially if they address any of the existing [issues](https://github.com/mariocj89/dothub/issues) or are "generic" improvements like [code coverage](https://coveralls.io/github/mariocj89/dothub), documentation or [style issues](https://landscape.io/github/mariocj89/dothub/master).

For any bug report or question, please use [the issue tracker](https://github.com/mariocj89/dothub/issues).

# What should I work on?

If it is your first contribution to an opensource project you are encouraged to take the simplest change possible. From fixing a typo, raising the coverage, improve documentaion or any other trivialtask you might spot. This helps you set up the environment and get ready for the "real stuff".

If you feel curage enough, check the [github issues open for collaborators](https://github.com/mariocj89/dothub/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22).

Feeling totally bored and hopeless in life? If you have sent a couple of Pull Request and want to get deeper in the project just send a mail.

# Validating your changes

Be sure to include tests that verify the change. All tests should have an human redable docstring that explains what is being tested or validate. Please, no tests just to raise the coverage.

If the change is implementing a new feature be sure to have some integration tests covering it as well.

The code has two kind of test levels:

- [unit](https://github.com/mariocj89/dothub/tree/master/tests/unit): *Quick* to write, validate "happy paths" and corner cases of each piece of code. One suite of tests per Python module. These suites make assumptions about the HTTP responses are.
- [end to end](https://github.com/mariocj89/dothub/tree/master/tests/end_to_end): Tests against the real github with a fake organization.

If any check in the Pull Request fails, the chances of your pull request getting merged are really low.

# TL;DR;

Contributions are welcomed. Just follow the same style and common sense

## Running tests
```bash
make test
```

## Publishing a new version
```bash
make release
```

