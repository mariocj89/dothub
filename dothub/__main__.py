import logging
from . import config, cli


def main():
    logging.basicConfig(levle=logging.INFO, format="%(message)s")
    conf = config.load_config()
    cli.dothub(obj={}, default_map=conf)

if __name__ == '__main__':  # pragma: no cover
    exit(main())
