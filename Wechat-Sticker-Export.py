import os
import re
import requests
import filetype
import glob
import logging
import argparse

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='wechat_sticker_export.log', filemode='a')

# 提取文件中的链接
def extract_links(archive_path):
    links = []
    try:
        with open(archive_path, "rb") as file:
            content = file.read().decode("latin1")
            links = extract_links_from_content(content)
    except OSError as e:
        logging.error(f"未能打开文件 {archive_path}：{e}")
    except UnicodeDecodeError as e:
        logging.error(f"未能解析文件 {archive_path}：{e}")
    return links

# 从内容中提取链接
def extract_links_from_content(content):
    return [re.sub(r"(bizid=\d+).*", r"\1", link) for link in re.findall(r"https?://[^\s]+", content)]

# 下载图片并保存到指定文件夹
def download_images(links, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    with requests.Session() as session:
        for index, link in enumerate(links):
            try:
                response = session.get(link.strip(), timeout=10)
                response.raise_for_status()
                kind = filetype.guess(response.content)
                if kind:
                    file_path = os.path.join(output_folder, f"image_{index + 1}.{kind.extension}")
                    with open(file_path, "wb") as img_file:
                        img_file.write(response.content)
                else:
                    logging.error(f"无法检测链接 {index + 1} 的图片类型：{link}")
            except requests.RequestException as e:
                logging.error(f"下载 {link} 失败：{e}")

def print_help():
    print("Usage: python Wechat-Sticker-Export.py [--list] [--dry] [--help|-h]")
    print("  --list    将所有提取出的链接打印到 link.txt 中")
    print("  --dry     不执行下载图片的操作")
    print("  --help, -h 打印出接收的参数")

def main():
    parser = argparse.ArgumentParser(description="微信表情包导出工具")
    parser.add_argument("--list", action="store_true", help="将所有提取出的链接打印到 link.txt 中")
    parser.add_argument("--dry", action="store_true", help="不执行下载图片的操作")
    parser.add_argument("--help", "-h", action="help", help="打印出接收的参数")
    args = parser.parse_args()

    base_path = os.path.expanduser("~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/")
    archive_paths = glob.glob(os.path.join(base_path, "*/Stickers/fav.archive"))

    if not archive_paths:
        logging.error("没有找到存放表情包的文件夹")
        return

    all_links = [link for path in archive_paths for link in extract_links(path)]
    if all_links:
        logging.info(f"所有表情包已提取，共 {len(all_links)} 个")

        if args.list:
            with open("links.txt", "w") as file:
                for link in all_links:
                    file.write(link + "\n")
            logging.info("表情包下载链接已保存到 links.txt")

        if not args.dry:
            download_images(all_links, "downloaded_images")

if __name__ == "__main__":
    main()