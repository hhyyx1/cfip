import os
import requests
import pandas as pd
from tqdm import tqdm
from time import sleep

def get_ip_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        ips = [line.strip() for line in f]
    return ips

def ipinfoapi(ips:list, session):
    url = 'http://ip-api.com/batch'
    ips_dict = [{'query': ip, "fields": "city,country,countryCode,isp,org,as,query"} for ip in ips]
    sleep(30)
    try:
        with session.post(url, json=ips_dict) as resp:
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f'获取ip信息失败: {resp.status_code}, {resp.reason}')
                return None
    except Exception as e:
        print(f'requests error:{e}')
        return None

def get_ip_info(ips):
    ipsinfo = []
    url = 'http://ip-api.com/batch'
    
    with tqdm(total=len(ips)) as bar:
        bar.set_description(f"Processed IP: {len(ips)}")
        with requests.Session() as session:
            for i in range(0, len(ips), 100):
                t = ipinfoapi(ips[i:i + 100], session)
                if t is not None:
                    ipsinfo += t
                bar.update(min(100, len(ips) - i))

    return ipsinfo

def gatherip(port):
    cfiplistDir = "./ips/"
    allips = []

    # 遍历 ./ips/ 下的所有子目录
    for subdir in os.listdir(cfiplistDir):
        subdir_path = os.path.join(cfiplistDir, subdir)
        if os.path.isdir(subdir_path):
            # 遍历子目录里的所有 txt 文件
            for file in os.listdir(subdir_path):
                if file.endswith(".txt"):
                    filepath = os.path.join(subdir_path, file)
                    allips += get_ip_from_file(filepath)

    return list(set(allips))

def process_ipinfo(ipinfo, port):
    save_dir = f"./ip{port}/"

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    grouped = pd.DataFrame(ipinfo).groupby('countryCode')
    for countryCode, group in grouped:
        only_ip = group['query'].drop_duplicates()
        only_ip.to_csv(os.path.join(save_dir, countryCode + '.txt'), header=None, index=False)

def main(port):
    ips = gatherip(port)
    print(f"Total ips: {len(ips)}")
    ipinfo = get_ip_info(ips)
    process_ipinfo(ipinfo, port)

if __name__ == "__main__":
    main(443)
    print("Done!")
