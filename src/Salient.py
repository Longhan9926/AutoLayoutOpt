import cv2
import imageio
import numpy as np
import tensorflow as tf

g_mean = np.array(([126.88, 120.24, 112.19])).reshape([1, 1, 3])
salience_bar = 0.7
len_px = 3.7795275591


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
        saver = tf.compat.v1.train.import_meta_graph('/Users/macos/PycharmProjects/AutoLayoutOpt/src/salient/meta_graph/my-model.meta')
        saver.restore(sess, tf.compat.v1.train.latest_checkpoint('/Users/macos/PycharmProjects/AutoLayoutOpt/src/salient/salience_model'))
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


def label_salient_region_cv(image):
    saliencyAlgorithm = cv2.saliency.StaticSaliencyFineGrained_create()
    success, saliencyMap = saliencyAlgorithm.computeSaliency(image)
    return saliencyMap


# def crop_salient(image, target_size):
#     """
#     :param file_path:
#     :param target_size: [width, height]
#     :return:
#     """
#     mask = label_salient_region(image)
#     mask = np.where(mask > 0.5, 1, 0)
#     m, n = mask.shape
#     mask_sum = np.zeros((m+1, n+1))
#     for i in range(1, m+1):
#         for j in range(1, n+1):
#             mask_sum[i, j] = mask_sum[i, j - 1] + mask_sum[i - 1, j] - mask_sum[i - 1, j - 1] + mask[i-1, j-1]
#
#     """
#     def cal_salient_score(p):
#
#         :param p: parameter, include real position of the left-top corner and right-bottom corner
#         :return: the evaluation score of the salient crop
#
#         p_res = [math.floor(x * len_px) for x in p]
#         if p_res[0] < p_res[2]:
#             left, top, right, btm = p_res
#         else:
#             right, btm, left, top = p_res
#         if left == right or top == btm or (left - right) * (top - btm) <= 0:
#             return -10000
#         mask_cropped = mask[top:btm, left:right]
#         width = mask_cropped.shape[1]
#         height = mask_cropped.shape[0]
#         sum_importance = mask_cropped.sum()
#         area = width * height
#         importance_percentage = sum_importance / area
#         edge_importance = sum(mask_cropped[0]) + sum(mask_cropped[-1])+sum(mask_cropped[:][0]) + sum(mask_cropped[:][-1])
#         salient_score = sum_importance**2 / math.exp(100*abs(importance_percentage - salience_bar)) - edge_importance*10
#         # print(salient_score, area)
#         return salient_score
#     """
#
#     def cal_salient_score(p):
#         """
#         :param p: parameter, include real position of the left-top corner and right-bottom corner
#         :return: the evaluation score of the salient crop
#         """
#         ring = 2
#         p_res = [math.floor(x * len_px) for x in p]
#         if p_res[0] < p_res[2]:
#             left, top, right, btm = p_res
#         else:
#             right, btm, left, top = p_res
#         if left >= right or top >= btm:
#             return -1000000
#         sum_importance = mask_sum[btm+1, right+1] - mask_sum[btm+1, left] - mask_sum[top, right+1] + mask_sum[top, left]
#         area = (btm - top) * (right - left)
#         importance_percentage = sum_importance / area
#         edge_importance = sum_importance - (mask_sum[btm, right] - mask_sum[btm, left+1] - mask_sum[top+1, right] + mask_sum[top+1, left+1])
#         if edge_importance / (btm-top+right-left) > 0.5:
#             return -1000000
#         # print(importance_percentage, area)
#         salient_score = 100 * sum_importance ** 3 / math.exp(100 * abs(importance_percentage - salience_bar)) - edge_importance
#         # print(salient_score, area)
#         return salient_score
#
#     def crop_n_scale(origin_size, target_size):
#         """
#         crop the original picture into the target shape
#         :param origin_size: [width, height] in resolution, need to convert to real length
#         :param target_size: [width, height] in resolution, need to convert to real length
#         :return: image
#         """
#         hor = origin_size[1] / len_px
#         ver = origin_size[0] / len_px
#         constraint_eq = [
#             lambda x: (x[2] - x[0]) * target_size[1] - (x[3] - x[1]) * target_size[0],
#             lambda x: x[2] - x[0] - target_size[0] / len_px
#         ]
#         num_points = 5000
#
#         ga = GA(func=cal_salient_score, n_dim=4, size_pop=num_points, max_iter=100, \
#                 lb=[0, 0, 0, 0], ub=[hor-0.4, ver-0.4, hor-0.4, ver-0.4], constraint_eq=constraint_eq, precision=0.01)
#         best_loc, best_score = ga.run()
#
#         #pso = PSO(func=cal_salient_score,n_dim=4, pop=num_points, max_iter=200, \
#         #        lb=[0, 0, 0, 0], ub=[hor-0.4, ver-0.4, hor-0.4, ver-0.4], constraint_eq=constraint_eq, w=0.8, c1=0.5, c2=0.5)
#         #best_loc, best_score = pso.run()
#         return [best_loc, best_score]
#
#     best_loc, best_score = crop_n_scale(mask.shape, target_size)
#     loc_res = [math.floor(x * len_px) for x in best_loc]
#     if best_loc[0] < best_loc[2]:
#         left, top, right, btm = loc_res
#     else:
#         right, btm, left, top = loc_res
#     #print(left, top, right, btm)
#     image_cropped = image[top:btm, left:right]
#     return image_cropped

def crop_salient(image, target_size):
    """
    :param file_path:
    :param target_size: [width, height]
    :return:
    """
    mask = label_salient_region_cv(image)
    # mask = np.where(mask > 0.5, 1, 0)
    m, n = mask.shape
    mask_sum = np.zeros((m + 1, n + 1))
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            mask_sum[i, j] = mask_sum[i, j - 1] + mask_sum[i - 1, j] - mask_sum[i - 1, j - 1] + mask[i - 1, j - 1]

    def crop_n_scale(origin_size, target_size):
        """
        crop the original picture into the target shape
        :param origin_size: [width, height] in resolution, need to convert to real length
        :param target_size: [width, height] in resolution, need to convert to real length
        :return: image
        """
        origin_size = [origin_size[1], origin_size[0]]
        if origin_size[0]*target_size[1] - origin_size[1]*target_size[0] > 0:
            target_size[0] = (target_size[0] * origin_size[1]) // target_size[1]
            target_size[1] = origin_size[1]
            lim = origin_size[0] - target_size[0]
            S = [mask_sum[-1,i+target_size[0]]-mask_sum[-1,i] for i in range(lim)]
            left = np.argmax(S)
            image_cropped = image[:,left:left+target_size[0]]
            return image_cropped
        else:
            target_size[1] = (target_size[1] * origin_size[0]) // target_size[0]
            target_size[0] = origin_size[0]
            lim = origin_size[1] - target_size[1]
            S = [mask_sum[i + target_size[1],-1] - mask_sum[i,-1] for i in range(lim)]
            left = np.argmax(S)
            image_cropped = image[left:left + target_size[1],:]
            return image_cropped

    def direct_scale(origin_size, target_size, image):
        if image.shape[-1] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
            image[:, :, 3] = 255
        origin_size = [origin_size[1], origin_size[0]]
        if origin_size[0] * target_size[1] - origin_size[1] * target_size[0] < 0:
            target_size[0] = (target_size[0] * origin_size[1]) // target_size[1]
            target_size[1] = origin_size[1]
            lim = - origin_size[0] + target_size[0]
            canva = np.ones((target_size[1], target_size[0], 4))*255
            canva[:,lim // 2:lim // 2 + origin_size[0]] = image
            return canva
        else:
            target_size[1] = (target_size[1] * origin_size[0]) // target_size[0]
            target_size[0] = origin_size[0]
            lim = - origin_size[1] + target_size[1]
            canva = np.ones((target_size[1], target_size[0], 4))*255
            canva[lim//2:lim//2 + origin_size[1],:] = image
            return canva

    mode = np.random.choice((1,0))
    if mode == 1:
        return crop_n_scale(mask.shape, target_size)
    else:
        # return crop_n_scale(mask.shape, target_size)
        return direct_scale(mask.shape, target_size, image)


if __name__ == '__main__':
    file_path = '../input/img/free_stock_photo.jpg'
    image = imageio.imread(file_path)
    image_cropped = crop_salient(image, [300, 400])
    imageio.imwrite('cropped.png', image_cropped)
