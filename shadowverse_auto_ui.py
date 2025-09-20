#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shadowverse Automation UI 主程序入口
使用重构后的UI模块启动图形界面
"""

import sys
import os
import logging
import queue

# 添加src目录到系统路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.ui import ShadowverseUI, load_custom_font
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from main import setup_logging as setup_main_logging, log_queue  # 使用别名导入日志设置函数和日志队列

def setup_logging():
    """设置基础日志系统，使用main.py中的配置并连接到日志队列"""
    from src.config import ConfigManager
    config_manager = ConfigManager()
    
    # 使用main.py中的setup_logging函数并传入log_queue
    logger = setup_main_logging(config_manager.config, log_queue)
    return logger

if __name__ == "__main__":
    # 设置日志
    logger = setup_logging()
    logger.info("=== Shadowverse Automation UI 启动 ===")
    
    try:
        # 设置中文字体支持
        load_custom_font()
        
        # 创建应用程序实例
        app = QApplication(sys.argv)
        
        # 设置应用程序样式
        app.setStyle('Fusion')  # 使用Fusion风格以获得更好的跨平台一致性
        
        # 应用全局样式表（可选）
        app.setStyleSheet("""
            QWidget {
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            }
            QPushButton {
                padding: 6px;
                border-radius: 3px;
            }
            QLineEdit, QComboBox, QTextEdit {
                padding: 5px;
                border-radius: 3px;
            }
        """)
        
        # 创建并显示主窗口
        window = ShadowverseUI()
        window.show()
        
        logger.info("主窗口已显示")
        
        # 运行应用程序主循环
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.exception(f"UI程序运行出错: {str(e)}")
        print(f"程序崩溃: {str(e)}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
        sys.exit(1)