"""
通知管理器
处理用户通知和界面交互
"""

"""
通知管理器
处理用户通知和界面交互
在打包为 exe 的环境中未必包含 tkinter，因此这里使用可选导入策略：
- 优先使用 PyQt5.QtWidgets.QMessageBox（若可用）
- 然后尝试 tkinter（如果存在）
- 最后回退到 ctypes 的 MessageBox 或控制台输出
"""

try:
    from PyQt5.QtWidgets import QMessageBox, QApplication
    _HAS_PYQT = True
except Exception:
    _HAS_PYQT = False

try:
    import tkinter as tk
    from tkinter import messagebox
    _HAS_TK = True
except Exception:
    _HAS_TK = False

import ctypes
import logging
import queue
import threading
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class NotificationManager:
    """通知管理器类"""
    
    def __init__(self):
        self.notification_queue = queue.Queue()
        self.notification_thread = None
        self.running = False
    
    def start(self):
        """启动通知处理线程"""
        if self.running:
            return
        
        self.running = True
        self.notification_thread = threading.Thread(target=self._notification_handler, daemon=True)
        self.notification_thread.start()
        logger.info("通知管理器已启动")
    
    def stop(self):
        """停止通知处理线程"""
        self.running = False
        if self.notification_queue:
            self.notification_queue.put(None)  # 发送退出信号
        
        if self.notification_thread and self.notification_thread.is_alive():
            self.notification_thread.join(timeout=2.0)
        
        logger.info("通知管理器已停止")
    
    def show_notification(self, title: str, message: str):
        """显示通知"""
        self.notification_queue.put((title, message))
    
    def _notification_handler(self):
        """处理通知队列中的消息"""
        while self.running:
            try:
                # 从队列获取通知
                notification = self.notification_queue.get(timeout=1.0)
                if notification is None:  # 退出信号
                    self.notification_queue.task_done()
                    break
                
                title, message = notification
                # Prefer PyQt notification when available (running inside Qt app)
                if _HAS_PYQT:
                    self._show_pyqt_notification(title, message)
                elif _HAS_TK:
                    self._show_tkinter_notification(title, message)
                else:
                    self._show_fallback_notification(title, message)
                self.notification_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"通知处理出错: {str(e)}")
                # 只有在实际获取到项目时才调用task_done
                # 这里不调用task_done，因为异常可能发生在获取项目之后
    
    def _show_tkinter_notification(self, title: str, message: str):
        """使用Tkinter显示通知"""
        try:
            # 创建临时窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            # 显示消息框
            messagebox.showinfo(title, message)
            
            # 关闭窗口
            root.destroy()
        except Exception as e:
            logger.error(f"显示Tkinter通知失败: {str(e)}")
            # 回退到传统弹窗
            self._show_fallback_notification(title, message)

    def _show_pyqt_notification(self, title: str, message: str):
        """使用 PyQt5 的 QMessageBox 显示通知（如果在 Qt 应用上下文中）。"""
        try:
            # If there's an existing QApplication, use it; otherwise create a temporary one.
            app = QApplication.instance()
            own_app = False
            if app is None:
                app = QApplication([])
                own_app = True

            msg = QMessageBox()
            msg.setWindowTitle(title)
            msg.setText(message)
            msg.setIcon(QMessageBox.Information)
            msg.exec_()

            if own_app:
                app.quit()
        except Exception as e:
            logger.error(f"显示PyQt通知失败: {str(e)}")
            # 回退
            if _HAS_TK:
                self._show_tkinter_notification(title, message)
            else:
                self._show_fallback_notification(title, message)
    
    def _show_fallback_notification(self, title: str, message: str):
        """回退通知方法"""
        try:
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
        except Exception as e:
            logger.error(f"回退通知也失败: {str(e)}")
            # 最后回退到控制台输出
            print(f"\n=== {title} ===")
            print(message)
            print("=" * 50)
    
    def show_error(self, title: str, message: str):
        """显示错误通知"""
        self.show_notification(f"错误: {title}", message)
    
    def show_warning(self, title: str, message: str):
        """显示警告通知"""
        self.show_notification(f"警告: {title}", message)
    
    def show_info(self, title: str, message: str):
        """显示信息通知"""
        self.show_notification(f"信息: {title}", message)
    
    def show_success(self, title: str, message: str):
        """显示成功通知"""
        self.show_notification(f"成功: {title}", message) 