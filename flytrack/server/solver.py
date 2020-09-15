import numpy as np
import tensorflow as tf


DEFAULT_MODEL_URL = \
        'https://www.dropbox.com/s/kuyqdopree4fh0r/best_model.h5?dl=1'

class FlyCentroidDetector:
    DEFAULT_MODEL_URL = DEFAULT_MODEL_URL

    def __init__(self, cache_directory='/tmp', model_url=DEFAULT_MODEL_URL):
        model_path = tf.keras.utils.get_file(
                                'model.h5',
                                model_url,
                                extract=False,
                                cache_subdir=cache_directory)
        self.__model = tf.keras.models.load_model(model_path, compile=False)

    def generate_heatmap(self, img, upsample_heatmap=False):
        # Convert to grayscale if necessary.
        if img.shape[-1] != 1:
            img = img[:, :, :1]

        # Scale to [0, 1]
        X = np.expand_dims(img, axis=0).astype("float32") / 255.

        # Normalize to fixed dimensions.
        X = tf.image.resize(X, size=[512, 512])

        # Perform the prediction and return.
        Y = self.__model.predict(X)

        # If we want to upsample back to original image dimensions.
        if upsample_heatmap:
            Y = tf.image.resize(Y, size=img.shape[:2])

        return Y

    def find_centroids(self, img):
        # Use max pooling to find the centroid.
        max_pooled = tf.nn.pool(img, window_shape=(3, 3),
                                pooling_type='MAX',
                                padding='SAME')
        maxima = tf.where(tf.equal(img, max_pooled), img, tf.zeros_like(img))

        # Squeeze out the unused dimension
        maxima = tf.squeeze(maxima)

        # Find global maximum
        maximum = tf.math.reduce_max(maxima)

        # Find the indices of the local maximums
        indices = tf.where(maxima > 0.5 * maximum).numpy().astype(np.float64)
        indices /= tf.squeeze(img).shape

        # Tensorflow column/row conventions are opposite of what is desired
        # for this application.
        indices[:,[0, 1]] = indices[:,[1, 0]]

        return indices


