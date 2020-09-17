from argparse import ArgumentParser
from multiprocessing import Process
from flytrack.client.main import main as client_main
from flytrack.server.main import main as server_main


def main(argv=None):
    argp = ArgumentParser()
    argp.add_argument(
            '--video',
            required=True)
    argp.add_argument(
            '--port',
            type=int,
            default=8003)
    argp.add_argument(
            '--cache-dir',
            default='/tmp')
    argp.add_argument(
            '--model-url',
            default=None)

    args = argp.parse_args(argv)

    server_handle = Process(target=server_main,
                            args=(args.port, args.cache_dir))
    server_handle.daemon = True
    server_handle.start()
    client_main(args.video, args.port)

    # Close down the server.

if __name__ == '__main__':
    main()
