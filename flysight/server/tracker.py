import pickle
import numpy as np

#def nearest_neighbor(value, array):
#    #return np.argmin(np.linalg.norm(array - value))
#    norms = np.linalg.norm(array - value, axis=1)
#    index = np.argmin(norms)
#    return (norms[index], index)
#
#print(nearest_neighbor(
#      np.array([1., 1.1]),
#      np.array([
#          [1.00, 1.31],
#          [1.00, 1.21],
#          [1.10, 1.11]
#      ])))
#
#
#class FlyCentroidTrackerTrack:
#    Id = 0
#    def __init__(self, row, col):
#        self.id  = self.Id
#        self.row = row
#        self.col = col
#        self.Id += 1
#
#    def array(self):
#        return np.array([self.row, self.col])
#
#class FlyCentroidTrackerContext:
#    def __init__(self):
#        self.tracks = []
#
#    def to_array(self):
#        data = []
#        for track in self.tracks:
#            data.append((track.row, track.col))
#        return np.array(data)
#
#class FlyCentroidTracker:
#    @staticmethod
#    def Load(data):
#        return FlyCentroidTracker(pickle.loads(data))
#
#    def __init__(self, ctx=None):
#        self.ctx = ctx or FlyCentroidTrackerContext()
#
#    def update_track(self, tracks):
#        # Initialize the tracks.
#        new_tracks = []
#        for track in tracks:
#            new_tracks.append((track.row, track.col))
#
#        new_tracks = np.array(new_tracks)
#        old_tracks = ctx.tracks.to_array()
#
#        # Track
#        for track in new_tracks:
#            (value, index) = nearest_neighbor(track, old_tracks)
#
#
#class K:
#    pass
#trck = FlyCentroidTrackerTrack()

