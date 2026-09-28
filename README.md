# world.execute(me); — ASCII love letter

![world.execute(me);](docs/images/mv-cover.png)

Mili《world.execute(me);》的字符动画。支持中英字幕、原曲同步播放和终端字符动画。

基于原有 Python／Swift **终端命令行 ASCII 播放器框架**重新编排的音乐短片。画面在终端中以字符实时生成，由原曲音频时钟驱动；不使用网页或浏览器。

## 新版演出

保留原版多种画面语言，在其基础上按词义重新编排动作，不再用统一的几何体变形覆盖整首歌。英文歌词逐词点亮，屏幕右上角显示当前词。

- **开场**：`switch / on / power / line` 分别控制开关、通电和电流传输；保护、部件组装、数据写入与初始化各自成镜。
- **数学段**：`give / you / dimension` 推动点、线、面、体；圆在 `CIRCUMFERENCE` 时展开边界；`sit` 让 YOU 落上切线；保留原版无穷带和边界收紧。
- **切换段**：交流／直流、A.D.／B.C.、F／M、AM／PM 等使用不同的原版场景，关键切换重新绑定词级时刻。
- **生命与连接**：保留蔬菜网格、猫、身份改写和双通道心电图；传输从 `give / purr` 开始，六个 `left` 分别断开一条连接。
- **执行段**：十二次 EXECUTION 分别切割心、撕裂圆、拉平波、擦除猫、破坏时间、拆解身份、停止心跳、删除连接、递归模拟、清除记忆、关闭世界、执行自我。被破坏的画面来自前面实际出现过的场景。
- **结尾**：学习与问答沿用原版复杂场景；`algebraic / expression` 展示方程与对应心形；`free / trapped` 分别让 YOU 离开、把 ME 留在笼中。

按 **O** 在原版和逐词版间即时切换，音频不重启。按 **J / K** 暂停并跳到上一词／下一词，便于检查动作；空格继续播放。**C** 留下回应提示，不改写歌词中的离开与孤立。

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
| O | 原版／逐词版即时对比 |
| J / K | 暂停并跳到上一词／下一词 |
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
# 同一时刻的原版场景
python3 player.py --original --snapshot 150.8 --width 128 --height 44
python3 -m unittest discover -s tests -p 'test_choreography.py'
```

## 词级时间表

`word_timings.json` 包含 129 条原歌词时间段、396 个词。用本地原曲与 Whisper `small.en` / `base.en` 做强制对齐，并在原有短句边界内整理。播放不运行模型、不联网，只读取 JSON。

唱腔中的短词和重复词有对齐歧义。目前 **29 个词** 标为 `minimum-slot-estimate`：对零时长或过短结果做了最小显示时隙修补，以免单词被跳过。这些词仍需听校，时间表不代表人工逐词核准的音素标注。可编辑词的 `start` / `end` 微调高亮与词级动作；原版场景仍保留对应短句的时间锚点。

离线制作工具为 `tools/align_words.py`（可选依赖 `stable-ts==2.19.1`、FFmpeg、Whisper 模型）和 `tools/merge_word_timings.py`。模型和中间结果不属于播放器发布包，也不提交仓库。

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

本项目基于 [yym8224961/world.execute-me-ascii](https://github.com/yym8224961/world.execute-me-ascii) 继续开发。初始播放器、字符动画、字幕、频谱数据、构建工具及封面来自该项目，感谢原作者的工作。本版本在保留原版场景库 `scenes.py` 的基础上，新增 `choreography.py` 中的词义动作、词级时间表、逐词高亮和原版即时对比；沿用原项目的音频同步、字幕、频谱及构建框架。

截至 2026-09-28，当前克隆及原仓库的 GitHub 元数据中未发现明确的开源许可证；此来源声明不代表原作者授予了额外许可。
