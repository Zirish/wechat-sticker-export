## Wechat Sticker Export

这是一个在 Mac 上运行的 python 脚本，从微信文件夹中各账户的表情包管理文件中提取链接，再从微信服务器上下载微信所有表情包。

使用则同意后果自负，如有封号风险需由自己承担。

### 使用
**安装依赖**：

```
pip install -r requirements.txt
```

**直接使用**：
```
python -m Wechat-Sticker-Export.py [-h] [--list] [--dry] [--output OUTPUT] [--timeout TIMEOUT] [--log LOG]
```

**参数**：
* -h, --help         显示帮助
* --list             将表情包下载链接输出到`link.txt`
* --dry              只获取链接，不从微信服务器下载表情包
* --output OUTPUT    指定下载路径。默认为downloaded_images
* --timeout TIMEOUT  指定超时。默认为None
* --log LOG          指定log路径。默认为wechat_sticker_export.log