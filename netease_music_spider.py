# github ID获取方法：api.github.com/users/自己的用户名

import os
import time
import requests
from lxml import etree
import PySimpleGUI as sg

# 定义请求头信息
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

def download_song(song_url, music_name, output_dir):
    try:
        # 发送请求下载音乐数据
        response = requests.get(song_url, headers=headers, timeout=10)
        response.raise_for_status()  # 如果响应状态不是 200，抛出异常

        # 将音乐保存为 MP3 文件
        with open(os.path.join(output_dir, f'{music_name}.mp3'), 'wb') as file:
            file.write(response.content)

        print(f'《{music_name}》 下载成功')
        return True

    except requests.exceptions.RequestException as e:
        print(f"下载歌曲时出错: {e}")
        return False

def download_songs_from_playlist(playlist_url, output_dir):
    try:
        # 发送请求获取歌单页面内容
        response = requests.get(playlist_url, headers=headers, timeout=10)
        response.raise_for_status()  # 如果响应状态不是 200，抛出异常

        # 使用 lxml 解析 HTML
        html = etree.HTML(response.text)

        # 提取歌曲链接和名称
        music_label_list = html.xpath('//ul[@class="f-hide"]/li/a')

        # 如果输出目录不存在，则创建
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 遍历歌曲链接列表并下载
        for music_label in music_label_list:
            music_id = music_label.xpath('./@href')[0].split('=')[-1]
            music_name = music_label.xpath('./text()')[0]  # 提取歌曲名称

            # 构建下载链接
            song_download_url = f'http://music.163.com/song/media/outer/url?id={music_id}'

            # 下载歌曲
            download_song(song_download_url, music_name, output_dir)

            # 下载一首歌后延时1秒
            time.sleep(1)

    except requests.exceptions.RequestException as e:
        print(f"下载歌曲时出错: {e}")

def download_single_song(song_url, output_dir):
    try:
        # 提取音乐ID和名称
        music_id = song_url.split('=')[-1]
        song_info_url = f'http://music.163.com/api/song/detail/?id={music_id}&ids=[{music_id}]'
        response = requests.get(song_info_url, headers=headers, timeout=10)
        response.raise_for_status()
        song_info = response.json()
        music_name = song_info['songs'][0]['name']

        # 构建下载链接
        song_download_url = f'http://music.163.com/song/media/outer/url?id={music_id}'

        # 下载歌曲
        download_song(song_download_url, music_name, output_dir)

    except requests.exceptions.RequestException as e:
        print(f"下载单首歌曲时出错: {e}")

def main():
    # 定义 GUI 界面布局
    layout = [
        [sg.Text('请输入网易云音乐歌单链接:', size=(30, 1)), sg.InputText(key='playlist_url')],
        [sg.Text('请输入单首音乐链接:', size=(30, 1)), sg.InputText(key='song_url')],
        [sg.Text('选择保存目录:', size=(30, 1)), sg.InputText(key='output_dir'), sg.FolderBrowse(button_text='浏览')],
        [sg.Button('下载歌单', size=(10, 1)), sg.Button('下载单曲', size=(10, 1)), sg.Button('退出', size=(10, 1))]
    ]

    # 创建 GUI 窗口
    window = sg.Window('网易云音乐下载器', layout)

    # 事件循环，处理 GUI 事件和获取输入值
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == '退出':
            break
        elif event == '下载歌单':
            playlist_url = values['playlist_url']
            output_dir = values['output_dir']

            if not playlist_url:
                sg.popup_error('请输入有效的歌单链接.')
                continue
            if not output_dir:
                sg.popup_error('请选择保存目录.')
                continue

            # 调用函数下载歌单
            download_songs_from_playlist(playlist_url, output_dir)
            sg.popup('下载歌单完成!', keep_on_top=True)

        elif event == '下载单曲':
            song_url = values['song_url']
            output_dir = values['output_dir']

            if not song_url:
                sg.popup_error('请输入有效的歌曲链接.')
                continue
            if not output_dir:
                sg.popup_error('请选择保存目录.')
                continue

            # 调用函数下载单曲
            download_single_song(song_url, output_dir)
            sg.popup('下载单曲完成!', keep_on_top=True)

    window.close()

if __name__ == "__main__":
    main()
