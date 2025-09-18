#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数设置页面模块
提供游戏参数和卡片优先级设置功能
"""

import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QGroupBox, QGridLayout, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from src.utils.resource_utils import resource_path

class ConfigPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.config_data = self.load_config()
        self.card_widgets = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("参数设置")
        title_label.setStyleSheet("font-size: 20px; color: #88AAFF; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 拖拽速度设置
        drag_group = QGroupBox("拖拽速度设置 (单位:秒)")
        drag_layout = QGridLayout(drag_group)
        
        # 获取当前拖拽速度设置
        drag_range = [0.10, 0.13]  # 默认值
        if "game" in self.config_data and "human_like_drag_duration_range" in self.config_data["game"]:
            drag_range = self.config_data["game"]["human_like_drag_duration_range"]
        
        drag_layout.addWidget(QLabel("最小拖拽时间:"), 0, 0)
        self.min_drag_input = QLineEdit(str(drag_range[0]))
        self.min_drag_input.setStyleSheet("background-color: rgba(80, 80, 120, 180); color: white;")
        drag_layout.addWidget(self.min_drag_input, 0, 1)
        
        drag_layout.addWidget(QLabel("最大拖拽时间:"), 1, 0)
        self.max_drag_input = QLineEdit(str(drag_range[1]))
        self.max_drag_input.setStyleSheet("background-color: rgba(80, 80, 120, 180); color: white;")
        drag_layout.addWidget(self.max_drag_input, 1, 1)
        
        drag_layout.addWidget(QLabel("说明: 设置更小的值会使操作更快，但可能被检测为脚本"), 2, 0, 1, 2)
        
        main_layout.addWidget(drag_group)
        
        # 卡片优先级设置
        card_group = QGroupBox("卡片优先级设置")
        card_layout = QVBoxLayout(card_group)
        
        # 说明
        desc_label = QLabel("为卡组中的卡片设置优先级 数字越大优先级越低，优先度上限是999(默认所有卡牌999)")
        desc_label.setStyleSheet("font-size: 12px; color: #AACCFF;")
        card_layout.addWidget(desc_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()  # 保存为实例变量
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        scroll_area.setWidget(self.scroll_content)
        
        # 设置滚动区域样式
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QWidget#ScrollContent {
                background-color: transparent;
            }
        """)
        self.scroll_content.setObjectName("ScrollContent")
        
        card_layout.addWidget(scroll_area)
        main_layout.addWidget(card_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存设置")
        self.save_btn.clicked.connect(self.save_config)
        self.back_btn = QPushButton("返回主界面")
        self.back_btn.clicked.connect(lambda: self.parent.stacked_widget.setCurrentIndex(0))
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.back_btn)
        btn_layout.addStretch()
        
        main_layout.addLayout(btn_layout)
        
        # 加载卡片优先级设置
        self.load_card_priority_settings(self.scroll_content)
    
    def get_current_config(self):
        """获取当前配置的JSON数据"""
        config = {
            "game": {
                "human_like_drag_duration_range": [
                    float(self.min_drag_input.text()),
                    float(self.max_drag_input.text())
                ]
            }
        }
        
        # 获取卡片优先级设置
        high_priority_cards = {}
        evolve_priority_cards = {}
        
        for card in self.card_widgets:
            card_name = card["card_name"]
            
            play_priority_text = card["play_priority"].text().strip()
            if play_priority_text:
                high_priority_cards[card_name] = {
                    "priority": int(play_priority_text)
                }
            
            evolve_priority_text = card["evolve_priority"].text().strip()
            if evolve_priority_text:
                evolve_priority_cards[card_name] = {
                    "priority": int(evolve_priority_text)
                }
        
        if high_priority_cards:
            config["high_priority_cards"] = high_priority_cards
        if evolve_priority_cards:
            config["evolve_priority_cards"] = evolve_priority_cards
        
        return config
    
    def refresh_card_priority(self):
        """刷新卡片优先级显示"""
        # 保存当前输入的优先级值
        current_settings = {}
        for card in self.card_widgets:
            play_priority = card["play_priority"].text().strip()
            evolve_priority = card["evolve_priority"].text().strip()
            current_settings[card["card_name"]] = {
                "play": play_priority,
                "evolve": evolve_priority
            }
        
        # 重新加载卡片
        self.load_card_priority_settings(self.scroll_content)
        
        # 恢复之前输入的优先级值
        for card in self.card_widgets:
            card_name = card["card_name"]
            if card_name in current_settings:
                settings = current_settings[card_name]
                if settings["play"]:
                    card["play_priority"].setText(settings["play"])
                if settings["evolve"]:
                    card["evolve_priority"].setText(settings["evolve"])
    
    def load_config(self):
        """加载配置文件"""
        config_path = resource_path("config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {str(e)}")
                return {}
        return {}
    
    def load_card_priority_settings(self, scroll_content):
        """加载卡片优先级设置"""
        # 清空现有内容
        for i in reversed(range(self.scroll_layout.count())): 
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.card_widgets = []
        
        # 获取卡组目录
        card_dir = resource_path("shadowverse_cards_cost")
        if not os.path.exists(card_dir):
            QMessageBox.warning(self, "警告", "未找到'shadowverse_cards_cost'文件夹，请先选择卡组！")
            return
        
        # 获取所有卡片文件
        card_files = []
        for file in os.listdir(card_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                card_files.append(file)
        
        # 如果没有卡片，显示提示
        if not card_files:
            no_card_label = QLabel("没有找到卡片，请先在'卡组选择'页面选择卡片")
            no_card_label.setStyleSheet("color: #FF8888; font-size: 14px;")
            no_card_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(no_card_label)
            return
        
        # 为每张卡片创建设置行
        for card_file in card_files:
            # 解析卡片名称
            card_name = card_file.split('_', 1)[-1].rsplit('.', 1)[0]
            
            # 创建卡片行控件
            card_row = QWidget()
            card_row.setStyleSheet("background-color: rgba(60, 60, 90, 150); border-radius: 10px;")
            row_layout = QHBoxLayout(card_row)
            row_layout.setContentsMargins(10, 5, 10, 5)
            
            # 卡片图片
            card_label = QLabel()
            card_path = resource_path(os.path.join("shadowverse_cards_cost", card_file))
            pixmap = QPixmap(card_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(80, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                card_label.setPixmap(pixmap)
            card_label.setAlignment(Qt.AlignCenter)
            row_layout.addWidget(card_label)
            
            # 卡片名称
            name_label = QLabel(card_name)
            name_label.setStyleSheet("color: #FFFFFF; font-weight: bold; min-width: 120px;")
            name_label.setAlignment(Qt.AlignCenter)
            row_layout.addWidget(name_label)
            
            # 出牌优先级
            row_layout.addWidget(QLabel("出牌优先级:"))
            play_priority_input = QLineEdit()
            play_priority_input.setStyleSheet("background-color: rgba(80, 80, 120, 180); color: white;")
            play_priority_input.setMaximumWidth(50)
            
            # 设置当前值（如果有）
            high_priority = self.config_data.get("high_priority_cards", {}).get(card_name, {})
            if high_priority:
                play_priority_input.setText(str(high_priority.get("priority", "")))
            else:
                play_priority_input.setText("")  # 确保为空
            row_layout.addWidget(play_priority_input)
            
            # 进化优先级
            row_layout.addWidget(QLabel("进化优先级:"))
            evolve_priority_input = QLineEdit()
            evolve_priority_input.setStyleSheet("background-color: rgba(80, 80, 120, 180); color: white;")
            evolve_priority_input.setMaximumWidth(50)
            
            # 设置当前值（如果有）
            evolve_priority = self.config_data.get("evolve_priority_cards", {}).get(card_name, {})
            if evolve_priority:
                evolve_priority_input.setText(str(evolve_priority.get("priority", "")))
            else:
                evolve_priority_input.setText("")  # 确保为空
            row_layout.addWidget(evolve_priority_input)
            
            # 保存控件引用
            self.card_widgets.append({
                "card_name": card_name,
                "play_priority": play_priority_input,
                "evolve_priority": evolve_priority_input
            })
            
            self.scroll_layout.addWidget(card_row)
        
        self.scroll_layout.addStretch()
    
    def save_config(self):
        """保存配置到文件"""
        # 验证并保存拖拽速度设置
        try:
            min_drag = float(self.min_drag_input.text())
            max_drag = float(self.max_drag_input.text())
            
            if min_drag < 0 or max_drag < 0:
                raise ValueError("拖拽时间不能为负数")
            if min_drag > max_drag:
                raise ValueError("最小拖拽时间不能大于最大拖拽时间")
            
            # 更新配置数据
            if "game" not in self.config_data:
                self.config_data["game"] = {}
            self.config_data["game"]["human_like_drag_duration_range"] = [min_drag, max_drag]
        except Exception as e:
            QMessageBox.warning(self, "输入错误", f"拖拽时间设置错误: {str(e)}")
            return
        
        # 准备卡片优先级设置
        high_priority_cards = {}
        evolve_priority_cards = {}
        
        # 处理每张卡片的优先级设置
        for card in self.card_widgets:
            card_name = card["card_name"]
            
            # 处理出牌优先级
            play_priority_text = card["play_priority"].text().strip()
            if play_priority_text:
                try:
                    priority = int(play_priority_text)
                    if priority < 0 or priority > 999:
                        raise ValueError("优先级必须在0-999之间")
                    high_priority_cards[card_name] = {"priority": priority}
                except Exception as e:
                    QMessageBox.warning(
                        self, "输入错误", 
                        f"卡片 '{card_name}' 的出牌优先级设置错误: {str(e)}"
                    )
                    return
            
            # 处理进化优先级
            evolve_priority_text = card["evolve_priority"].text().strip()
            if evolve_priority_text:
                try:
                    priority = int(evolve_priority_text)
                    if priority < 0 or priority > 999:
                        raise ValueError("优先级必须在0-999之间")
                    evolve_priority_cards[card_name] = {"priority": priority}
                except Exception as e:
                    QMessageBox.warning(
                        self, "输入错误", 
                        f"卡片 '{card_name}' 的进化优先级设置错误: {str(e)}"
                    )
                    return
        
        # 更新配置数据
        if high_priority_cards:
            self.config_data["high_priority_cards"] = high_priority_cards
        elif "high_priority_cards" in self.config_data:
            del self.config_data["high_priority_cards"]
        
        if evolve_priority_cards:
            self.config_data["evolve_priority_cards"] = evolve_priority_cards
        elif "evolve_priority_cards" in self.config_data:
            del self.config_data["evolve_priority_cards"]
        
        # 保存到文件
        config_path = os.path.join(get_exe_dir(), "config.json")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            
            QMessageBox.information(self, "成功", "配置已保存！")
            self.parent.log_output.append("[配置] 参数设置已更新")
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存配置文件时出错: {str(e)}")
    
    def refresh_config_display(self):
        """刷新整个配置页面的显示"""
        # 重新加载配置数据
        self.config_data = self.load_config()
        
        # 刷新拖拽速度设置
        drag_range = [0.10, 0.13]  # 默认值
        if "game" in self.config_data and "human_like_drag_duration_range" in self.config_data["game"]:
            drag_range = self.config_data["game"]["human_like_drag_duration_range"]
        self.min_drag_input.setText(str(drag_range[0]))
        self.max_drag_input.setText(str(drag_range[1]))
        
        # 刷新卡片优先级设置
        self.load_card_priority_settings(self.scroll_content)