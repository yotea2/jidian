"""
设备管理界面 - 主界面类
"""
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QProgressBar, QHeaderView,
    QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon

from .device_model import EMGDevice, DeviceStatus


class DeviceManagerUI(QWidget):
    """设备管理主界面"""

    # 信号定义
    scan_requested = pyqtSignal()
    connect_requested = pyqtSignal(EMGDevice)
    disconnect_requested = pyqtSignal()
    pair_requested = pyqtSignal(EMGDevice)
    update_firmware_requested = pyqtSignal(EMGDevice)

    def __init__(self):
        super().__init__()
        self.devices = []
        self.current_device = None
        self.setup_ui()
        self.setup_styles()

    def setup_styles(self):
        """设置界面样式"""
        self.setStyleSheet("""
            QWidget {
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
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                min-height: 36px;
                border: none;
            }
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
        """)

    def setup_ui(self):
        """初始化界面布局"""
        main_layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("📱 设备管理")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #343a40;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # 设备列表
        device_list = self.create_device_list()
        main_layout.addWidget(device_list, 1)

        # 设备详情
        detail_panel = self.create_detail_panel()
        main_layout.addWidget(detail_panel)

        # 固件升级区域
        update_panel = self.create_update_panel()
        main_layout.addWidget(update_panel)

    def create_control_panel(self):
        """创建设备控制面板"""
        panel = QGroupBox("设备控制")
        layout = QHBoxLayout(panel)

        # 扫描按钮
        self.scan_btn = QPushButton("🔍 扫描设备")
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.scan_btn.clicked.connect(self.scan_requested.emit)

        # 连接按钮
        self.connect_btn = QPushButton("🔗 连接设备")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.connect_btn.clicked.connect(self._on_connect)
        self.connect_btn.setEnabled(False)

        # 断开按钮
        self.disconnect_btn = QPushButton("❌ 断开连接")
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.disconnect_btn.clicked.connect(self.disconnect_requested.emit)
        self.disconnect_btn.setEnabled(False)

        # 状态标签
        self.status_label = QLabel("状态: 未连接")
        self.status_label.setStyleSheet("font-size: 14px; color: #6c757d;")

        layout.addWidget(self.scan_btn)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.disconnect_btn)
        layout.addStretch()
        layout.addWidget(self.status_label)

        return panel

    def create_device_list(self):
        """创建设备列表表格"""
        panel = QGroupBox("可用设备")
        layout = QVBoxLayout(panel)

        self.device_table = QTableWidget()
        self.device_table.setColumnCount(6)
        self.device_table.setHorizontalHeaderLabels([
            "设备名称", "信号强度", "电量", "固件版本", "状态", "配对状态"
        ])
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.device_table.setAlternatingRowColors(True)
        self.device_table.itemSelectionChanged.connect(self._on_device_selected)

        layout.addWidget(self.device_table)
        return panel

    def create_detail_panel(self):
        """创建设备详情面板"""
        panel = QGroupBox("设备详情")
        layout = QGridLayout(panel)

        # 设备信息
        layout.addWidget(QLabel("设备名称:"), 0, 0)
        self.name_label = QLabel("未选择设备")
        layout.addWidget(self.name_label, 0, 1)

        layout.addWidget(QLabel("蓝牙地址:"), 1, 0)
        self.address_label = QLabel("--")
        layout.addWidget(self.address_label, 1, 1)

        layout.addWidget(QLabel("信号强度:"), 2, 0)
        self.rssi_label = QLabel("--")
        layout.addWidget(self.rssi_label, 2, 1)

        layout.addWidget(QLabel("电池电量:"), 0, 2)
        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setTextVisible(True)
        layout.addWidget(self.battery_bar, 0, 3)

        layout.addWidget(QLabel("固件版本:"), 1, 2)
        self.firmware_label = QLabel("--")
        layout.addWidget(self.firmware_label, 1, 3)

        # 配对按钮
        self.pair_btn = QPushButton("🤝 蓝牙配对")
        self.pair_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
        """)
        self.pair_btn.clicked.connect(self._on_pair)
        self.pair_btn.setEnabled(False)
        layout.addWidget(self.pair_btn, 2, 2, 1, 2)

        return panel

    def create_update_panel(self):
        """创建固件升级面板"""
        panel = QGroupBox("固件升级")
        layout = QVBoxLayout(panel)

        # 升级信息
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("当前版本:"))
        self.current_version_label = QLabel("1.0.0")
        info_layout.addWidget(self.current_version_label)
        info_layout.addWidget(QLabel("最新版本:"))
        self.latest_version_label = QLabel("1.0.0")
        info_layout.addWidget(self.latest_version_label)
        info_layout.addStretch()

        # 升级按钮和进度
        btn_layout = QHBoxLayout()
        self.update_btn = QPushButton("🔄 检查更新")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #fd7e14;
                color: white;
            }
            QPushButton:hover {
                background-color: #e9690c;
            }
        """)
        self.update_btn.clicked.connect(self._on_check_update)
        btn_layout.addWidget(self.update_btn)

        self.upgrade_btn = QPushButton("🚀 升级固件")
        self.upgrade_btn.setStyleSheet("""
            QPushButton {
                background-color: #20c997;
                color: white;
            }
            QPushButton:hover {
                background-color: #1ba87e;
            }
        """)
        self.upgrade_btn.clicked.connect(self._on_upgrade)
        self.upgrade_btn.setEnabled(False)
        btn_layout.addWidget(self.upgrade_btn)

        # 进度条
        self.update_progress = QProgressBar()
        self.update_progress.setVisible(False)

        layout.addLayout(info_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.update_progress)

        return panel

    # ========== 槽函数 ==========

    def _on_device_selected(self):
        """设备被选中时更新详情"""
        selected = self.device_table.selectedItems()
        if selected:
            row = selected[0].row()
            if row < len(self.devices):
                self.current_device = self.devices[row]
                self.update_device_details(self.current_device)
                self.connect_btn.setEnabled(True)
                self.pair_btn.setEnabled(not self.current_device.is_paired)

    def _on_connect(self):
        """连接按钮点击"""
        if self.current_device:
            self.connect_requested.emit(self.current_device)

    def _on_pair(self):
        """配对按钮点击"""
        if self.current_device:
            self.pair_requested.emit(self.current_device)

    def _on_check_update(self):
        """检查更新"""
        if self.current_device:
            # 模拟检查更新
            self.latest_version_label.setText("1.1.0")
            self.upgrade_btn.setEnabled(True)
            QMessageBox.information(self, "检查更新", "发现新版本 1.1.0")

    def _on_upgrade(self):
        """升级固件"""
        if self.current_device:
            self.update_firmware_requested.emit(self.current_device)

    # ========== 公共方法 ==========

    def update_device_list(self, devices):
        """更新设备列表"""
        self.devices = devices
        self.device_table.setRowCount(len(devices))

        for row, device in enumerate(devices):
            data = device.to_dict()
            for col, key in enumerate(data.keys()):
                item = QTableWidgetItem(str(data[key]))
                item.setTextAlignment(Qt.AlignCenter)

                # 状态列特殊颜色
                if key == "状态":
                    if device.status == DeviceStatus.CONNECTED:
                        item.setForeground(QColor("#28a745"))  # 绿色
                    elif device.status == DeviceStatus.ERROR:
                        item.setForeground(QColor("#dc3545"))  # 红色

                self.device_table.setItem(row, col, item)

    def update_device_details(self, device):
        """更新设备详情"""
        self.name_label.setText(device.name)
        self.address_label.setText(device.address)
        self.rssi_label.setText(f"{device.rssi} dBm")
        self.battery_bar.setValue(device.battery)
        self.firmware_label.setText(device.firmware_version)
        self.current_version_label.setText(device.firmware_version)

    def update_connection_status(self, connected, device_name=""):
        """更新连接状态"""
        if connected:
            self.status_label.setText(f"状态: 已连接到 {device_name}")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.scan_btn.setEnabled(False)
        else:
            self.status_label.setText("状态: 未连接")
            self.connect_btn.setEnabled(self.current_device is not None)
            self.disconnect_btn.setEnabled(False)
            self.scan_btn.setEnabled(True)

    def show_update_progress(self, value, total):
        """显示固件升级进度"""
        self.update_progress.setVisible(True)
        self.update_progress.setMaximum(total)
        self.update_progress.setValue(value)
        if value == total:
            QMessageBox.information(self, "升级完成", "固件升级成功！")
            self.update_progress.setVisible(False)