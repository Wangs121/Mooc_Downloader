'''
    www.icourse163.org 下所有免费课程的下载和解析
'''

import os
import re
import requests
if __package__ is None:
    import sys
    sys.path.append('..\\')
    sys.path.append("..\\..\\")
from Mooc.Mooc_Config import *
from Mooc.Mooc_Base import *
from Mooc.Mooc_Download import *
from Mooc.m3u8_Download import *
from Mooc.Mooc_Request import *
from Mooc.Mooc_Potplayer import *
from Mooc.Icourse163.Icourse163_Config import * 
from Mooc.Icourse163.Icourse163_Base import *

__all__ = [
    "Icourse163_Mooc"
]

class Icourse163_Mooc(Icourse163_Base):
    course_url = "https://www.icourse163.org/course/"
    infos_url = 'https://www.icourse163.org/dwr/call/plaincall/CourseBean.getMocTermDto.dwr'
    parse_url = 'https://www.icourse163.org/dwr/call/plaincall/CourseBean.getLessonUnitLearnVo.dwr'
    csrf_url = None
    m3u8_url_head = 'https://vod.study.163.com/eds/api/v1/vod/video?videoId='
    
    infos_data = {
        'callCount':'1', 
        'scriptSessionId':'${scriptSessionId}190', 
        'c0-scriptName':'CourseBean',
        'c0-methodName':'getMocTermDto', 
        'c0-id':'0', 
        'c0-param0':None,  # 'number:'+self.term_id,
        'c0-param1':'number:0', 
        'c0-param2':'boolean:true', 
        'batchId':'1543633161622'
    }
    parse_data = {
        'callCount': '1', 
        'scriptSessionId': '${scriptSessionId}190',
        'c0-scriptName':'CourseBean',
        'c0-methodName':'getLessonUnitLearnVo', 
        #'httpSessionId':'5531d06316b34b9486a6891710115ebc',
        'httpSessionId' : None,
        'c0-id': '0', 
        'c0-param0':None, #'number:'+meta[0],
        'c0-param1':None, #'number:'+meta[1], 
        #'c0-param1':'number:1',
        'c0-param2':'number:0',
        'c0-param3':None, #'number:'+meta[2], 
        'batchId': '1543633161622'
        #'batchId': '1609820564913'
    }
    
    m3u8_data = {
        'bizId' : None,
        'bizType' : '1',
        'contentType' : '1'
        }
    
    def __init__(self, mode=IS_SHD):
        super().__init__()
        self.mode = mode
        self.c = requests.session()
        g = self.c.get(self.course_url)
        self.csrfToken = g.cookies['NTESSTUDYSI']
        self.parse_data['httpSessionId'] = self.csrfToken
        self.csrf_url = 'https://www.icourse163.org/web/j/resourceRpcBean.getResourceToken.rpc?csrfKey=' + self.csrfToken
        
        

    def _get_cid(self, url):
        self.cid = None
        match = courses_re['icourse163_mooc'].match(url)
        if match and match.group(4):
            self.cid = match.group(4)

    def _get_title(self):
        if self.cid is None:
            return
        self.title = self.term_id = None
        url = self.course_url + self.cid
        text = request_get(url)
        match = re.search(r'termId : "(\d+)"', text)
        if match:
            self.term_id = match.group(1)
        names = re.findall(r'name:"(.+)"', text)
        if names:
            title = '__'.join(names)
            self.title = winre.sub('', title)[:WIN_LENGTH] # 用于除去win文件非法字符

    def _get_infos(self):
        if self.term_id is None:
            return
        self.infos = {}
        self.infos_data['c0-param0'] = 'number:'+self.term_id
        text = request_post(self.infos_url, self.infos_data, decoding='unicode_escape')
        chapters = re.findall(r'homeworks=\w+;.+?id=(\d+).+?name="((.|\n)+?)";',text)
        for i,chapter in enumerate(chapters,1):
            chapter_title = winre.sub('', '{'+str(i)+'}--'+chapter[1])[:WIN_LENGTH]
            self.infos[chapter_title] = {}
            lessons = re.findall(r'chapterId='+chapter[0]+r'.+?contentType=1.+?id=(\d+).+?isTestChecked=false.+?name="((.|\n)+?)".+?test', text)
            for j,lesson in enumerate(lessons,1):
                lesson_title = winre.sub('', '{'+str(j)+'}--'+lesson[1])[:WIN_LENGTH]
                self.infos[chapter_title][lesson_title] = {}
                videos = re.findall(r'contentId=(\d+).+contentType=(1).+id=(\d+).+lessonId=' +
                                lesson[0] + r'.+name="(.+)"', text)
                pdfs = re.findall(r'contentId=(\d+).+contentType=(3).+id=(\d+).+lessonId=' +
                                lesson[0] + r'.+name="(.+)"', text)
                video_source = [{'params':video[:3], 'name':winre.sub('','[{}.{}.{}]--{}'.format(i,j,k,video[3])).rstrip('.mp4')[:WIN_LENGTH]} for k,video in enumerate(videos,1)]
                pdf_source = [{'params':pdf[:3], 'name':winre.sub('','({}.{}.{})--{}'.format(i,j,k,pdf[3])).rstrip('.pdf')[:WIN_LENGTH]} for k,pdf in enumerate(pdfs,1)]
                self.infos[chapter_title][lesson_title]['videos'] = video_source
                self.infos[chapter_title][lesson_title]['pdfs'] = pdf_source

    def _get_source_text(self, params):
        self.parse_data['c0-param0'] = params[0]
        self.parse_data['c0-param1'] = params[1]
        self.parse_data['c0-param3'] = params[2]
        self.m3u8_data['bizId'] = params[2]
        text = request_post(self.parse_url, self.parse_data, decoding='unicode_escape')
        return text

    def _get_pdf_url(self, params):
        text = self._get_source_text(params)
        pdf_match = re.search(r'textOrigUrl:"(.*?)"', text)
        pdf_url = None
        if pdf_match:
            pdf_url = pdf_match.group(1)
        return pdf_url

    def _get_video_url(self, params):
        text = self._get_source_text(params)
        sub_match = re.search(r'name=".+";.*url="(.*?)"', text)
        video_url = sub_url = None
        is_mp4 = True
        if sub_match:
            sub_url = sub_match.group(1)
        resolutions = ['Shd', 'Hd', 'Sd']
        for index, sp in enumerate(resolutions,1):
            video_match = re.search(r'(?P<ext>mp4)%sUrl="(?P<url>.*?\.(?P=ext).*?)"' % sp, text)
            if video_match:
                video_url, _ = video_match.group('url', 'ext')
                if index >= self.mode: break
        #无mp4格式
        if not video_url:
           is_mp4 = False
           #print("csrf_url" + self.csrf_url)
           signiture_raw = self.c.post(self.csrf_url, data = self.m3u8_data)
           #print("signiture_raw" + signiture_raw.text)
           signiture = re.search(r'"signature":"(\w+)"', signiture_raw.text).group(1)
           #print("signiture" + signiture)
           m3u8_post_url = self.m3u8_url_head + params[0] + '&signature=' + signiture + '&clientType=1'
           #print("m3u8_post_url" + m3u8_post_url)
           m3u8_inf0 = self.c.get(m3u8_post_url)
           #print("m3u8_inf0" + m3u8_inf0.text)
           video_url_all = re.search(r'"videos":\[(.+)]',m3u8_inf0.text).group(1)
           #print("video_url_all" + video_url_all)
           video_urls = re.search(r'"videoUrl":"(?P<Sd>.+?).m3u8?(.*?)"videoUrl":"(?P<Hd>.+?).m3u8',video_url_all)
           #video_url = video_urls.group(1) + '.m3u8'
           if self.mode == 3 :
               video_url = video_urls.group('Sd') + '.m3u8'
           else:
               video_url = video_urls.group('Hd') + '.m3u8'
        return video_url, sub_url, is_mp4
    

    def _download(self):  # 根据课程视频链接来下载高清MP4慕课视频, 成功下载完毕返回 True
        print('\n{:^{}s}'.format(self.title, LEN_S))
        self.rootDir = rootDir = os.path.join(PATH, self.title)
        courseDir = os.path.join(rootDir, COURSENAME)
        if not os.path.exists(courseDir):
            os.makedirs(courseDir)
        Icourse163_Base.potplayer.init(rootDir)
        Icourse163_Base.potplayer.enable()
        for i,chapter in enumerate(self.infos,1):  # 去除 win 文价夹中的非法字符
            print(chapter)
            chapterDir = os.path.join(courseDir, chapter)
            if not os.path.exists(chapterDir):
                os.mkdir(chapterDir)
            for j,lesson in enumerate(self.infos[chapter],1):
                lessonDir = os.path.join(chapterDir, lesson)
                if not os.path.exists(lessonDir):
                    os.mkdir(lessonDir)
                print("  "+lesson)
                sources = self.infos[chapter][lesson]
                for k,pdf_source in enumerate(sources['pdfs'],1):
                    params, pdf_name = pdf_source['params'], pdf_source['name']
                    pdf_url= self._get_pdf_url(params)
                    if pdf_url:
                        self.download_pdf(pdf_url, pdf_name, lessonDir)
                if self.mode == ONLY_PDF:
                    continue           
                for k,video_source in enumerate(sources['videos'],1):
                    params, name = video_source['params'], video_source['name']
                    video_name = sub_name = name
                    video_url, sub_url, is_mp4 = self._get_video_url(params)
                    if is_mp4:
                        #print(video_url)
                        self.download_video(video_url=video_url, video_name=video_name, video_dir=lessonDir)
                    else:   
                        print(video_name + " 无mp4资源，正在下载m3u8格式")
                        M3u8Download(video_url, video_name, lessonDir)
                    if sub_url:
                        self.download_sub(sub_url, sub_name, lessonDir)

    def prepare(self, url):
        self._get_cid(url)
        self._get_title()
        self._get_infos()

    def download(self):
        if self.cid and self.title and self.term_id and self.infos:
            self._download()
            return True
        return False


def main():
    # url = 'http://www.icourse163.org/course/GDUFS-1002493010'
    # url = 'https://www.icourse163.org/course/WHU-1001539003'
    url = 'https://www.icourse163.org/course/XHDX-1205600803'
    icourse163_mooc = Icourse163_Mooc()
    if (icourse163_mooc.set_mode()):
        icourse163_mooc.prepare(url)
        icourse163_mooc.download()

if __name__ == '__main__':
    main()
