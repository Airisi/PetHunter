from utils.window_tool import WindowTool


class MouseKeyboard:
    click_at = staticmethod(WindowTool.click_at)
    start_capture_click = staticmethod(WindowTool.start_capture_click)
    is_capture_active = staticmethod(WindowTool.is_capture_active)
    stop_capture_click = staticmethod(WindowTool.stop_capture_click)

