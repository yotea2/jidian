import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, 
    QFrame, QStackedWidget, QGroupBox,QPushButton, QLabel, QMessageBox, 
    QApplication, QLineEdit)
from PyQt5.QtGui import QPainter, QIcon, QPixmap,QColor
from PyQt5.QtCore import Qt, QDateTime, QTimer
import pyqtgraph as pg # 用于数据可视化


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("肌电信号分析系统YSJ")
        self.setGeometry(114, 514, 1600, 1200)
        
        # 应用程序样式
        self.setup_styles()
        
        # 中心部件和主布局
        self.setup_central_widget()
        
        # 顶部状态栏
        self.create_top_bar()
        
        # 页面堆叠管理器
        self.create_page_stack()
        
        # 底部导航栏
        self.create_bottom_nav()
        
        # 初始化当前页面
        self.current_page_index = 0

    """设置应用程序样式"""
    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #495057;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QLabel {
                font-size: 14px;
                color: #212529;
            }
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox {
                padding: 6px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
                min-height: 36px;
            }
            QListWidget, QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background-color: #007bff;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #dee2e6;
            }
        """)

    """创建中心部件"""
    def setup_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主垂直布局
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
    
    """创建顶部状态栏"""
    def create_top_bar(self):
        top_bar = QFrame()
        top_bar.setFixedHeight(80)
        top_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
            }
        """)
        
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 10, 20, 10)
        
        title_container = QHBoxLayout()

        title_label = QLabel("肌电信号分析系统")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                padding-left: 10px;
            }
        """)
        
        title_container.addWidget(title_label)
        
        # 状态信息区域
        status_container = QHBoxLayout()
        
        # 连接状态
        self.connection_status = QLabel()
        self.connection_status.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                background-color: rgba(0, 0, 0, 0.2);
                padding: 6px 12px;
                border-radius: 4px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        self.update_connection_status(False)  # 初始未连接
        
        # 时间
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        
        status_container.addWidget(self.connection_status)
        status_container.addWidget(self.time_label)
        
        # 添加到顶部
        top_layout.addLayout(title_container)
        top_layout.addStretch()
        top_layout.addLayout(status_container)
        
        # 添加顶部栏到主布局
        self.main_layout.addWidget(top_bar)
        
        # 时间更新
        self.update_time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 1秒

        """更新时间显示"""
    def update_time(self):
        current_time = QDateTime.currentDateTime()
        time_str = current_time.toString("yyyy-MM-dd hh:mm:ss")
        self.time_label.setText(f"📅 {time_str}")

        """更新连接状态"""
    def update_connection_status(self, connected):
        if connected:
            self.connection_status.setText("✅ 设备已连接")
            self.connection_status.setStyleSheet(self.connection_status.styleSheet() + "color: #d4edda;")
        else:
            self.connection_status.setText("❌ 设备未连接")
            self.connection_status.setStyleSheet(self.connection_status.styleSheet() + "color: #f8d7da;")
        
        """页面堆叠管理器"""
    def create_page_stack(self):
        self.page_stack = QStackedWidget()
        self.page_stack.setStyleSheet("""
            QStackedWidget {
                background-color: white;
                border: none;
            }
        """)
        
        # 各个页面
        self.create_home_page()
        self.create_visualization_page()                
        self.create_device_page()
        self.create_settings_page()
        
        # 添加到堆叠窗口
        self.page_stack.addWidget(self.home_page)
        self.page_stack.addWidget(self.visualization_page)
        self.page_stack.addWidget(self.device_page)
        self.page_stack.addWidget(self.settings_page)
        
        # 添加到主布局
        self.main_layout.addWidget(self.page_stack, 1)

        """创建首页"""  
    def create_home_page(self):
        self.home_page = QWidget()
        layout = QVBoxLayout(self.home_page)
    
        welcome_label = QLabel("欢迎使用肌电信号分析系统")
        welcome_label.setStyleSheet(f"""
        QLabel {{
            font-size: 36px;
            font-weight: bold;
            color: #343a40;
            padding: 10px 0;
        }}
    """)
        welcome_label.setAlignment(Qt.AlignCenter)

        # 实时波形图
        wave_group = QGroupBox("实时肌电信号波形")
        wave_layout = QVBoxLayout(wave_group)
    
        # 创建图表
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left', '振幅', units='mV')
        self.plot_widget.setLabel('bottom', '时间', units='s')
        self.plot_widget.showGrid(x=True, y=True)
        
        wave_layout.addWidget(self.plot_widget)
        
        #活动状态显示
        status_group = QGroupBox("肌肉活动状态")
        status_layout = QGridLayout(status_group)
        
        # 状态标签
        self.activity_status = QLabel("静止")
        self.activity_status.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #28a745;
                padding: 10px;
                border: 2px solid #28a745;
                border-radius: 8px;
            }
        """)
        self.activity_status.setAlignment(Qt.AlignCenter)
        
        # 状态描述
        status_desc = QLabel("状态说明：肌肉处于休息状态")
        status_desc.setStyleSheet(f"""
        QLabel {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            font-size: 20px;
            color: #6c757d;
        }}
    """)

        status_layout.addWidget(self.activity_status, 0, 0, 1, 2)
        status_layout.addWidget(status_desc, 1, 0, 1, 2)
        
        # 预警信息
        warning_group = QGroupBox("健康预警")
        warning_layout = QVBoxLayout(warning_group)
        
        self.warning_label = QLabel("暂无预警")
        self.warning_label.setStyleSheet("""
            QLabel {
                font-size: 30px;
                color: #6c757d;
                padding: 10px;
            }
        """)
        warning_layout.addWidget(self.warning_label)
        
        layout.addWidget(welcome_label, 1)
        layout.addWidget(wave_group, 6)
        layout.addWidget(status_group, 4)
        layout.addWidget(warning_group, 2)
        

        #"""颜色变暗"""
    def darken_color(self, hex_color):
        # 转换为RGB降低亮度
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, c - 30) for c in rgb)
        return f'#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}'
    
        
        #"""数据可视化页面"""
    def create_visualization_page(self):
        self.visualization_page = QWidget()
        layout = QVBoxLayout(self.visualization_page)
        
        title = QLabel("数据可视化")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #343a40;")
        title.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title)
        layout.addStretch()
        
        """设备管理页面"""

    def create_device_page(self):
        """设备管理页面"""
        from device_manager import DeviceManagerUI

        # 使用独立的设备管理组件
        self.device_page = DeviceManagerUI()

        # 连接信号（示例，实际根据需求连接）
        self.device_page.scan_requested.connect(self._scan_devices)
        self.device_page.connect_requested.connect(self._connect_device)
        self.device_page.disconnect_requested.connect(self._disconnect_device)

        # 模拟一些测试设备
        self._setup_test_devices()

    def _setup_test_devices(self):
        """设置测试设备（开发用）"""
        from device_manager import EMGDevice, DeviceStatus

        devices = [
            EMGDevice("肌电采集器-A", "AA:BB:CC:DD:EE:FF", -45, 85, DeviceStatus.DISCONNECTED, "1.0.0"),
            EMGDevice("肌电采集器-B", "11:22:33:44:55:66", -60, 100, DeviceStatus.DISCONNECTED, "1.0.0",
                      is_paired=True),
            EMGDevice("肌电采集器-C", "77:88:99:AA:BB:CC", -75, 30, DeviceStatus.CONNECTED, "1.0.0"),
        ]

        self.device_page.update_device_list(devices)

    def _scan_devices(self):
        """扫描设备（模拟）"""
        QMessageBox.information(self, "扫描", "正在扫描附近设备...")
        # 这里可以添加真实的蓝牙扫描逻辑

    def _connect_device(self, device):
        """连接设备（模拟）"""
        QMessageBox.information(self, "连接", f"正在连接 {device.name}...")
        self.device_page.update_connection_status(True, device.name)

    def _disconnect_device(self):
        """断开连接"""
        self.device_page.update_connection_status(False)
    def create_settings_page(self):
        
        self.settings_page = QWidget()
        layout = QVBoxLayout(self.settings_page)
        
        title = QLabel("用户设置")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #343a40;")
        title.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title)
        layout.addStretch()
    
        """创建底部导航栏"""
    def create_bottom_nav(self):
        
        bottom_nav = QFrame()
        bottom_nav.setFixedHeight(70)
        bottom_nav.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 2px solid #dee2e6;
            }
        """)
        
        nav_layout = QHBoxLayout(bottom_nav)
        nav_layout.setContentsMargins(20, 10, 20, 10)
        nav_layout.setSpacing(10)
        
        # 导航按钮
        nav_items = [
            ("🤪首页", 0, "#007bff"),
            ("🤩数据可视化", 1, "#17a2b8"),
            ("😎设备管理", 2, "#28a745"),
            ("🥺用户设置", 3, "#343a40")
        ]
        
        self.nav_buttons = []
        
        for content, page_idx, color in nav_items:
            btn = self.create_nav_button(content, page_idx, color)
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        # 添加到底部
        self.main_layout.addWidget(bottom_nav)
    
    def create_nav_button(self, content, page_idx, color):
        """创建导航按钮"""
        btn = QPushButton()
        btn.setCheckable(True)
        btn.setFixedHeight(66)
        btn.setCursor(Qt.PointingHandCursor)
        
        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(30, 8, 30, 8)
        btn_layout.setSpacing(1)

        content_label = QLabel(content)
        content_label.setAlignment(Qt.AlignCenter)
        
        btn_layout.addWidget(content_label)
        
        # 初始样式
        if page_idx == 0:
            btn.setChecked(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 8px;
                    border: none;
                }}
                QLabel {{
                    color: white;
                    font-size: 25px;
                    font-weight: bold;
                }}
                QPushButton::menu-indicator {{ image: none; }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #dee2e6;
                }}
                QPushButton:hover {{
                    background-color: #f8f9fa;
                    border-color: {color};
                }}
                QLabel {{
                    color: #6c757d;
                    font-size: 25px;
                    font-weight: bold;
                }}
                QPushButton::menu-indicator {{ image: none; }}
            """)
        
        # 连接处理函数
        btn.clicked.connect(lambda checked, idx=page_idx: self.switch_page(idx))
        
        return btn
    
        #"""切换页面"""
    def switch_page(self, page_index):
        if 0 <= page_index < self.page_stack.count():
            self.page_stack.setCurrentIndex(page_index)
            self.current_page_index = page_index
            # 导航按钮状态
            for i, btn in enumerate(self.nav_buttons):
                if i == page_index:
                    # 获取按钮颜色
                    colors = ["#007bff", "#28a745", "#17a2b8", "#6c757d", "#343a40"]
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {colors[i]};
                            border-radius: 8px;
                            border: none;
                        }}
                        QLabel {{
                            color: white;
                            font-size: 25px;
                            font-weight: bold;
                        }}
                    """)
                    btn.setChecked(True)
                else:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: white;
                            border-radius: 8px;
                            border: 1px solid #dee2e6;
                        }}
                        QPushButton:hover {{
                            background-color: #f8f9fa;
                        }}
                        QLabel {{
                            color: #6c757d;
                            font-size: 25px;
                            font-weight: bold;
                        }}
                    """)
                    btn.setChecked(False)
    
        """导出报告"""
    def export_report(self):
        
        reply = QMessageBox.information(
            self,
            "导出报告",
            "此功能尚未实现。\n\n",
            QMessageBox.Ok
        )

"""应用程序入口"""
def main():
    
    app = QApplication(sys.argv)
    
    # 应用程序信息
    app.setApplicationName("肌电信号分析系统")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("生物信号实验室")
    
    # 创建显示主窗口
    window = MainWindow()
    window.show()
    
    # 显示启动提示
    QMessageBox.information(
        window,
        "分析系统已启动",
        "祝您使用愉快喵！",
        QMessageBox.Ok
    )

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()