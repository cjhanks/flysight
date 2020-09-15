#import solver
#import tensorflow as tf
#import matplotlib.pyplot as plt
#import matplotlib.patches as patch
#import cv2
#
##help(cv2.Feature2D)
#
#detector = solver.FlyCentroidDetector()
#
#
#plt.ion()
#fig = plt.figure()
#ax  = fig.add_subplot(111)
#
##plt.imshow(img)
#
##reader = cv2.VideoCapture("/tmp/content/clip.mp4")
#sift = cv2.xfeatures2d.SIFT_create()
#matcher = cv2.BFMatcher()
#previous_features = None
#previous_image = None
#previous_kps = None
#
#reader = cv2.VideoCapture("/tmp/content/many_flies.mp4")
#while True:
#    status, img = reader.read()
#    if not status:
#        break
#
#    ax.clear()
#
#    heatmap = detector.generate_heatmap(img, True)
#    maxed = detector.find_centroids(heatmap)
#    kps = [cv2.KeyPoint(*i, 48) for i in maxed * img.shape[:2]]
#
#    (_, features) = sift.compute(img, keypoints=kps)
#
#    ax.imshow(tf.squeeze(heatmap))
#    ax.imshow(img)
#
#    if previous_features is not None:
#        matches = matcher.knnMatch(features, previous_features, k=1)
#        for match in matches:
#            match = match[0]
#            print(match)
#            print(match.queryIdx, match.trainIdx)
#        #print(matches)
#        #print(len(kps))
#        #print(len(matches))
#        #plt.imshow(draw)
#
#
#    previous_features = features
#    previous_image = img
#    previous_kps = kps
#
#    #print(features)
#
#    fig.canvas.draw()
#    fig.canvas.flush_events()
#
#
##plt.figure()
##plt.imshow(heatmap.squeeze())
#
##print(maxed)
#
##plt.figure()
##plt.imshow(maxed.squeeze())
#
##plt.show()
