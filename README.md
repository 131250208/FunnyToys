# FunnyToys
放一些有趣的code

## 李峋同款爱心代码（附蝴蝶代码）
1. 代码是上面的heart.py 有python环境可以直接运行：python heart.py 默认循环跳动10个周期，可以自己修改代码。没有python环境的朋友自己搜一下安装配置教程吧
2. 近期会上传一键运行版本（无需安装环境）

参考了B站UP主码农高天的[视频](https://www.bilibili.com/video/BV16g411B7Ff/?spm_id_from=333.880.my_history.page.click&vd_source=ba45c0407ee008ebddccf236e153d82a)
另外自己做了改进：
1. 用numpy实现提高效率
2. 用opencv来刷新帧，比tkinter要快，避免点过多的时候卡顿
3. 根据周期调整心形的饱满程度，看起来更像是跳动
4. 根据周期调整光晕的散点分布，正态分布使其看上去边缘的粒子更像是被振开！
5. 加了一个蝴蝶曲线
6. 加上高亮粒子，使其更美观
