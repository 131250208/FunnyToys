# FunnyToys
放一些有趣的code

## 李峋同款爱心代码（附蝴蝶代码）
1. 源代码是上面的heart.py 有python环境可以直接运行：python heart.py 默认循环跳动5个周期，可以自己修改代码。没有python环境的朋友自己搜一下安装配置教程吧
2. 下载完python, 再打开命令行安装3个工具包：`pip install numpy opencv-python pyyaml`, 安装完毕即可正常使用
2. 一键运行文件已打包好上传[百度云盘](https://pan.baidu.com/s/1jyoka14XncXCYtUwqHWT_Q?pwd=4whe)（无需装环境，对小白友好~直接解压双击运行即可）

## 一键版使用说明
1. 双击heart.exe运行
2. settings.yaml里可以改颜色、图案（爱心、蝴蝶、五角星、六角星、七角星）、图案和背景的透明度等
3. src/center_imgs里可以存放背景图片（会以第一张的尺寸为准），在settings.yaml里设置set_bg_imgs为false可以回到原版黑背景（默认为true，使用背景图片）
4. 背景图片尽量选择宽高400像素以上的，不必要的报错发生，如果图像实在太小，调整settings里的scale缩小爱心
5. 其他参数说明详见settings.yaml里 # 以后的注释部分

注意：
1. 杀毒软件报毒属于误报
2. 有些同学运行出现闪烁，可能也是杀毒软件的问题，短暂关闭杀软即可
3. 作为一个用真实身份在网络上发视频的博主，人格担保此软件绝对无毒无木马

## 参考
参考了B站UP主码农高天的[视频](https://www.bilibili.com/video/BV16g411B7Ff/?spm_id_from=333.880.my_history.page.click&vd_source=ba45c0407ee008ebddccf236e153d82a)
另外自己做了改进：
1. 用numpy实现提高效率
2. 用opencv来刷新帧，比tkinter要快，避免点过多的时候卡顿
3. 根据周期调整心形的饱满程度，看起来更像是跳动
4. 根据周期调整光晕的散点分布，正态分布使其看上去边缘的粒子更像是被振开！
5. 加了一个蝴蝶曲线
6. 加上高亮粒子，使其更美观
