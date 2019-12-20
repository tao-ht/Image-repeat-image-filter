## Image-repeat-image-filter
millisecond repeat image filter with Photo gallery 毫秒级图片库去重， 去重效率与图片库数量无关，0.1~10ms

* 实现算法思路
```
1.多线程提取图片的hash值；
2.hash转化成32~64位长索引值, 在信息库中顺序查找索引，相同索引为重复图；
3.如无重复，将提取图片信息按索引顺序插入信息库；
```
* requirement:
```
cv2
PIL
concurrent
imagehash or use my phash only
```
* 图片信息保存的信息库
```
image_infobase.json
{"info_base": [[hash_index, image_path], ...]}
信息库大小会影响读写时的速度，基本不影响查找时间。
```
* 本地测试结果展示
```
读取图片信息库数据字典耗时: 0.6860 s
当前信息库图片数量：  436776
10-57_50157089.jpg is similar to E:/2019/image_rm-dui/train0/57_50157089.jpg !
100-57_49992915.jpg is similar to E:/2019/image_rm-dui/train0/57_49992915.jpg !
0-69_50002503.jpg is similar to E:/2019/image_rm-dui/train0/69_50002503.jpg !
1-69_50362572.jpg is similar to E:/2019/image_rm-dui/train0/69_50002503.jpg !
1002-69_49593728.jpg is similar to E:/2019/image_rm-dui/train0/69_49593728.jpg !
1000-69_49924978.jpg is similar to E:/2019/image_rm-dui/train0/69_49924978.jpg !
1001-69_49926153.jpg is similar to E:/2019/image_rm-dui/train0/69_49924978.jpg !
1003-69_49614853.jpg is similar to E:/2019/image_rm-dui/train0/69_49593728.jpg !
重复图查找平均耗时: 0.2556 ms
写/更新的图片信息库耗时： 1.3470 s
```
* 觉得还行，点个star呗
##
Copyright hengtao tao. All Rights Reserved.














