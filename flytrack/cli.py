from argparse import ArgumentParser
import cv2
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patch
from flytrack.client import Client



def main(argv=None):
    argp = ArgumentParser()
    argp.add_argument(
            '--uri',
            default='tcp://127.0.0.1:8003')
    argp.add_argument(
            '--video',
            required=True)
    argp.add_argument(
            '--return-peaks',
            default=False,
            action='store_true')

    args = argp.parse_args(argv)

    # - Initialize socket
    client = Client(args.uri)

    # - Initialize video reader
    reader = cv2.VideoCapture(args.video)

    # {
    plt.ion()
    fig = plt.figure()
    ax  = fig.add_subplot(111)

    while True:
        status, img = reader.read()
        if not status:
            break

        # Make it single channel.
        img = img[:, :, 0]

        # Construct a request.
        (image, peaks) = client.detect(img)

        if image is not None:
            ax.imshow(image)

        for peak in peaks:
            circle = patch.Circle((peak[0] * image.shape[0],
                                   peak[1] * image.shape[1]),
                                   .2,
                                   color='blue')
            ax.add_patch(circle)



        fig.canvas.draw()
        fig.canvas.flush_events()

    # }

if __name__ == '__main__':
    main()
