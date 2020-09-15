import numpy as np
import zmq
from flytrack.message_pb2 import (
        Request,
        RepDetections,
        RepTracking,
        )

class Client:
    def __init__(self, uri):
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.REQ)
        self.socket.connect(uri)

        # {
        self.return_heatmap = True
        self.return_peaks = True
        # }

    def detect(self, image):
        req = Request()
        detect = req.detections
        detect.return_heatmap = self.return_heatmap
        detect.return_peaks = self.return_peaks
        detect.upsample_heatmap = True
        detect.image.data = image.tobytes()
        detect.image.rows = image.shape[0]
        detect.image.cols = image.shape[1]
        self.socket.send(req.SerializeToString())

        rep = self.socket.recv()
        detections = RepDetections()
        detections.ParseFromString(rep)

        if self.return_heatmap:
            image = np.frombuffer(detections.heatmap.data, dtype=np.float32
                    ).reshape(detections.heatmap.rows,
                              detections.heatmap.cols)
        else:
            image = None

        peaks = []
        for peak in detections.peaks:
            peaks.append((peak.row, peak.col))

        return (image, peaks)


