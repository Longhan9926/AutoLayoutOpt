import tensorflow as tf
import numpy as np
import os
import cv2
from scipy import misc
import imageio
import argparse
import sys

g_mean = np.array(([126.88, 120.24, 112.19])).reshape([1, 1, 3])
output_folder = "./test_output"


def rgba2rgb(img):
    return img[:, :, :3] * np.expand_dims(img[:, :, 3], 2)


def main(args):
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=args.gpu_fraction)
    with tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options)) as sess:
        saver = tf.compat.v1.train.import_meta_graph('./meta_graph/my-model.meta')
        saver.restore(sess, tf.compat.v1.train.latest_checkpoint('./salience_model'))
        image_batch = tf.compat.v1.get_collection('image_batch')[0]
        pred_mattes = tf.compat.v1.get_collection('mask')[0]

        if args.rgb_folder:
            rgb_pths = os.listdir(args.rgb_folder)
            for rgb_pth in rgb_pths:
                rgb = imageio.imread(os.path.join(args.rgb_folder, rgb_pth))
                if rgb.shape[2] == 4:
                    rgb = rgba2rgb(rgb)
                origin_shape = (rgb.shape[1],rgb.shape[0])
                rgb = np.expand_dims(
                    cv2.resize(rgb.astype(np.uint8), (320, 320), interpolation = cv2.INTER_NEAREST).astype(np.float32) - g_mean, 0)

                feed_dict = {image_batch: rgb}
                pred_alpha = sess.run(pred_mattes, feed_dict=feed_dict)
                final_alpha = cv2.resize(np.squeeze(pred_alpha), origin_shape)
                imageio.imwrite(os.path.join(output_folder, rgb_pth), final_alpha)

        else:
            rgb = imageio.imread(args.rgb)
            if rgb.shape[2] == 4:
                rgb = rgba2rgb(rgb)
            origin_shape = (rgb.shape[1],rgb.shape[0])
            rgb = np.expand_dims(
                cv2.resize(rgb.astype(np.uint8), (320, 320), interpolation = cv2.INTER_NEAREST).astype(np.float32) - g_mean, 0)

            feed_dict = {image_batch: rgb}
            pred_alpha = sess.run(pred_mattes, feed_dict=feed_dict)
            final_alpha = cv2.resize(np.squeeze(pred_alpha), origin_shape)
            imageio.imwrite(os.path.join(output_folder, 'alpha.png'), final_alpha)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--rgb', type=str,
                        help='input rgb', default=None)
    parser.add_argument('--rgb_folder', type=str,
                        help='input rgb', default=None)
    parser.add_argument('--gpu_fraction', type=float,
                        help='how much gpu is needed, usually 4G is enough', default=1.0)
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
