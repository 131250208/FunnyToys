from math import cos, pi
import numpy as np
import cv2


class HeartSignal:
    def __init__(self, frame_num=20, seed_points_num=2000, seed_num=None, frame_width=1080, frame_height=960, scale=10.1):
        super().__init__()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.center_x = self.frame_width / 2
        self.center_y = self.frame_height / 2

        self._points = set()  # 主图坐标点
        self._edge_diffusion_points = set()  # 边缘扩散效果点坐标集合
        self._center_diffusion_points = set()  # 中心扩散效果点坐标集合
        self._heart_halo_point = set()  # 光晕效果坐标集合
        self.frame_points = []  # 每帧动态点坐标
        self.frame_num = frame_num
        self.seed_num = seed_num
        self.seed_points_num = seed_points_num
        self.scale = scale

    def heart_function(self, t, frame_idx=0, scale=5.20):
        """
        图形方程
        :param frame_idx: 帧的索引，根据帧数变换心形
        :param scale: 放大比例
        :param t: 参数
        :return: 坐标
        """
        trans = 3
        trans = 3 - (1 + self.curve(frame_idx, self.frame_num)) * 0.5  # 改变心形饱满度度的参数

        x = 15 * (np.sin(t) ** 3)
        t = np.where((pi < t) & (t < 2 * pi), 2 * pi - t, t)  # 翻转x > 0部分的图形到3、4象限
        y = -(14 * np.cos(t) - 4 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(trans * t))

        ign_area = 0.15
        center_ids = np.where((x > -ign_area) & (x < ign_area))
        if np.random.random() > 0.32:
            x, y = np.delete(x, center_ids), np.delete(y, center_ids)  # 删除稠密部分的扩散，为了美观

        # 放大
        x *= scale
        y *= scale

        # 移到画布中央
        x += self.center_x
        y += self.center_y


        # 原心形方程
        # x = 15 * (sin(t) ** 3)
        # y = -(14 * cos(t) - 4 * cos(2 * t) - 2 * cos(3 * t) - cos(3 * t))
        return x.astype(int), y.astype(int)

    def butterfly_function(self, t, frame_idx=0, scale=64):
        """
        图形函数
        :param frame_idx:
        :param scale: 放大比例
        :param t: 参数
        :return: 坐标
        """
        # 基础函数
        # x = 15 * (sin(t) ** 3)
        # y = -(14 * cos(t) - 4 * cos(2 * t) - 2 * cos(3 * t) - cos(3 * t))
        t = t * pi
        p = np.exp(np.sin(t)) - 2.5 * np.cos(4 * t) + np.sin(t) ** 5
        x = p * np.cos(t)
        y = - p * np.sin(t)

        # 放大
        x *= scale
        y *= scale

        # 移到画布中央
        x += self.center_x
        y += self.center_y

        return x.astype(int), y.astype(int)

    def shrink(self, x, y, ratio, offset=1, p=0.5, dist_func="uniform"):
        """
        带随机位移的抖动
        :param x: 原x
        :param y: 原y
        :param ratio: 缩放比例
        :param p:
        :param offset:
        :return: 转换后的x,y坐标
        """
        x_ = (x - self.center_x)
        y_ = (y - self.center_y)
        force = 1 / ((x_ ** 2 + y_ ** 2) ** p + 1e-30)

        dx = ratio * force * x_
        dy = ratio * force * y_

        def d_offset(x):
            if dist_func == "uniform":
                return x + np.random.uniform(-offset, offset, size=x.shape)
            elif dist_func == "norm":
                return x + offset * np.random.normal(0, 1, size=x.shape)

        dx, dy = d_offset(dx), d_offset(dy)

        return x - dx, y - dy

    def scatter(self, x, y, alpha=0.75, beta=0.15):
        """
        随机内部扩散的坐标变换
        :param alpha: 扩散因子 - 松散
        :param x: 原x
        :param y: 原y
        :param beta: 扩散因子 - 距离
        :return: x,y 新坐标
        """

        ratio_x = - beta * np.log(np.random.random(x.shape) * alpha)
        ratio_y = - beta * np.log(np.random.random(y.shape) * alpha)
        dx = ratio_x * (x - self.center_x)
        dy = ratio_y * (y - self.center_y)

        return x - dx, y - dy

    def curve(self, x, x_num):
        """
        跳动周期曲线
        :param p: 参数
        :return: y
        """

        # 可以尝试换其他的动态函数，达到更有力量的效果（贝塞尔？）
        def ori_func(t):
            return cos(t)

        func_period = 2 * pi
        return ori_func(x / x_num * func_period)

    def gen_points(self, points_num, frame_idx, shape_func):
        # 用周期函数计算得到一个因子，用到所有组成部件上，使得各个部分的变化周期一致
        cy = self.curve(frame_idx, self.frame_num)
        ratio = 10 * cy

        # 图形
        seed_points = np.linspace(0, 2 * pi, points_num)
        seed_x, seed_y = shape_func(seed_points, frame_idx, scale=self.scale)
        x, y = self.shrink(seed_x, seed_y, ratio, offset=2)
        point_size = np.random.choice([1, 2], x.shape, replace=True, p=[0.5, 0.5])
        tag = np.ones_like(x)

        def delete_points(x_, y_, ign_area, ign_prop):
            ign_area = ign_area
            center_ids = np.where((x_ > self.center_x - ign_area) & (x_ < self.center_x + ign_area))
            center_ids = center_ids[0]
            np.random.shuffle(center_ids)
            del_num = round(len(center_ids) * ign_prop)
            del_ids = center_ids[:del_num]
            x_, y_ = np.delete(x_, del_ids), np.delete(y_, del_ids)  # 删除稠密部分的扩散，为了美观
            return x_, y_

        # 多层次扩散
        for idx, beta in enumerate(np.linspace(0.05, 0.2, 6)):
            alpha = 1 - beta
            x_, y_ = self.scatter(seed_x, seed_y, alpha, beta)
            x_, y_ = self.shrink(x_, y_, ratio, offset=round(beta * 15))
            x = np.concatenate((x, x_), 0)
            y = np.concatenate((y, y_), 0)
            p_size = np.random.choice([1, 2], x_.shape, replace=True, p=[0.55 + beta, 0.45 - beta])
            point_size = np.concatenate((point_size, p_size), 0)
            tag_ = np.ones_like(x_) * 2
            tag = np.concatenate((tag, tag_), 0)

        # 光晕
        halo_ratio = int(7 + 2 * abs(cy))  # 收缩比例随周期变化

        # 基础光晕
        x_, y_ = shape_func(seed_points, frame_idx, scale=self.scale + 0.9)
        x_1, y_1 = self.shrink(x_, y_, halo_ratio, offset=18, dist_func="uniform")
        x_1, y_1 = delete_points(x_1, y_1, 20, 0.5)
        x = np.concatenate((x, x_1), 0)
        y = np.concatenate((y, y_1), 0)

        # 炸裂感光晕
        halo_number = int(points_num * 0.6 + points_num * abs(cy))  # 光晕点数也周期变化
        seed_points = np.random.uniform(0, 2 * pi, halo_number)
        x_, y_ = shape_func(seed_points, frame_idx, scale=self.scale + 0.9)
        x_2, y_2 = self.shrink(x_, y_, halo_ratio, offset=int(6 + 15 * abs(cy)), dist_func="norm")
        x_2, y_2 = delete_points(x_2, y_2, 20, 0.5)
        x = np.concatenate((x, x_2), 0)
        y = np.concatenate((y, y_2), 0)

        # 膨胀光晕
        x_3, y_3 = shape_func(np.linspace(0, 2 * pi, int(points_num * .4)),
                                             frame_idx, scale=self.scale + 0.2)
        x_3, y_3 = self.shrink(x_3, y_3, ratio * 2, offset=6)
        x = np.concatenate((x, x_3), 0)
        y = np.concatenate((y, y_3), 0)

        halo_len = x_1.shape[0] + x_2.shape[0] + x_3.shape[0]
        p_size = np.random.choice([1, 2, 3], halo_len, replace=True, p=[0.7, 0.2, 0.1])
        point_size = np.concatenate((point_size, p_size), 0)
        tag_ = np.ones(halo_len) * 2 * 3
        tag = np.concatenate((tag, tag_), 0)

        x_y = np.around(np.stack([x, y], axis=1), 0)
        x, y = x_y[:, 0], x_y[:, 1]
        return x, y, point_size, tag

    def get_frames(self, shape_func):
        for frame_idx in range(frame_num):
            np.random.seed(self.seed_num)
            self.frame_points.append(self.gen_points(self.seed_points_num, frame_idx, shape_func))

        frames = []

        def add_points(frame, x, y, size, tag):
            # white = np.array([255, 255, 255], dtype='uint8')
            # dark_red = np.array([250, 90, 90], dtype='uint8')
            purple = np.array([180, 87, 200], dtype='uint8')  # 180, 87, 200
            light_pink = np.array([228, 140, 140], dtype='uint8')   # [228, 140, 140]
            rose_pink = np.array([228, 100, 100], dtype='uint8')

            x, y = x.astype(int), y.astype(int)
            frame[y, x] = rose_pink

            size_2 = np.int64(size == 2)
            frame[y, x + size_2] = rose_pink
            frame[y + size_2, x] = rose_pink

            size_3 = np.int64(size == 3)
            frame[y + size_3, x] = rose_pink
            frame[y - size_3, x] = rose_pink
            frame[y, x + size_3] = rose_pink
            frame[y, x - size_3] = rose_pink
            frame[y + size_3, x + size_3] = rose_pink
            frame[y - size_3, x - size_3] = rose_pink
            # frame[y - size_3, x + size_3] = color
            # frame[y + size_3, x - size_3] = color

            # 高光
            random_sample = np.random.choice([1, 0], size=tag.shape, p=[0.3, 0.7])

            # tag2_size1 = np.int64((tag <= 2) & (size == 1) & (random_sample == 1))
            # frame[y * tag2_size1, x * tag2_size1] = light_pink

            tag2_size2 = np.int64((tag <= 2) & (size == 2) & (random_sample == 1))
            frame[y * tag2_size2, x * tag2_size2] = purple
            # frame[y * tag2_size2, (x + 1) * tag2_size2] = light_pink
            # frame[(y + 1) * tag2_size2, x * tag2_size2] = light_pink
            frame[(y + 1) * tag2_size2, (x + 1) * tag2_size2] = light_pink

            # frame[y * tag2_size2, x * tag2_size2] = light_pink
            # frame[y, x + tag2_size2] = light_pink
            # frame[y + tag2_size2, x] = light_pink
            # frame[y + tag2_size2, x + tag2_size2] = light_pink

        for x, y, size, tag in self.frame_points:
            frame = np.zeros([self.frame_height, self.frame_width, 3], dtype="uint8")
            add_points(frame, x, y, size, tag)
            frames.append(frame)

        return frames

    def draw(self, wait, shape_func):
        frames = self.get_frames(shape_func)
        while True:
            for frame in frames:
                show_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                show_frame = cv2.resize(show_frame, (self.frame_width, self.frame_height))
                cv2.imshow("Love U", show_frame)
                cv2.waitKey(wait)


if __name__ == '__main__':
    period_time = 1000 * 1.5  # 1.5s一个周期
    frame_num = 30
    wait = int(period_time / frame_num)
    heart = HeartSignal(frame_num=frame_num, seed_points_num=2000, seed_num=5201314, frame_width=720, frame_height=640, scale=10.1)
    heart.draw(wait, heart.heart_function)

    # # 蝴蝶，取消下面两行注释，注释掉上面两行
    # heart = HeartSignal(frame_num=frame_num, seed_points_num=2000, seed_num=5201314, frame_width=800, frame_height=720,
    #                     scale=60)
    # heart.draw(wait, heart.butterfly_function)
    pass