from . import config, cli


def main():
    conf = config.load_config()
    cli.dothub(obj={}, default_map=conf)

if __name__ == '__main__':  # pragma: no cover
    exit(main())
