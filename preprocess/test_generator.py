#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 25.4.21
"""

import cv2
import os
import sys

from multiprocessing.pool import Pool
from urllib import parse

p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.append(p)

from myutils.project_utils import *
from myutils.cv_utils import *
from x_utils.vpf_utils import get_ocr_trt_dev_service, get_ocr_trt_service_new
from root_dir import DATA_DIR


class TestGenerator(object):
    def __init__(self):
        # self.grades = ["七", "八", "九"]
        # folder_format = "5-3语文-初中同步作文-{}年级"
        # grades_folder_name = "5-3语文-初中同步作文"

        # self.grades = ["三", "四", "五", "六"]
        # folder_format = "同步作文{}年级"
        # grades_folder_name = "同步作文"

        self.grades = ["三", "四", "五", "六"]
        folder_format = "小学生开心同步作文{}年级下册"
        grades_folder_name = "小学生开心同步作文下册"

        # self.grades = ["三", "四", "五", "六", "七"]
        # folder_format = "小学语文同步作文{}年级下册"
        # grades_folder_name = "小学语文同步作文下册"

        self.out_folder = os.path.join(DATA_DIR, "essay_prelabel", grades_folder_name)
        mkdir_if_not_exist(self.out_folder)

        self.num_dict = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}

        self.folder_list = [folder_format.format(g) for g in self.grades]
        self.in_folder = os.path.join(DATA_DIR, 'essay')
        self.url_format = "https://sm-transfer.oss-cn-hangzhou.aliyuncs.com/zhengsheng.wcl/essay-library/" \
                          "datasets/20210420/essay/{}/{}/{}"

    def process(self):
        paths_list, names_list = traverse_dir_files(self.in_folder)
        print('[Info] 处理文件夹: {}'.format(self.in_folder))
        print('[Info] 文件数: {}'.format(len(paths_list)))

        count = 0
        for path, name in zip(paths_list, names_list):
            items = path.split('/')
            img_name = items[-1]
            type_name = items[-2]
            book_name = items[-3]

            if type_name != "questions":
                continue

            if book_name in self.folder_list:
                grade = -1
                for g in self.grades:
                    if g in book_name:
                        grade = self.num_dict[g]
                if grade < 0:
                    continue
                out_path = os.path.join(self.out_folder, "{}_{}_{}".format(grade, type_name, img_name))
                shutil.copy(path, out_path)
                count += 1
        print('[Info] num: {}'.format(count))

    @staticmethod
    def rename_files():
        folder_name = os.path.join(DATA_DIR, 'essay_prelabel_txt')
        paths_list, names_list = traverse_dir_files(folder_name)
        for path, name in zip(paths_list, names_list):
            out_file = path.split('.')[0] + ".out.txt"
            out_path = os.path.join(folder_name, out_file)
            data_lines = read_file(path)

            parsed_list = []
            for data_line in data_lines:
                x_name = data_line.split('/')[-2]
                parsed_name = parse.quote(x_name)
                parsed_line = data_line.replace(x_name, parsed_name)
                parsed_list.append(parsed_line)
            write_list_to_file(out_path, parsed_list)

        print('[Info] 处理完成!')


def main():
    tg = TestGenerator()
    # tg.process()
    tg.rename_files()


if __name__ == '__main__':
    main()
