import os
import re
import requests
import imghdr
import glob

def extract_links(archive_path):
    try:
        with open(archive_path, "rb") as file:
            content = file.read().decode("latin1")
    except (OSError, UnicodeDecodeError) as e:
        print(f"错误：未能解析{archive_path}：{e}")
        return []
    return [re.sub(r"(bizid=\d+).*", r"\1", link) for link in re.findall(r"https?://[^\s]+", content)]

def download_images(links, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    with requests.Session() as session:
        for index, link in enumerate(links):
            try:
                response = session.get(link.strip(), timeout=10)
                response.raise_for_status()
                image_type = imghdr.what(None, h=response.content)
                if image_type:
                    with open(os.path.join(output_folder, f"image_{index + 1}.{image_type}"), "wb") as img_file:
                        img_file.write(response.content)
                else:
                    print(f"错误：无法检测链接 {index + 1} 的图片类型：{link}")
            except requests.RequestException as e:
                print(f"错误：下载 {link} 失败：{e}")

def main():
    base_path = os.path.expanduser("~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/")
    archive_paths = glob.glob(base_path + "*/Stickers/fav.archive")

    if not archive_paths:
        print("错误：没有找到存放表情包的文件夹")
        return

    all_links = [link for path in archive_paths for link in extract_links(path)]
    if all_links:
        print(f"所有表情包已提取，共 {len(all_links)} 个")
        download_images(all_links, "downloaded_images")

if __name__ == "__main__":
    main()
