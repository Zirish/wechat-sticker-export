import os
import re
import requests
import filetype
import glob
import logging
import argparse

# 配置日志记录
def setup_logging(log_file):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file, filemode='a')

# 提取文件中的链接
def extract_links(archive_path):
    links = []
    try:
        with open(archive_path, "rb") as file:
            content = file.read().decode("latin1")
            links = [re.sub(r"(bizid=\d+).*", r"\1", link) for link in re.findall(r"https?://[^\s]+", content)]
    except OSError as e:
        logging.error(f"未能打开文件 {archive_path}：{e}")
    except UnicodeDecodeError as e:
        logging.error(f"未能解析文件 {archive_path}：{e}")
    return links

# 下载图片并保存到指定文件夹
def download_images(links, output_folder, timeout):
    os.makedirs(output_folder, exist_ok=True)
    with requests.Session() as session:
        for index, link in enumerate(links):
            try:
                response = session.get(link.strip(), timeout=timeout)
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

def main():
    parser = argparse.ArgumentParser(description="Wechat Sticker Exporter")
    parser.add_argument("--list", action="store_true", help="create a list of download links")
    parser.add_argument("--dry", action="store_true", help="only list download links without downloading images")
    parser.add_argument("--output", type=str, default="downloaded_images", help="specify the output folder for downloaded images. Default is downloaded_images")
    parser.add_argument("--timeout", type=int, default=None, help="specify the timeout for downloading images. Default is None")
    parser.add_argument("--log", type=str, default="wechat_sticker_export.log", help="specify the log file. Default is wechat_sticker_export.log")
    args = parser.parse_args()

    setup_logging(args.log)

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
            download_images(all_links, args.output, args.timeout if args.timeout else None)

if __name__ == "__main__":
    main()