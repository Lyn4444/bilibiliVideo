import requests
import re
import json
import os


def validate_filename_in_windows(filename):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_name = re.sub(rstr, "_", filename)  # 替换为下划线
    return new_name


class Bilibili(object):
    def __init__(self, save_dir='.'):
        self.save_dir = save_dir
        self.session = requests.Session()
        self.cookies = None

    def set_cookies(self, cookies_str: str):
        self.cookies = cookies_str

    def set_save_dir(self, save_dir):
        self.save_dir = save_dir

    def get_video(self, aid):
        url = f'https://www.bilibili.com/video/av{aid}'
        r = self._get(url)
        title = re.findall(r'h1 title="([^"]+)"', r.text)[0]
        print(f'获取 {title}')
        info = self.extract_playinfo(r.text)
        self.save(aid, title, info)

    def extract_playinfo(self, text):
        pattern = '__playinfo__='
        pos = text.find(pattern)
        if pos == -1:
            return None
        i = pos + len(pattern)
        left = 0
        while True:
            if text[i] == '{':
                left += 1
            elif text[i] == '}':
                left -= 1
                if left == 0:
                    break
            i += 1
        return json.loads(text[pos+len(pattern):i+1])

    def save(self, aid, title, info: dict):
        video = sorted(info['data']['dash']['video'], key=lambda video: video['bandwidth'])[-1]
        audio = sorted(info['data']['dash']['audio'], key=lambda audio: audio['bandwidth'])[-1]
        quality = ''
        idx = -1
        for i in range(len(info['data']['accept_quality'])):
            if info['data']['accept_quality'][i] == video['id']:
                idx = i
                break
        if idx != -1 and idx < len(info['data']['accept_description']):
            quality = info['data']['accept_description'][idx].encode('unicode_escape').decode('unicode_escape')

        save_dir = os.path.join(self.save_dir, validate_filename_in_windows(f'{title}_{aid}_{quality}'))
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        tmp_file_save_dir = os.path.join(save_dir, 'tmp')
        if not os.path.exists(tmp_file_save_dir):
            os.makedirs(tmp_file_save_dir)

        output_filename = validate_filename_in_windows(f'{title}.mp4')
        output_path = os.path.join(save_dir, output_filename)
        if os.path.exists(output_path):
            print(f'文件已存在，跳过')
            return None

        video_filename = 'video-' + video['base_url'].split('?')[0].split('/')[-1]
        self.download(aid, video['segment_base']['initialization'], video['base_url'], tmp_file_save_dir, video_filename)

        audio_filename = 'audio-' + audio['base_url'].split('?')[0].split('/')[-1]
        self.download(aid, audio['segment_base']['initialization'], audio['base_url'], tmp_file_save_dir, audio_filename)

        os.system(f'ffmpeg -i "{os.path.join(tmp_file_save_dir, video_filename)}" -i "{os.path.join(tmp_file_save_dir, audio_filename)}" -c:v copy -c:a copy "{output_path}"')

        print(f'下载成功')

    def download(self, aid, initialization, url, save_dir, filename):
        savepath = os.path.join(save_dir, filename)
        if os.path.exists(savepath):
            print(f'文件 {savepath} 已存在，跳过')
            return

        headers = {
            'range': f'bytes={initialization}',
            'referer': f'https://www.bilibili.com/video/av{aid}'
        }
        r = self._get(url, headers=headers)
        total_size = int(r.headers['Content-Range'].split('/')[-1])
        headers['range'] = f'bytes=0-{total_size}'
        r = self._get(url, headers=headers)

        # percentage = lambda a, b: '%.2f' % ((float(a) / float(b)) * 100,)
        cur = 0
        chunk_size = 4096
        # print(f'[{percentage(cur, total_size)}] {cur} bytes / {total_size} bytes', end="\r")
        with open(savepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                cur += len(chunk)
                # print(f'[{percentage(cur, total_size)}] {cur} bytes / {total_size} bytes', end="\r")

    def _get(self, url, params={}, headers: dict = {}):
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
        headers['Origin'] = 'https://www.bilibili.com'
        if self.cookies is not None:
            headers['Cookie'] = self.cookies
        return self.session.get(url, params=params, headers=headers)


if __name__ == '__main__':
    aid = input("输入视频号：")
    b = Bilibili(save_dir='./downloads')
    b.set_cookies("")
    b.get_video(aid)
