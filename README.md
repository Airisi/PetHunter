# PetHunter 辅助测量台

一个基于 `PySide6` 的 Windows 桌面小工具，用于在目标游戏窗口上进行飞行过程测量。  
工具支持窗口绑定、蒙层显示、自动点击触发、飞行倒计时与结果统计。

## 当前功能

- 绑定目标窗口（按窗口标题模糊匹配）
- 透明蒙层跟随游戏窗口（显示状态、高度、倒计时）
- 记录自动点击轨迹（可开关）
- 支持捕获起飞/动作按钮点击坐标
- 自动按配置触发点击并进行多次飞行测量
- 输出测量结果（总上升高度、平均上升速度、下落耗时/速度等）

## 项目结构

```text
PetHunter/
├─ main.py                         # 程序入口
├─ app/                            # 状态机/事件/编排（骨架已建）
├─ features/                       # 测量/截图/识别/抓宠/对战（逐步迁移）
├─ infrastructure/                 # Windows/输入/叠加层等平台能力（封装）
├─ config/                         # runs 下配置与输出路径集中管理
├─ core/
│  ├─ mask_overlay.py              # 游戏蒙层显示
│  └─ mouse_trace_overlay.py       # 鼠标轨迹绘制蒙层
├─ ui/
│  ├─ main_window.py               # 主窗口逻辑
│  ├─ designer/
│  │  └─ main_window.ui            # Qt Designer 源文件
│  └─ generated/
│     └─ ui_main_window.py         # 由 .ui 生成的 Python UI 代码
└─ utils/
   ├─ flight_tool.py               # 飞行测量核心逻辑
   ├─ window_tool.py               # 窗口查找、前置、点击、坐标转换
   └─ log_manager.py               # 日志展示与去重
```

## 运行环境

- 操作系统：`Windows`（依赖 Win32 API）
- Python：建议 `3.10+`

依赖库：

- `PySide6`
- `pywin32`

## 安装与启动

在项目根目录执行：

```bash
pip install PySide6 pywin32
python main.py
```

## 使用说明（快速）

1. 启动程序后，在“窗口标题”输入框中填入目标窗口标题关键字。
2. 点击“绑定窗口”，确认日志显示绑定成功。
3. 需要时点击“捕获起飞点/捕获目标点”，在目标窗口内点一次完成坐标捕获。
4. 设置“单次飞行时长”和“飞行次数”。
5. 点击“开始测量”，进入测量流程。
6. 测量结束后点击“标记落地”，查看统计结果。
7. 点击“重置”可清空当前状态并重新开始。

## 配置与数据

- 所有配置会写入：`runs/configs/flight_config.json`
  - `window_name`：绑定成功的窗口名称关键字
  - `fly_duration`：单次飞行时长（秒）
  - `fly_times`：飞行次数
  - `start_click` / `action_click`：捕获到的起飞/动作点击坐标
  - `mask_enabled`：蒙板是否开启
  - `trace_enabled`：绘图轨迹是否开启
- 每次测量结果会追加写入同一个 CSV：`runs/measurements/measurement_results.csv`（便于后续汇总对比）

## 注意事项

- 本项目通过窗口前置与鼠标事件模拟进行自动点击，请确保目标窗口可见且可交互。
- DPI 缩放会影响坐标换算，建议使用捕获功能获取点击坐标。
- 仅适用于 Windows 环境。

## 其他

ui 文件转换

```bash
pyside6-uic ui/designer/main_window.ui -o ui/generated/ui_main_window.py
```