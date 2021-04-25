#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 23.4.21
"""

import os
import sys
import random
from urllib import parse

from myutils.project_utils import write_line, shuffle_two_list, read_file, create_file

p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.append(p)

from myutils.img_checker import traverse_dir_files
from root_dir import DATA_DIR
from x_utils.vpf_utils import get_problem_segment_service


class PsEvaluator(object):
    def __init__(self):
        self.in_folder = os.path.join(DATA_DIR, 'essay')
        self.out_file = os.path.join(DATA_DIR, 'essay-ps-out.v2.txt')
        self.html_file = os.path.join(DATA_DIR, 'essay-ps-out.v2.html')
        # self.error_file = os.path.join(DATA_DIR, 'essay-error.txt')
        self.url_format = "https://sm-transfer.oss-cn-hangzhou.aliyuncs.com/zhengsheng.wcl/essay-library/" \
                          "datasets/20210420/essay/{}/{}/{}"

    @staticmethod
    def call_service(url):
        """
        调用OCR服务
        img_url:
        https://sm-transfer.oss-cn-hangzhou.aliyuncs.com/zhengsheng.wcl/essay-library/datasets/20210420/essay/
        5-3%E8%AF%AD%E6%96%87-%E5%88%9D%E4%B8%AD%E5%90%8C%E6%AD%A5%E4%BD%9C%E6%96%87-%E4%B8%83%E5%B9%B4%E7%BA%A7/
        bookcover/page-0001.jpg
        """
        res_dict = get_problem_segment_service(img_url=url)
        print('[Info] url: {}'.format(url))
        oss_url = res_dict['data']['oss_url']
        return oss_url

    @staticmethod
    def make_html_page(html_file, imgs_path, n=1):
        header = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>MathJax TeX Test Page</title>
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script type="text/javascript" id="MathJax-script" async
          src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
        </script>
        <style>
        img{
            max-height:640px;
            max-width: 640px;
            vertical-align:middle;
        }
        </style>
        </head>
        <body>
        <table>
        """

        tail = """
        </table>
        </body>
        </html>
        """

        data_lines = read_file(imgs_path)
        print('[Info] 样本行数: {}'.format(len(data_lines)))
        urls_list = []  # url列表
        for data_line in data_lines:
            # urls = data_line.split("<sep>")
            urls = data_line.split(",")
            urls_list.append(urls)

        with open(html_file, 'w') as f:
            f.write(header)
            for idx, items in enumerate(urls_list):
                f.write('<tr>\n')
                f.write('<td>%d</td>\n' % ((idx / n)))
                for item in items:
                    f.write('<td>\n')
                    if item.startswith("http"):
                        f.write('<img src="%s" width="600">\n' % item)
                    else:
                        f.write('%s' % item)
                    f.write('</td>\n')
                f.write('</tr>\n')
            f.write(tail)

    @staticmethod
    def process_url(idx, img_url, out_file):
        """
        处理URL
        """
        oss_url = PsEvaluator.call_service(img_url)
        write_line(out_file, "{},{}".format(idx, oss_url))
        print('[Info] 处理完成: {} - {}'.format(idx, img_url))

    def process(self):
        paths_list, names_list = traverse_dir_files(self.in_folder)
        print('[Info] 处理文件夹: {}'.format(self.in_folder))
        print('[Info] 文件数: {}'.format(len(paths_list)))

        random.seed(47)
        paths_list, names_list = shuffle_two_list(paths_list, names_list)
        paths_list = paths_list[:100]
        names_list = names_list[:100]

        url_list = []
        for path, name in zip(paths_list, names_list):
            items = path.split('/')
            img_name = items[-1]
            clz_name = items[-2]
            book_name = parse.quote(items[-3])

            img_url = self.url_format.format(book_name, clz_name, img_name)
            url_list.append(img_url)
        print('[Info] img_url num: {}'.format(len(url_list)))

        for idx, img_url in enumerate(url_list):
            PsEvaluator.process_url(idx, img_url, self.out_file)

        print('[Info] 全部处理完成: {}'.format(self.out_file))

    def process_html(self):
        create_file(self.html_file)
        PsEvaluator.make_html_page(self.html_file, self.out_file, n=1)  # 生成URL
        print('[Info] 处理完成: {}'.format(self.html_file))

def main():
    pe = PsEvaluator()
    # pe.process()
    pe.process_html()


if __name__ == '__main__':
    main()
