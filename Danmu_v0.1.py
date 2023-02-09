# -*- coding = utf-8 -*-
# @Time :2023/1/17 11:45
# @Author : 王俊庆
# @File : Danmu_v0.1.py
# @Software : PyCharm

import requests
import re
import os

# 格式默认为1
style = 1
font_size = 25
default_num = 16777215
MarginL, MarginR, MarginV = 0, 0, 0

# xml字幕示例
# <d p="24,1,25,16777215,0,0,0,76561198068208329">与长安汽车一起追番</d>
# Time_line = []
# Content_total = []
# User_id = []

headers = {
    'referer': 'https://v.qq.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.52'
}

proxies = {
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809'
}


def get_time_duration(url):
    vid = url.split('/')[-1].split('.')[0]
    resp = requests.get(url, headers=headers, proxies=proxies)
    mask = re.compile(f'"vid":"{vid}","lid":undefined,"duration":"(.*?)"')
    result = re.findall(mask, resp.text)[0]
    # print(result)
    return vid, result
def get_video_title(time_duration,url):
    resp = requests.get(url,headers=headers,proxies=proxies)
    mask = re.compile(f'"duration":"{time_duration}","playTitle":"(.*?)"')
    result = re.findall(mask, resp.text)[0]
    # print(result)
    return result

def calculate_time_total(time_format):
    time = time_format.split(':')
    if len(time) == 2:
        time_total = int(time[0]) * 60 + int(time[1])
        # print(time_total)
        return time_total

def alter(file, old_str, new_str):
    """
    将替换的字符串写到一个新的文件中，然后将原文件删除，新文件改为原来文件的名字
    :param file: 文件路径
    :param old_str: 需要替换的字符串
    :param new_str: 替换的字符串
    :return: None
    """
    with open(file, "r", encoding="utf-8") as f1, open("%s.bak" % file, "w", encoding="utf-8") as f2:
        for line in f1:
            if old_str in line:
                line = line.replace(old_str, new_str)
            f2.write(line)
    os.remove(file)
    os.rename("%s.bak" % file, file)


def get_Danmu(url, f, num):
    resp = requests.get(url, headers=headers, proxies=proxies)

    json_data = resp.json()
    # print(len(json_data['barrage_list']))
    danmu_list = json_data['barrage_list']

    string_bad = "@#$%^&_+/\/"
    for item in danmu_list:
        time_offset = item['time_offset']
        content = item['content']
        content = content.replace('<', '《')
        content = content.replace('>', '》')
        for string in string_bad:
            if string in content:
                # print(string)
                content = content.replace(string, ' ')
        id = item['id']

        time_format = int(eval(time_offset) / 1000)

        f.write(
            f'\t<d p="{time_format},{style},{font_size},{default_num},{MarginL},{MarginR},{MarginV},{id}">{content}</d>\n')
        num += 1

    return num

    # Time_line.append(time_offset)
    # Content_total.append(content)
    # User_id.append(id)

    # print(Time_line, Content_total, User_id)


if __name__ == '__main__':
    # url = 'https://v.qq.com/x/cover/mzc002007knmh3g/s00453h4di9.html'
    url = input("请输入视频网址：")
    vid, time_format = get_time_duration(url)
    print(f"视频ID:{vid}", f'视频时长:{time_format}')
    time_total = calculate_time_total(time_format)
    print(f'视频共有{time_total}秒')
    video_title = get_video_title(time_format,url)
    print(f'开始爬取{video_title}实时弹幕')
    epoch = int(time_total / 30)
    danmu_num = 0
    file_name = video_title + '.xml'
    with open(file_name, 'w', encoding='utf-8')as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<i>\n')
        f.write('\t<chatserver>wjq_self_spider</chatserver>\n')
        f.write('\t<chatid>LZU_physic_wjq</chatid>\n')
        f.write('\t<count>danmu_Total_num</count>\n')
        print("正在爬取实时弹幕……")
        for i in range(epoch + 1):
            time_mask = i * 30 * 1000
            URL = f'https://dm.video.qq.com/barrage/segment/{vid}/t/v1/{time_mask}/{time_mask + 30000}'
            # print(URL)
            danmu_num = get_Danmu(URL, f, danmu_num)
        f.write('</i>')
    print(f"共有{danmu_num}条弹幕")
    alter(file_name, "danmu_Total_num", str(danmu_num))
    print('弹幕保存成功！')
