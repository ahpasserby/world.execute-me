# world.execute(me); — ASCII love letter

![world.execute(me);](docs/images/mv-cover.png)

Mili《world.execute(me);》的字符动画。支持中英字幕、原曲同步播放和终端字符动画。

基于原有 Python／Swift **终端命令行 ASCII 播放器框架**重新编排的音乐短片。画面在终端中以字符实时生成，由原曲音频时钟驱动；不使用网页或浏览器。

## 新版演出

围绕歌词中的创世、奉献、离开、执行和困于爱重新制作字符场景：

- 同一个字符核心在点集、圆周、正弦波、生命形态之间连续变化。
- 透视字符隧道、深度明暗与频谱呼吸共同表现空间；场景使用 ASCII 可打印字符，字幕保留中英双语。
- “你已经离开”逐次切断连接；十二次 `EXECUTION` 对应十二个逐个被清除的模拟世界。
- 前半段的圆在结尾成为循环与牢笼，保留“你自由了，我仍被困住”的落点。
- 按 **C** 回应，在当前角色周围留下字符波纹；离开段落只产生回声，不改变歌曲叙事。

先全屏终端再运行 `./run.sh`。建议至少 **128 列 × 44 行**；支持最低 64 列 × 24 行，窗口变化会自动适配。

## 单文件运行

当前再创作版本尚未发布 Release，请先按下方「从源码运行」启动。以下说明适用于自行构建的单文件包。

构建生成的 `world-execute-mv-macos.zip` 解压后包含 `world-execute-mv.pyz`。音乐、动画、字幕、频谱数据和音频播放组件内嵌在该文件内，无需另外指定 MP3。

需要 **macOS 12 或更新版本、Python 3.9 或更新版本**。音频组件同时包含 Apple Silicon 和 Intel 架构。终端播放器自身只使用 Python 标准库。

在 macOS「终端」中进入解压目录运行：

```sh
python3 world-execute-mv.pyz
```

也可双击 `运行单文件.command`，在系统终端中播放。按空格开始。推荐全屏，终端至少 64 列 × 24 行，128 列 × 44 行及以上效果更好。

```sh
# 从 2:38.7 开始直接播放
python3 world-execute-mv.pyz --start 158.7 --autoplay
```

内嵌音乐是随程序封装的资源，不是加密或 DRM。播放时会解包到当前用户的临时目录，正常退出后清理；不会读取旧电脑 Downloads 中的文件。运行过程无需联网。

## 操作

| 按键 | 功能 |
| --- | --- |
| 空格 | 开始／暂停 |
| 左／右 | 后退／前进 5 秒 |
| R | 从头播放 |
| C | 回应／留下回声 |
| Q | 退出 |
| H | 显示全部帮助 |
| 1–5 | 跳转章节 |

## 从源码运行

仓库不保存音频文件。从源码运行或重新打包前，请将自己的音频放到本地 `media/song.mp3`。使用 Release 播放包无需此步骤。

首次构建音频组件需要 Apple Command Line Tools（含 Swift 编译器）：

```sh
xcode-select --install
```

然后执行：

```sh
./run.sh
```

启动脚本在缺少 `audio-clock` 时自动编译本机架构。双击 `播放MV.command` 可在 macOS 系统终端中运行源码版。

## 检查场景

不播放音频也可以输出确定时刻的字符快照：

```sh
python3 player.py --snapshot 150.8 --width 128 --height 44
python3 player.py --snapshot 190 --width 128 --height 44 --plain
python3 -m unittest discover -s tests -p 'test_choreography.py'
```

## 重新打包

```sh
python3 tools/build_bundle.py
python3 tests/test_bundle.py
```

构建输出在 `dist/`：

- `world-execute-mv.pyz`：内嵌音乐的单文件播放器。
- `world-execute-mv-macos.zip`：包含播放器、启动器、说明的分发包。
- `SHA256SUMS.txt`：下载校验值。

音频以 macOS 音频时钟驱动画面；暂停、跳转时字幕与动画跟随音频时间。构建会生成 universal 音频组件，并在单文件包内记录各资源 SHA-256 以检查完整性。

## 收录范围

本仓库包含播放器、字幕、频谱和构建工具。源码不包含音乐文件；自行构建的播放包会内嵌本地提供的音频。

原曲与歌词：Mili《world.execute(me);》。本项目未对原曲、歌词或其他第三方素材授予额外使用许可。

## 参考与致谢

本项目基于 [yym8224961/world.execute-me-ascii](https://github.com/yym8224961/world.execute-me-ascii) 继续开发。初始播放器、字符动画、字幕、频谱数据、构建工具及封面来自该项目，感谢原作者的工作。本版本的逐句 ASCII 场景编排位于 `choreography.py`，播放器增加了情绪配色与键盘回应；保留原项目的音频同步、字幕、频谱及构建框架。

截至 2026-09-28，当前克隆及原仓库的 GitHub 元数据中未发现明确的开源许可证；此来源声明不代表原作者授予了额外许可。
