import numpy as np
import cv2
import math
import tensorflow as tf
import imageio
import sko
from sko.GA import GA

g_mean = np.array(([126.88, 120.24, 112.19])).reshape([1, 1, 3])
salience_bar = 0.6


def label_salient_region(image):
    """
    Detect the salient region of a picture
    :param image: image read by imageio, 4 channels
    :return: labelled mask of the salient region
    """
    image_size = image.shape
    mask = np.zeros(image_size[0:2])

    gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=1.0)
    with tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options)) as sess:
        saver = tf.compat.v1.train.import_meta_graph('./salient/meta_graph/my-model.meta')
        saver.restore(sess, tf.compat.v1.train.latest_checkpoint('./salient/salience_model'))
        image_batch = tf.compat.v1.get_collection('image_batch')[0]
        pred_mattes = tf.compat.v1.get_collection('mask')[0]

        origin_shape = (image_size[1], image_size[0])
        image = np.expand_dims(cv2.resize(image.astype(np.uint8), (320, 320), \
                                          interpolation=cv2.INTER_NEAREST).astype(np.float32) - g_mean, 0)

        feed_dict = {image_batch: image}
        pred_alpha = sess.run(pred_mattes, feed_dict=feed_dict)
        mask = cv2.resize(np.squeeze(pred_alpha), origin_shape)
        # imageio.imwrite('alpha.png', mask)
    return mask


def cal_salient_score(mask_cropped):
    width = mask_cropped.shape[1]
    height = mask_cropped.shape[0]
    sum_importance = sum(mask_cropped)
    area = width * height
    importance_percentage = sum_importance / area
    edge_importance = sum(mask_cropped[0])+sum(mask_cropped[-1])
    salient_score = sum_importance/math.exp(abs(importance_percentage-salience_bar))
    return salient_score


def crop_n_scale(origin_size, target_size, mask):
    """
    crop the original picture into the target shape
    :param target_size: [width, height]
    :return: image
    """
    num_points = 50

    points_coordinate = np.random.rand(num_points, 2)  # generate coordinate of points
    ga_tsp = GA(func=cal_salient_score(), n_dim=2, size_pop=num_points, max_iter=800, lb=[0, -1], ub=[1, 1], precision=1e-7)
    best_points, best_distance = ga_tsp.run()


if __name__ == '__main__':
    file_path = '../input/img/free_stock_photo.jpg'
    image = imageio.imread(file_path)
    mask = label_salient_region(image)

