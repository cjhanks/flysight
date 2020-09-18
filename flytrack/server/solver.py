import numpy as np
import tensorflow as tf
from flytrack.config import Config


class FlyCentroidDetector:
    def __init__(self):
        url   = Config.Instance.model.url
        cache = Config.Instance.model.cache
        model_path = tf.keras.utils.get_file(
                                'model.h5',
                                url,
                                extract=False,
                                cache_subdir=cache)
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
        dim = (Config.Instance.centroid_detector.nonmax_suppression_dim,
               Config.Instance.centroid_detector.nonmax_suppression_dim)
        max_pooled = tf.nn.pool(img, window_shape=dim,
                                pooling_type='MAX',
                                padding='SAME')
        maxima = tf.where(tf.equal(img, max_pooled), img, tf.zeros_like(img))

        # Squeeze out the unused dimension
        maxima = tf.squeeze(maxima)

        # Find global maximum
        maximum = tf.math.reduce_max(maxima)

        # Find the indices of the local maximums
        threshold = Config.Instance.centroid_detector.coef_maximum_threshold
        indices = tf.where(maxima > threshold * maximum).numpy(
                          ).astype(np.float64)
        indices /= tf.squeeze(img).shape

        # Tensorflow column/row conventions are opposite of what is desired
        # for this application.
        indices[:,[0, 1]] = indices[:,[1, 0]]

        return indices


