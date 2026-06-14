# 流水线生产模拟器 - Factory Pipeline Simulator

一个基于 Python 和 Pygame 的流水线生产模拟小游戏。玩家需要将传送带上不断出现的零件，快速准确地拖拽到对应的工位进行处理。

## 目录结构

```
label-059/
├── game/
│   ├── __init__.py          # 包初始化
│   ├── config.py            # 游戏配置（参数、颜色、零件/工位定义）
│   ├── part.py              # 零件类（渲染、拖拽、碰撞检测）
│   ├── conveyor.py          # 传送带类（渲染、动画）
│   ├── station.py           # 工位类（渲染、逻辑判断）
│   ├── task_manager.py      # 任务管理核心（任务CRUD、状态流转）
│   ├── ui_components.py     # UI组件（按钮、输入框、下拉框、任务卡片）
│   └── game.py              # 游戏主循环（状态管理、核心逻辑）
├── main.py                  # 游戏入口
├── start.bat                # Windows 启动脚本
├── requirements.txt         # 依赖清单
├── PROMPT.md                # 需求文档
└── README.md                # 本文件
```

## 快速开始

### 环境要求
- Python 3.8 或更高版本
- pygame >= 2.5.0

### 一键启动（Windows）

双击运行 `start.bat` 即可自动检查环境、安装依赖并启动游戏。

### 手动启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动游戏
python main.py
```

## 游戏玩法

### 核心机制
1. **传送带**：零件从左侧不断出现，随传送带向右移动
2. **零件种类**：齿轮、螺丝、电路板、芯片、包装盒、标签
3. **三个工位**：
   - 🔵 **组装工位**：处理齿轮、螺丝
   - 🟢 **质检工位**：处理电路板、芯片
   - 🟠 **包装工位**：处理包装盒、标签
4. **得分规则**：
   - 放对位置：+10 分
   - 放错位置：-15 分，零件退回传送带
   - 漏掉零件：不计分，但消耗生命值
5. **难度递增**：随着时间推移，零件生成速度和移动速度会越来越快
6. **生命值**：最多允许漏掉 10 个零件，超过则游戏结束

### 操作方式

| 操作 | 说明 |
|------|------|
| 鼠标左键拖拽 | 拖拽零件到对应工位 |
| 鼠标左键点击 + 数字键 | 点击选中零件后，按 1/2/3 放到对应工位 |
| ESC | 暂停游戏 |
| T | 打开任务管理中心 |
| 空格 / 回车 | 开始游戏 / 重新开始 |
| R | 重新开始（暂停/结束时） |
| M | 返回主菜单（暂停/结束时） |

## 任务管理系统

游戏内置完整的任务管理系统，按 `T` 键打开任务管理中心。

### 核心功能

#### 1. 任务创建
- 设置任务名称和描述
- 选择关联工位（组装/质检/包装/不限）
- 设置优先级（高/中/低）
- 设置目标完成数量

#### 2. 任务编辑
- 可修改任务的所有属性
- 支持随时调整目标和优先级

#### 3. 状态流转
任务支持以下状态：
- ⚪ **待处理 (Pending)**：任务已创建，尚未开始
- 🔵 **进行中 (In Progress)**：任务正在执行
- 🟢 **已完成 (Completed)**：任务已达成目标
- 🔴 **已取消 (Cancelled)**：任务被取消

可以通过任务卡片上的下拉框手动切换状态。

#### 4. 任务删除
- 点击任务卡片上的"删除"按钮移除任务

#### 5. 列表筛选
支持多维度筛选和排序：
- **状态筛选**：全部/待处理/进行中/已完成/已取消
- **优先级筛选**：全部/高/中/低
- **工位筛选**：全部/组装/质检/包装
- **排序方式**：创建时间/更新时间/优先级/状态/进度

### 任务进度跟踪
- 游戏中处理零件时，关联的进行中任务会自动累计进度
- 任务卡片实时显示进度条和完成百分比
- 达成目标后任务自动标记为已完成

## 模块架构说明

代码采用模块化设计，各模块职责清晰，便于迭代扩展：

### 1. 配置层 - [config.py](file:///d:/proje/label-059/game/config.py)
集中管理所有游戏参数：
- 屏幕尺寸、帧率
- 颜色定义
- 传送带、工位、零件的尺寸和位置
- 游戏平衡参数（速度、分数、生命值等）
- 零件类型和对应工位配置

### 2. 游戏对象层
- **[part.py](file:///d:/proje/label-059/game/part.py)**：零件实体，负责自身渲染、拖拽逻辑、动画
- **[conveyor.py](file:///d:/proje/label-059/game/conveyor.py)**：传送带渲染和动画
- **[station.py](file:///d:/proje/label-059/game/station.py)**：工位实体，判断零件是否匹配

### 3. 业务逻辑层
- **[task_manager.py](file:///d:/proje/label-059/game/task_manager.py)**：纯业务逻辑，不依赖 Pygame
  - `Task` 类：任务数据模型
  - `TaskManager` 类：任务管理核心，提供完整 CRUD 和查询接口

### 4. UI 组件层 - [ui_components.py](file:///d:/proje/label-059/game/ui_components.py)
可复用的 UI 组件：
- `UIComponent`：基类，定义组件接口
- `Button`：通用按钮
- `InputBox`：文本输入框
- `Dropdown`：下拉选择框
- `TaskCard`：任务卡片组件
- `TaskManagerUI`：任务管理中心界面

### 5. 游戏控制层 - [game.py](file:///d:/proje/label-059/game/game.py)
游戏主控制器：
- 管理游戏状态（菜单/游戏中/暂停/结束/任务管理）
- 事件分发和处理
- 游戏循环更新逻辑
- 渲染控制

### 6. 入口层 - [main.py](file:///d:/proje/label-059/main.py)
程序入口，负责初始化 Pygame 和启动游戏。

## 扩展开发指南

### 添加新零件类型

1. 在 [config.py](file:///d:/proje/label-059/game/config.py) 的 `PART_TYPES` 中添加配置：
```python
'new_part': {
    'name': '新零件',
    'color': (R, G, B),
    'target_station': 'assembly',  # 目标工位
    'shape': 'new_shape'            # 渲染形状标识
}
```

2. 在 [part.py](file:///d:/proje/label-059/game/part.py) 的 `draw()` 方法中添加对应形状的渲染逻辑：
```python
elif self.shape == 'new_shape':
    self._draw_new_shape(surface, x, y, size)
```

### 添加新工位

1. 在 [config.py](file:///d:/proje/label-059/game/config.py) 的 `STATION_TYPES` 中添加配置。

2. 在 [station.py](file:///d:/proje/label-059/game/station.py) 的 `_draw_content()` 中添加对应图标渲染。

3. 在 [game.py](file:///d:/proje/label-059/game/game.py) 的 `_init_stations()` 中注册新工位。

### 修改游戏平衡参数

所有游戏参数都集中在 [config.py](file:///d:/proje/label-059/game/config.py) 中，可以方便地调整：
- `INITIAL_SPEED` / `MAX_SPEED`：速度范围
- `SCORE_CORRECT` / `SCORE_WRONG`：得分规则
- `MAX_MISSED_PARTS`：生命值
- `SPAWN_INTERVAL_START` / `SPAWN_INTERVAL_MIN`：零件生成间隔

## 技术特点

1. **模块化设计**：各模块职责单一，耦合度低，便于测试和迭代
2. **状态机模式**：游戏状态清晰，状态切换逻辑明确
3. **组件化 UI**：UI 组件可复用，易于扩展新界面
4. **配置驱动**：所有参数集中管理，平衡性调整方便
5. **任务系统**：完整的 CRUD 和状态流转，支持游戏内目标管理

## 许可证

本项目仅供学习和娱乐使用。
