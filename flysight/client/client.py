import numpy as np
import zmq
from flysight.message_pb2 import (
        Request,
        RepDetections,
        RepTracking,
        )

class Client:
    """
    :class Client:

    Small wrapper over the ZMQ socket which implements the necessary protobuf
    packaging logic.
    """
    def __init__(self, uri: str):
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.REQ)
        self.socket.connect(uri)

        # {
        self.return_heatmap = True
        self.return_peaks = True
        # }

    def detect(self, image: np.array) -> (np.array, [(float, float)]):
        """
        This is the network interface for handling detections.  It does;
        - Create an appropriate request protobuf message.
        - Sends it to the client.
        - Receives the response.
        - Unpack the heatmap (if present)
        - Unpack the peaks computed (if present)
        """
        # {
        # Package the request.
        req = Request()
        detect = req.detections
        detect.return_heatmap = self.return_heatmap
        detect.return_peaks = self.return_peaks
        detect.upsample_heatmap = True
        detect.image.data = image.tobytes()
        detect.image.rows = image.shape[0]
        detect.image.cols = image.shape[1]
        self.socket.send(req.SerializeToString())
        # }

        # Receive the results
        rep = self.socket.recv()

        # {
        # Unpack the results.
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
        # }

        return (image, peaks)

