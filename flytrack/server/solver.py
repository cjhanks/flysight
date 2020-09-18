import numpy as np
import tensorflow as tf
from flytrack.config import Config


class FlyCentroidDetector:
    """
    :class FlyCentroidDetector:

    This class can be slightly expensive to instantiate and should only be done
    once.  Wraps the necessary tensorflow logic for extracting information from
    images and heatmaps.
    """
    def __init__(self):
        url   = Config.Instance.model.url
        cache = Config.Instance.model.cache
        model_path = tf.keras.utils.get_file(
                                'model.h5',
                                url,
                                extract=False,
                                cache_subdir=cache)
        self.__model = tf.keras.models.load_model(model_path, compile=False)

    def generate_heatmap(
            self, img: np.array, upsample_heatmap: bool = False) -> np.array:
        """
        Given an `img` input use the tensorflow prediction to generate a
        heatmap.  The heatmap is a float32 matrix.
        """
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

    def find_peaks(self, heatmap: np.array) -> np.array:
        """
        Given an input `heatmap`, use non-max suppression to detect the peaks.
        """
        # Use max pooling to find the centroid.
        dim = (Config.Instance.centroid_detector.nonmax_suppression_dim,
               Config.Instance.centroid_detector.nonmax_suppression_dim)
        max_pooled = tf.nn.pool(heatmap, window_shape=dim,
                                pooling_type='MAX',
                                padding='SAME')
        maxima = tf.where(tf.equal(heatmap, max_pooled), heatmap,
                          tf.zeros_like(heatmap))

        # Squeeze out the unused dimension
        maxima = tf.squeeze(maxima)

        # Find global maximum
        maximum = tf.math.reduce_max(maxima)

        # Find the indices of the local maximums
        threshold = Config.Instance.centroid_detector.coef_maximum_threshold
        indices = tf.where(maxima > threshold * maximum).numpy(
                          ).astype(np.float64)
        indices /= tf.squeeze(heatmap).shape

        # Tensorflow column/row conventions are opposite of what is desired
        # for this application.
        indices[:,[0, 1]] = indices[:,[1, 0]]

        return indices


