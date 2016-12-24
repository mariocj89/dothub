from . import _main


def main():
    conf = _main.load_config()
    _main.dothub(obj={}, default_map=conf)

if __name__ == '__main__':  # pragma: no cover
    exit(main())
