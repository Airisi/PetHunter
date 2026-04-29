游戏：洛克王国世界（3D游戏）
画面：1280×720 固定窗口、全最低画质、固定地图区域、固定俯视视角、
变量：白天 / 傍晚 / 黑夜 / 雨天、光影变化
干扰：少量其他宠物、偶尔小遮挡
视角高度固定、3D 模型姿态稳定、无视角畸变



```bash
pyside6-uic ui/designer/main_window.ui -o ui/generated/ui_main_window.py
```

apt update && apt install libgl1-mesa-glx -y

conda create -n pytorch python=3.12 -y

conda activate pytorch

pip install pyside6

pip install ultralytics

pip install tqdm
