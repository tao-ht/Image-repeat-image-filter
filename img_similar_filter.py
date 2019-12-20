# -*- coding: utf-8 -*-
# Copyright hengtao tao. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cv2, os
import numpy as np
import time, json
import imagehash
from scipy.misc import imread, imresize
from PIL import Image
import os, shutil
from concurrent.futures import ThreadPoolExecutor
from skimage import io

def mycopyfile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!"%(srcfile))
    else:
        fpath, fname=os.path.split(dstfile)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        if not os.path.isfile(dstfile):
            shutil.copyfile(srcfile, dstfile)
            print("copy %s -> %s"%(srcfile, dstfile))

def pHash(img, read=False):
    if read:
        # img = io.imread(img)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.imread(img)
        img = cv2.resize(img, (32, 32), interpolation=cv2.INTER_CUBIC)
    vis = np.zeros_like(img)
    if len(img.shape)==3:
        vis[..., 0] = cv2.dct(cv2.dct(np.float32(img[..., 0])))
        vis[..., 1] = cv2.dct(cv2.dct(np.float32(img[..., 1])))
        vis[..., 2] = cv2.dct(cv2.dct(np.float32(img[..., 2])))
        vis1 = (vis[6:14, 6:14, 0] + vis[6:14, 18:26, 1] + vis[18:26, 6:14, 2] + vis[18:26, 18:26, 0] + vis[12:20, 12:20, 0] + vis[12:20, 12:20, 1] + vis[12:20, 12:20, 2])/7.0
    else:
        vis[..., 0] = cv2.dct(cv2.dct(np.float32(img[..., 0])))
        vis1 = (vis[6:14, 6:14, 0] + vis[6:14, 18:26, 0] + vis[18:26, 6:14, 0] + vis[18:26, 18:26, 0] + vis[12:20, 12:20, 0]) / 5.0
    img_list = vis1.reshape(-1).tolist()

    avg = np.mean(img_list)
    avg_list = ['0' if i < avg else '1' for i in img_list]

    phash = ['%d' % int("".join(avg_list[x:x + 3]), 2) for x in range(0, 8 * 8, 3)]
    int_hash = ''
    for i in phash:
        if int(i) < 10:
            int_hash += '0' + str(i)
        else:
            int_hash += str(i)
    int_hash = int(int_hash)
    return int_hash


def wHash(img, mode="db4", read=True):
    if read:
        img = Image.open(img)
    hash = imagehash.whash(img, image_scale=32, hash_size=8, mode=mode, remove_max_haar_ll=True)
    hash = np.array([int(i, 16) for i in str(hash)], np.int)
    int_hash = ''
    for i in hash:
        if i < 10:
            int_hash += '0' + str(i)
        else:
            int_hash += str(i)
    int_hash = int(int_hash)
    return int_hash

def dHash(img, read=False):
    if read:
        img = Image.open(img)
    hash = [int(i, 16) for i in str(imagehash.dhash(img, hash_size=10))]#8:32 9:21*2 10:25*2
    int_hash = ''
    for i in hash:
        if i < 10:
            int_hash += '0' + str(i)
        else:
            int_hash += str(i)
    int_hash = int(int_hash)
    return int_hash

def euclidean(node, ceil):
    return int(np.sqrt(np.sum(np.power(node - ceil, 2)))*10000000000)

def my_sort(dict):
    # dict = {k:(v[0], v[1], v[2]) for k, v in dict.items()}
    # sorted(zip(dict.values(), dict.keys()))
    return sorted(dict)

def find_Sorted_Position(List, target):
    """
    # 二分法查找100000000以内,查找耗时不超过1ms
    :param List: the list waiting to lookup
    :param target: target number
    :return: target's position
    """
    if target < List[0]:
        return 0
    elif target > List[-1]:
        return len(List)
    else:
        low = 0
        high = len(List) - 1
        while low <= high:
            mid = (high + low) // 2
            if high - low <= 1:
                return mid + 1
            elif target == List[mid]:
                return mid
            elif target < List[mid]:
                high = mid
            else:
                low = mid
        return low + 1

class Img_infobase():
    def __init__(self, infobase):
        self.infobase = infobase
        self.similar = []
        self.similar_now = []
        self.img_dict = []
        self.hash = []
        if os.path.isfile(self.infobase):
            time_read = time.time()
            with open(self.infobase, 'r') as load_info:
                load_dict = json.load(load_info)
                self.img_dict = load_dict["info_base"]
                self.hash = [i[0] for i in self.img_dict]
            print("读取图片信息库数据字典耗时: {:0.4f} s".format(time.time()-time_read))
            print("当前信息库图片数量： ", len(self.img_dict))

    def info_update(self, update=False):
        import time
        tm_min = time.localtime(time.time())[5]
        # 每30min更新一次图片信息库
        if tm_min % 31 == 0 or update:
            time_start = time.time()
            with open(self.infobase, 'w') as write_f:
                img_info = {"info_base": self.img_dict}
                json.dump(img_info, write_f)
            print("写/更新的图片信息库耗时： {:0.4f} s".format(time.time() - time_start, len(self.img_dict)))
            with open("similar_imgs.txt", 'a')as file_similar:
                for similar_img in self.similar:
                    file_similar.write(similar_img[0] + ' ' + similar_img[1] + '\n')

    def info_add(self, new_img_info, pos):
        self.img_dict.insert(pos, new_img_info)
        self.hash.insert(pos, new_img_info[0])

    def img_info(self, img_path):
        if '.jpg' in img_path:#2.8ms, only whash*3 2.0ms, only dwash*3 0.7ms
            img_information = [pHash(img_path, read=True), img_path]
            if not self.hash:
                self.img_dict.append(img_information)
                self.hash.append(img_information[0])
            else:
                img_pos = find_Sorted_Position(self.hash, img_information[0])
                if img_pos < len(self.hash) and self.hash[img_pos] == img_information[0]:
                    print("%s is similar to %s !"%(os.path.basename(img_path), self.img_dict[img_pos][1]))
                    self.similar.append([img_path, self.img_dict[img_pos][1]])
                    self.similar_now.append([img_path, self.img_dict[img_pos][1]])
                else:
                    self.info_add(img_information, img_pos)
        else:
            print("file %s in %s not jpg image !"%(os.path.basename(img_path), img_path))

    def multi_seek(self, imgs_url):
        """
        :param file_path: image dataset path
        :return: built image database information
        """
        time_start0 = time.time()
        for i in range(len(imgs_url)):
            if i % 50 == 0:
                img_url = imgs_url[i:i+50]
                p = ThreadPoolExecutor(8)
                p.map(self.img_info, img_url)
                p.shutdown()
            if i % 500 == 0 and i != 0:
                line = '[{}/{}] time: {:0.4f}, average: {:0.2f} ms'.format(i, len(imgs_url), time.time() - time_start0,
                                                                     (time.time() - time_start0)*1000/i)
                print(line)
        print('重复图查找平均耗时: {:0.4f} ms'.format((time.time() - time_start0)*1000/len(imgs_url)))
        self.info_update(update=True)
        return self.similar_now

if __name__ == '__main__':
    # 创建/初始化信息库
    IMG_info = Img_infobase("./image_infobase.json")
    filenames = []
    test_img_path = 'E:/2019/image_rm-dui/train250_silimar/'
    for root, _, filenames in os.walk(test_img_path):
        filenames = [os.path.join(root, i) for i in filenames]

    imgs_url = filenames
    similar = IMG_info.multi_seek(imgs_url=imgs_url)

