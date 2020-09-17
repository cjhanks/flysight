"""
This file is responsible for implementing a server side `main` function.
"""
import numpy as np
import tensorflow as tf
import zmq
from flytrack.message_pb2 import (
        Request,
        RepTracking,
        RepDetections,
        )
from flytrack.server.solver import FlyCentroidDetector
#from flytrack.server.tracker import FlyCentroidTracker


def main(zmq_port, cache_directory,
         model_url=FlyCentroidDetector.DEFAULT_MODEL_URL):
    detector = FlyCentroidDetector(cache_directory, model_url)
    tracker = None

    ctx = zmq.Context()
    socket = ctx.socket(zmq.REP)
    socket.bind('tcp://*:{}'.format(zmq_port))

    while True:
        message = socket.recv()

        try:
            req = Request()
            req.ParseFromString(message)
        except Exception as err:
            print('Error: %s' % err)
            socket.send(b'ERROR: %s' % err)
            continue

        if   req.HasField('detections'):
            rep = handle_detection(req.detections, detector)
        elif req.HasField('tracking'):
            rep = handle_tracking(req.tracking)
        else:
            rep.send(b'ERROR: Incomprehensible request.')
            continue

        socket.send(rep.SerializeToString())


def handle_detection(req, detector):
    rep = RepDetections()

    image = np.frombuffer(req.image.data, dtype=np.uint8).reshape(
                            req.image.rows,
                            req.image.cols,
                            1)
    heatmap = detector.generate_heatmap(image, req.upsample_heatmap)

    if req.return_peaks:
        print('peaks')
        peaks = detector.find_centroids(heatmap)
        print('peaks')
        for peak in peaks:
            rpeak = rep.peaks.add()
            rpeak.row = peak[0]
            rpeak.col = peak[1]

    if req.return_heatmap:
        print('Heatmap requested.')
        hm = tf.squeeze(heatmap)
        rep.heatmap.rows = hm.shape[0]
        rep.heatmap.cols = hm.shape[1]
        rep.heatmap.data = hm.numpy().tobytes()

    return rep

def handle_tracking(req):
    if not req.has_context():
        tracker = FlyCentroidDetector()
    else:
        tracker = FlyCentroidDetector.Load(req.context())


if __name__ == '__main__':
    main(8003, '/tmp/', FlyCentroidDetector.DEFAULT_MODEL_URL)
