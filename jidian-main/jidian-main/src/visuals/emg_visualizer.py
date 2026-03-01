import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QGroupBox, QLabel, QComboBox, QPushButton, QListView, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg

class EMGVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- 1. 初始化数据存储 ---
        self.data_points = 200 # 显示的采样点数
        self.x = list(range(self.data_points))
        self.y = [0 for _ in range(self.data_points)]
        self.current_amplitude = 1.0 # 初始模拟振幅
        
        # --- 2. 初始化 UI ---
        self.init_ui()
        
        # --- 3. 启动“发动机”：定时器 ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50) # 每 50 毫秒刷新一次 (20Hz)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 1. 标题
        title = QLabel("数据可视化中心")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #343a40;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 2. 控制面板
        control_group = QGroupBox("控制面板")
        control_layout = QHBoxLayout(control_group)
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["实时数据", "最近1分钟", "最近5分钟", "最近1小时"])
        self.time_range_combo.setFixedWidth(180)
        self.time_range_combo.setView(QListView())
        self.time_range_combo.setStyleSheet("""
            QComboBox QAbstractItemView::item { min-height: 45px; padding-left: 10px; }
        """)

        self.refresh_btn = QPushButton("🔄 重置视图")
        self.refresh_btn.setFixedWidth(120)
        self.refresh_btn.clicked.connect(self.reset_data) # 绑定重置逻辑
        
        control_layout.addWidget(QLabel("时间范围:"))
        control_layout.addWidget(self.time_range_combo)
        control_layout.addStretch()
        control_layout.addWidget(self.refresh_btn)
        layout.addWidget(control_group)

        # 3. 波形图 (核心)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setYRange(-10, 10) # 固定 Y 轴范围，防止波形乱跳
        self.curve = self.plot_widget.plot(pen=pg.mkPen('#17a2b8', width=2))
        layout.addWidget(self.plot_widget, stretch=1)

        # 4. 状态栏 (动态显示分类结果)
        self.status_label = QLabel("正在初始化信号...")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 20px; 
                font-weight: bold;
                color: white; 
                background-color: #28a745; 
                padding: 12px; 
                border-radius: 8px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    # --- 核心逻辑：更新波形 ---
    def update_plot(self):
        """每隔 50ms 被调用一次，产生波动效果"""
        # 1. 模拟状态随机切换（演示分类效果）
        if random.random() > 0.98:
            states = [
                ("💪 肌肉收缩 (运动中)", "#007bff", 7.0),
                ("🧘 肌肉放松 (静止)", "#28a745", 1.2),
                ("⚠️ 检测到疲劳", "#dc3545", 3.5)
            ]
            text, color, amp = random.choice(states)
            self.status_label.setText(text)
            self.status_label.setStyleSheet(f"font-size:20px; font-weight:bold; color:white; background-color:{color}; padding:12px; border-radius:8px;")
            self.current_amplitude = amp

        # 2. 生成新的数据点（模拟 EMG 信号的高频随机性）
        new_value = random.uniform(-self.current_amplitude, self.current_amplitude)
        
        # 3. 更新数据列表 (滚动效果)
        self.y = self.y[1:] + [new_value]
        
        # 4. 重新绘制曲线
        self.curve.setData(self.x, self.y)

    def reset_data(self):
        """重置数据"""
        self.y = [0 for _ in range(self.data_points)]
        self.curve.setData(self.x, self.y)
        QMessageBox.information(self, "提示", "波形显示已重置。")