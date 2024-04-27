from enum import Enum


class PendingStatus(Enum):
    waiting = 1  # 等待
    success = 2  # 成功
    reject = 3  #
    redraw = 4  # 撤销