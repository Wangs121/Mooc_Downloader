# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 20:01:11 2021

@author: 27766
"""


import os
import requests
import subprocess
from Mooc.Mooc_Config import *

#next(实例)调用，调用一次变为下一次的值
def make_sum():
    ts_num = 0
    while True:
        yield ts_num
        ts_num += 1


class M3u8Download:
    """
    :param url: 完整的m3u8文件链接 如"https://www.bilibili.com/example/index.m3u8"
    :param name: 保存m3u8的文件名 如"index"
    :param num_retries: 重试次数
    """
    
    def __init__(self, url, name, lessonDir, num_retries=5):
        self._url = url
        self._name = name
        self._num_retries = num_retries
        self._lessonDir = os.path.join(lessonDir, self._name)
        self._file_path = os.path.join(os.getcwd(), self._name)
        self._front_url = None
        self._ts_url_list = []
        self._success_sum = 0
        self._ts_sum = 0
        self._headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
        self.aria2_path = os.path.join(os.getcwd(), "Mooc\\aria2c.exe")
        self.aria2c_cmd = '%s -x 16 -s 64 -j 64 -k 2M --disk-cache 4M  "{url:}" -d "{dirname:}" -o "{filename:}" --user-agent=Chrome'%(self.aria2_path)
        requests.packages.urllib3.disable_warnings()
        if not os.path.exists(self._lessonDir+'.mp4'):
            self.get_m3u8_info(self._url, self._num_retries)
            print('Downloading', self._name) 
    
            for k, ts_url in enumerate(self._ts_url_list):
                self.download_ts( ts_url, self._file_path, str(k) )
            if self._success_sum == self._ts_sum:
                self.output_mp4()
        print('\r  |-['+LENGTH*'*'+'] {:.0f}%'.format(100),end='  (完成)    \n')
        print("  |-{}  [mp4] 已经成功下载！".format(self.align(self._name,LENGTH)))

    def get_m3u8_info(self, m3u8_url, num_retries):
        """
        获取m3u8信息
        """
        try:
            res = requests.get(m3u8_url, timeout=(3, 30), verify=False, headers=self._headers)
            self._front_url = res.url.split(res.request.path_url)[0]

            m3u8_text_str = res.text
            self.get_ts_url(m3u8_text_str)
        except Exception as e:
            print(e)
            if num_retries > 0:
                self.get_m3u8_info(m3u8_url, num_retries - 1)

    def get_ts_url(self, m3u8_text_str):
        """
        获取每一个ts文件的链接
        """
        if not os.path.exists(self._file_path):
            os.mkdir(self._file_path)
        new_m3u8_str = ''
        ts = make_sum()
        for line in m3u8_text_str.split('\n'):
            if "#" in line:

                new_m3u8_str += f'{line}\n'
                if "EXT-X-ENDLIST" in line:
                    break
            else:
                new_m3u8_str += f"./{self._name}/{next(ts)}\n"
                
                #获取链接头
                #url.rsplit("/", 1)[0]
                self._ts_url_list.append(self._url.rsplit("/", 1)[0] + '/' + line)
        self._ts_sum = next(ts)
        with open(self._file_path + '.m3u8', "w") as f:
            f.write(new_m3u8_str)

    def download_ts(self, ts_url, dirname, filename):
        """
        下载 .ts 文件
        """
        cnt = 0
        abspath = os.path.join(dirname, filename)
       
        percent = float(self._success_sum/self._ts_sum)
        per = min(int(LENGTH*percent) , LENGTH)
        print('\r  |-['+per*'*'+(LENGTH-per)*'.'+'] {:.0f}%'.format(percent*100),end=' (ctrl+c中断)')
        if not os.path.exists(abspath):
            while cnt < self._num_retries:
                try:
                    
                    cmd = self.aria2c_cmd.format(url = ts_url, dirname = dirname, filename = filename)
                    #
                    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True, encoding='utf8')
                    while p.poll()is None:
                        
                        pass
                        #print('\r  [{:d}/ {:d}]\t'.format( self._success_sum ,self._ts_sum),end='')
                        
                    if p.returncode != 0:
                        cnt += 1
                        self.clear_file(filename)
                        print("Err"+filename)
                    else:
                        
                        #print("success_sum += 1")
                        self._success_sum += 1
                        return

                finally:
                    p.kill()
        else:
            #print("success_sum += 1")
            self._success_sum += 1

    def output_mp4(self):
        """
        合并.ts文件，输出mp4格式视频，需要ffmpeg
        """
        cmd = f"{os.getcwd()}\\Mooc\\ffmpeg -allowed_extensions ALL -i {self._file_path}.m3u8 -acodec \
        copy -vcodec copy -loglevel quiet -f mp4 {self._lessonDir}.mp4"
        os.system(cmd)
        file = os.listdir(self._file_path)
        for item in file:
            self.clear_file(item)
        os.removedirs(self._file_path)
        os.remove(self._file_path + '.m3u8')
        print(f"Download successfully --> {self._name}")
        
    def clear_file(self, filename):
        os.remove(os.path.join(self._file_path, filename))
        
    def align(self, string, width):  #  对齐汉字字符窜，同时截断多余输出
        '''
        align(string, width) 根据width宽度居中对齐字符窜 string，主要用于汉字居中
        '''
        res = ""
        size = 0
        for ch in string:
            if (size+3 > width):
                break
            size += 1 if ord(ch) <= 127 else 2
            res += ch
        res += (width-size)*' '
        return res