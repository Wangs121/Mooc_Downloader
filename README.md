### 				基于Python 爬虫的慕课视频下载

#### 修改说明

* 修复了aria2c 错误代码 22

* 无限速

* 修复了不能下载视频的问题

* 增加了无mp4格式视频时下载m3u8格式视频并转换为mp4功能（ffmpeg）

  

##### 1.  项目简介：

- 项目环境为 Windows10,  Python3
- 用 Python3.6 urllib3 和requests模块爬虫
- 支持Mooc视频，字幕，课件下载，课程以目录树形式下载到硬盘，支持Potplayer播放
- 支持中国大学慕课和爱课程二大慕课网站的视频课程下载，核心下载调用 Aria2c
- 无mp4资源自动下载m3u8格式补充，使用ffmpeg自动转换为mp4**（增加内容）**
- 有关下载器的使用以及相关问题，点击查看[Mooc下载器帮助文档](https://github.com/PyJun/Mooc_Downloader/wiki)

##### 2. 功能演示：

![demo1.png](./图片/demo1.png)

![demo2.png](./图片/demo2.png)

##### 4.项目文件

- Mooc_Main.py	          整个项目的主程序,  其实是调用了 Mooc_Interface
- Mooc_Interface.py       人机交互接口模块
- Mooc_Config.py            Mooc 的配置文件
- Mooc_Base.py               Mooc  抽象基类
- Mooc_Potplayer.py       用于生成专用于 Potplayer 播放的 dpl 文件 
- Mooc_Request.py          用 urllib 包装的一个Mooc请求库
- Mooc_Download.py      调用 Aira2c 下载的命令接口
- m3u8_Download.py      下载m3u8视频
- Icourses                          有关爱课程的模块包
  - Icourse_Base.py              爱课程下载器的基类，继承自 Mooc_Base
  - Icourse_Config.py            配置文件
  - Icourse_Cuoc.py              爱课程视频公开课的下载的子类，http://www.icourses.cn/cuoc/
  - Icourse_Mooc.py             爱课程资源共享课的下载的子类，http://www.icourses.cn/mooc/
- Icourse163                      有关中国大学慕课的模块包
  - Icourse163_Base.py         中国大学慕课下载器的基类，继承自 Mooc_Base
  - Icourse163_Config.py       配置文件
  - Icourse163_Mooc.py        中国大学慕课下载器得子类，继承自 Icourse163_Base.py

##### 5.运行项目

请确保在项目工程的根目录下，然后在终端输入以下指令（python3 环境，无依赖的第三方模块）

```powershell
python -m Mooc
```

##### 6.打包指令

1. 首先确保已经安装 **pyinstaller**，若未安装，则用 pip 安装，打开终端，输入：

   ```powershell
   pip install pyinstaller
   ```

2. 然后在项目工程的根目录下，终端输入：

   ```powershell
   pyinstaller Mooc.spec
   ```

3. 最后会在项目工程根目录下出现一个**dist**文件夹，该文件夹会出现一个**Mooc-3.5.0_dev.exe**程序

