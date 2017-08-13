import re


class MultipleKeyError(KeyError):
    """The item matched multiple keys"""


class RegExDict(dict):
    """A dict that items are regex and keys are matched against them

    :Example:

     >>> x = RegExDict({"I .+ coke": 5})
     >>> assert x["I love coke"] == 5
    """
    def __getitem__(self, item):
        keys = [key for key in self.keys() if re.match(key, item)]
        if not keys:
            raise KeyError(item)
        elif len(keys) > 1:
            raise MultipleKeyError(item)
        else:
            return super(RegExDict, self).__getitem__(keys[0])

    def get(self, item, default=None):
        try:
            return self.__getitem__(item)
        except KeyError:
            return default

