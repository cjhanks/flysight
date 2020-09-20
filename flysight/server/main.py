"""
This file is responsible for implementing a server side `main` function.
"""
import numpy as np
import tensorflow as tf
import zmq
from flysight.config import Config
from flysight.message_pb2 import (
        Request,
        RepTracking,
        ReqDetections,
        RepDetections,
        )
from flysight.server.solver import FlyCentroidDetector


def main():
    """
    """
    # Configure a default detector.
    detector = FlyCentroidDetector()

    # Configure the socket responsible for replying.
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REP)
    socket.bind('tcp://*:{}'.format(Config.Instance.networking.port))

    while True:
        message = socket.recv()

        # Try and receive the request.  If the request is malformed, send back
        # an error string.
        try:
            req = Request()
            req.ParseFromString(message)
        except Exception as err:
            print('Error: %s' % err)
            socket.send(b'ERROR: %s' % err)
            continue

        # There are two types of requests within a union; detections, tracking.
        # This handles that switch logic.
        if   req.HasField('detections'):
            rep = handle_detection(req.detections, detector)
        elif req.HasField('tracking'):
            rep = handle_tracking(req.tracking)
        else:
            rep.send(b'ERROR: Incomprehensible request.')
            continue

        # Done.
        socket.send(rep.SerializeToString())


def handle_detection(
        req: ReqDetections, detector: FlyCentroidDetector) -> RepDetections:
    """
    Given an input protobuf detection request; apply the detector, package
    a protobuf response, and return.
    """
    rep = RepDetections()

    # The third dimension here is necessary to support the tensor interface.
    image = np.frombuffer(req.image.data, dtype=np.uint8).reshape(
                            req.image.rows,
                            req.image.cols,
                            1)

    # Always perform the heatmap computation.
    heatmap = detector.generate_heatmap(image, req.upsample_heatmap)

    # Do peak detection.
    if req.return_peaks:
        peaks = detector.find_peaks(heatmap)
        for peak in peaks:
            rpeak = rep.peaks.add()
            rpeak.row = peak[0]
            rpeak.col = peak[1]

    # If the requester wants the heatmap returned, package it.
    if req.return_heatmap:
        hm = tf.squeeze(heatmap)
        rep.heatmap.rows = hm.shape[0]
        rep.heatmap.cols = hm.shape[1]
        rep.heatmap.data = hm.numpy().tobytes()

    return rep

def handle_tracking(req):
    """
    :notimplemented:
    """
    if not req.has_context():
        tracker = FlyCentroidDetector()
    else:
        tracker = FlyCentroidDetector.Load(req.context())


if __name__ == '__main__':
    main(8003, '/tmp/', FlyCentroidDetector.DEFAULT_MODEL_URL)
