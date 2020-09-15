#import tensorflow as tf
#import matplotlib.pyplot as plt
#import numpy as np
#import cv2
#
#tf.keras.utils.get_file("clip.mp4", "https://www.dropbox.com/s/b8974dstznzjzv4/test_clip.15s.mp4?dl=1", extract=False, cache_subdir="/tmp/content")
#tf.keras.utils.get_file("keras_model.h5", "https://www.dropbox.com/s/kuyqdopree4fh0r/best_model.h5?dl=1", extract=False, cache_subdir="/tmp/content")
#
## Open video clip for reading.
#reader = cv2.VideoCapture("/tmp/content/clip.mp4")
#
## Get the number of frames in the video.
#n_frames = int(reader.get(cv2.CAP_PROP_FRAME_COUNT))
#print(f"n_frames = {n_frames}")
#
## Seek to specific frame and decode the image data.
#frame_idx = n_frames - 10
#reader.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
#status, img = reader.read()
#img = img[:, :, :1]  # convert to grayscale
#print(f"img.shape = {img.shape}")
#print(f"img.dtype = {img.dtype}")
#
## Visualize image.
#plt.figure(figsize=(8, 8))
#plt.imshow(img.squeeze(), cmap="gray");
#
## Load keras model.
#model = tf.keras.models.load_model("/tmp/content/keras_model.h5",
#                                   compile=False)
#print(f"Inputs: {model.inputs}")
#print(f"Outputs: {model.outputs}")
#
## Preprocess the image for inference.
## Note that the input must be float32 in [0, 1] and of rank 4 with shape
## (batch_size, height, width, 1).
#X = np.expand_dims(img, axis=0).astype("float32") / 255.
#X = tf.image.resize(X, size=[512, 512])
#
## Predict on image.
#Y = model.predict(X)
#print(f"Y.shape = {Y.shape}")
#print(f"Y.dtype = {Y.dtype}")
#
## Visualize output.
#plt.figure(figsize=(9, 8))
#plt.imshow(Y.squeeze())
#plt.colorbar();
#
#plt.show()
