"""
设备数据模型 - 纯粹的数据类
"""
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional


class DeviceStatus(Enum):
    """设备状态枚举"""
    DISCONNECTED = "😴未连接"
    SCANNING = "🤔扫描中"
    CONNECTING = "🧐连接中"
    CONNECTED = "😋已连接"
    PAIRED = "🤗已配对"
    UPDATING = "🤤升级中"
    ERROR = "😇出错了喵"


@dataclass
class EMGDevice:
    """肌电设备数据类"""
    name: str
    address: str  # 蓝牙地址
    rssi: int = -60  # 信号强度
    battery: int = 100  # 电池电量 0-100%
    status: DeviceStatus = DeviceStatus.DISCONNECTED
    firmware_version: str = "1.0.0"
    last_seen: Optional[datetime] = None
    is_paired: bool = False

    def to_dict(self):
        """转换为字典（用于表格显示）"""
        return {
            "设备名称": self.name,
            "信号强度": f"{self.rssi} dBm",
            "电量": f"{self.battery}%",
            "固件版本": self.firmware_version,
            "状态": self.status.value,
            "配对状态": "已配对" if self.is_paired else "未配对"
        }