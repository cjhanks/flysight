from argparse import ArgumentParser
from multiprocessing import Process
from os.path import dirname, join
from flysight.config import Config
from flysight.client.main import main as client_main
from flysight.server.main import main as server_main


def main(argv=None):
    # Configuration parsing.
    argp = ArgumentParser()
    argp.add_argument(
            '--video',
            required=False)
    argp.add_argument(
            '--config',
            default=None)

    args = argp.parse_args(argv)

    # Load the config
    path = args.config or join(dirname(__file__), 'config.yml')
    Config.Load(path)

    # Initialize the server in a separate process, we set the `daemon` parameter
    # since it makes it life easier on shutdown.
    server_handle = Process(target=server_main)
    server_handle.daemon = True
    server_handle.start()

    # Start the client GUI.
    client_main(args.video)

if __name__ == '__main__':
    main()
