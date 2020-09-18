from argparse import ArgumentParser
from multiprocessing import Process
from os.path import dirname, join
from flytrack.config import Config
from flytrack.client.main import main as client_main
from flytrack.server.main import main as server_main


def main(argv=None):
    argp = ArgumentParser()
    argp.add_argument(
            '--video',
            required=True)
    argp.add_argument(
            '--config',
            default=None)

    args = argp.parse_args(argv)

    # Load the config
    path = args.config or join(dirname(__file__), 'config.yml')
    Config.Load(path)

    #
    server_handle = Process(target=server_main)
    server_handle.daemon = True
    server_handle.start()
    client_main(args.video)

    # Close down the server.

if __name__ == '__main__':
    main()
