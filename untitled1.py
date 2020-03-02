import requests
import re


def star(url):
    url2 = "https://api.bilibili.com/x/player/playurl?avid={avid}&cid={cid}&qn=32&type=&otype=json"
    headers2 = {
        "host": "",
        "Referer": "https://www.bilibili.com",
        "User-Agent": "Mozilla/5.0(Windows NT 10.0;WOW64) AppleWebKit/537.36(KHTML,likeGecko)Chrome/63.0.3239.132Safari/537.36"
    }

    avid = re.findall("video/av(.+)\?", url)
    # print(avid)
    avid = re.findall("^[1-9]\d*|0$", avid[0])
    # print(avid)
    cid, name = get_cid(avid[0])
    print(name, end=" ")
    flv_url, size = get_flvurl(url2.format(avid=avid[0], cid=cid))
    shuju = size / 1024 / 1024
    print("视频大小为：%.2fM" % shuju)
    # print(flv_url)
    # print(size)
    h = re.findall("https://(.+)com", flv_url)
    # print(h)
    host = h[0] + "com"
    # print(host1)
    headers2["host"] = host
    # print(headers2)
    res = requests.get(flv_url, headers=headers2, stream=True, verify=False)
    # print(flv_url)
    save_movie(res, name)


def get_cid(aid):  # 获得cid
    header = {
        'host': 'api.bilibili.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
    }
    url = "https://api.bilibili.com/x/player/pagelist?aid={aid}&jsonp=jsonp".format(aid=aid)
    response = requests.get(url, headers=header).json()
    # print(response)
    # print("---------")
    return response["data"][0]["cid"], response["data"][0]["part"]


def get_flvurl(url):  # 获得视频真实flv地址
    header = {'host': 'api.bilibili.com',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}

    response = requests.get(url, headers=header).json()
    print(response)
    # print("=====")
    return response["data"]["durl"][0]["url"], response["data"]["durl"][0]["size"]


def save_movie(res, name):  # 保存视频
    chunk_size = 1024
    with open("{name}.flv".format(name=name), "wb") as f:
        for data in res.iter_content(1024):
            f.write(data)
    print(name + "已经下载完毕")


if __name__ == "__main__":
    url = "https://www.bilibili.com/video/av40226524/?spm_id_from=333.788.videocard.0"
    star(url)
