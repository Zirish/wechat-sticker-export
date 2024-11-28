import os
import re
import requests
import filetype
import glob
import sys

# 提取文件中的链接
def extract_links(archive_path):
    try:
        with open(archive_path, "rb") as file:
            content = file.read().decode("latin1")
    except (OSError, UnicodeDecodeError) as e:
        print(f"错误：未能解析{archive_path}：{e}")
        return []
    # 提取所有链接
    return [re.sub(r"(bizid=\d+).*", r"\1", link) for link in re.findall(r"https?://[^\s]+", content)]

# 下载图片并保存到指定文件夹
def download_images(links, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    with requests.Session() as session:
        for index, link in enumerate(links):
            try:
                response = session.get(link.strip(), timeout=10)
                response.raise_for_status()
                # 检测文件类型
                kind = filetype.guess(response.content)
                if kind:
                    with open(os.path.join(output_folder, f"image_{index + 1}.{kind.extension}"), "wb") as img_file:
                        img_file.write(response.content)
                else:
                    print(f"错误：无法检测链接 {index + 1} 的图片类型：{link}")
            except requests.RequestException as e:
                print(f"错误：下载 {link} 失败：{e}")

def print_help():
    print("Usage: python Wechat-Sticker-Export.py [--list] [--dry] [--help|-h]")
    print("  --list    将所有提取出的链接打印到 link.txt 中")
    print("  --dry     不执行下载图片的操作")
    print("  --help, -h 打印出接收的参数")

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
        return

    base_path = os.path.expanduser("~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/")
    archive_paths = glob.glob(base_path + "*/Stickers/fav.archive")

    if not archive_paths:
        print("错误：没有找到存放表情包的文件夹")
        return

    # 提取所有链接
    all_links = [link for path in archive_paths for link in extract_links(path)]
    if all_links:
        print(f"所有表情包已提取，共 {len(all_links)} 个")

        if "--list" in sys.argv:
            with open("links.txt", "w") as file:
                for link in all_links:
                    file.write(link + "\n")
            print("表情包下载链接已保存到 links.txt")

        if "--dry" not in sys.argv:
            # 下载所有图片
            download_images(all_links, "downloaded_images")

if __name__ == "__main__":
    main()
