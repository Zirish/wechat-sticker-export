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

    links = re.findall(r"https?://[^\s]+", content)
    updated_links = [re.sub(r"(bizid=\d+).*", r"\1", link) for link in links]
    return updated_links

def download_images(links, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    with requests.Session() as session:
        for index, link in enumerate(links):
            link = link.strip()
            if link:
                try:
                    response = session.get(link, timeout=10)
                    response.raise_for_status()
                    image_type = imghdr.what(None, h=response.content)
                    if image_type:
                        file_path = os.path.join(
                            output_folder, f"image_{index + 1}.{image_type}"
                        )
                        with open(file_path, "wb") as img_file:
                            img_file.write(response.content)
                    else:
                        print(
                            f"错误：无法检测链接 {index + 1} 的图片类型：{link}"
                        )
                except requests.RequestException as e:
                    print(f"错误：下载 {link} 失败：{e}")

def main():
    user_home = os.path.expanduser("~")
    base_path = os.path.join(
        user_home, "Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/"
    )
    pattern = base_path + "*/Stickers/fav.archive"
    archive_paths = glob.glob(pattern)

    if not archive_paths:
        print("错误：没有找到存放表情包的文件夹")
        return

    all_links = []
    for archive_path in archive_paths:
        links = extract_links(archive_path)
        if links:
            all_links.extend(links)
        else:
            print(f"错误：{archive_path} 中没有找到表情文件")

    if all_links:
        print(f"所有表情包已提取，共 {len(all_links)} 个")
        download_images(all_links, "downloaded_images")

if __name__ == "__main__":
    main()