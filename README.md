# 校园招聘数据分析平台

一个基于FastAPI和现代前端技术的校园招聘数据分析平台，用于处理校园招聘签约名单Excel文件，实现数据解析、统计计算及可视化展示。

## ✨ 主要功能

### 🔐 安全认证
- **密码保护**: 应用级别的访问控制
- **会话管理**: 安全的用户会话
- **登录界面**: 美观的身份验证页面
- **自动登出**: 安全的退出机制

### 📊 数据分析
- **Excel文件上传**: 支持.xlsx/.xls格式
- **数据预处理**: 自动清洗和标准化
- **统计分析**: 多维度数据统计
- **趋势分析**: 时间序列分析

### 📈 可视化图表
- **招聘趋势图**: 时间维度分析
- **地域分布图**: 招聘地点热力图
- **薪资分析图**: 薪资水平分布
- **岗位分类图**: 职位类别统计
- **学历要求图**: 教育背景分析

### 📋 报告生成
- **PDF报告**: 专业格式报告
- **数据导出**: 支持多种格式
- **自定义模板**: 可配置报告样式
- **批量处理**: 支持多文件处理

### 🔧 系统特性
- **容器化部署**: Docker支持，一键部署
- **响应式设计**: 适配各种设备
- **实时处理**: 快速数据分析
- **错误处理**: 完善的异常处理
- **日志记录**: 详细的操作日志
- **配置管理**: 灵活的系统配置
- **性能优化**: 高效的数据处理
- **安全性**: 多层安全保护
- **可扩展性**: 模块化架构设计
- **用户体验**: 直观的操作界面
- **生产就绪**: Nginx反向代理支持

## 技术架构

### 后端技术栈
- **框架**: FastAPI (高性能异步Web框架)
- **数据处理**: Pandas (Excel文件解析和数据分析)
- **文件处理**: OpenPyXL (Excel文件读写)
- **API文档**: 自动生成的OpenAPI文档
- **包管理**: uv (现代Python包管理工具)

### 前端技术栈
- **基础**: HTML5 + 原生JavaScript
- **样式**: TailwindCSS 3.0+ (实用优先的CSS框架)
- **图表**: Apache ECharts (强大的数据可视化库)
- **图标**: Font Awesome 6.4.0 (丰富的图标库)
- **设计**: 响应式设计，移动端友好

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

#### 环境要求
- Docker Desktop 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存

#### 快速启动
```bash
# Windows
.\deploy.ps1 start

# Linux/macOS
./deploy.sh start

# 或使用 docker-compose
docker-compose up -d
```

#### 生产环境部署
```bash
# Windows
.\deploy.ps1 start -Production

# Linux/macOS
./deploy.sh start --production
```

### 方式二：本地开发环境

#### 环境要求
- Python 3.9+
- uv 包管理器
- Windows 10/11 (推荐)

#### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd 2025-06-10CampusTalentInsight
   ```

2. **安装依赖**
   ```bash
   # 使用 uv 安装依赖
   uv sync
   ```

3. **启动应用**
   ```bash
   # Windows
   .\start.ps1
   
   # 或者直接运行
   python main.py
   ```

4. **访问应用**
   - 打开浏览器访问: http://localhost:8000
   - 上传Excel文件开始分析

## 🐳 Docker 部署详细说明

### 快速部署命令

```bash
# Windows PowerShell
.\deploy.ps1 start                    # 开发环境
.\deploy.ps1 start -Production        # 生产环境
.\deploy.ps1 start -Build             # 重新构建

# Linux/macOS Bash
./deploy.sh start                     # 开发环境
./deploy.sh start --production        # 生产环境
./deploy.sh start --build             # 重新构建

# 直接使用 Docker Compose
docker-compose up -d                  # 开发环境
docker-compose --profile production up -d  # 生产环境
```

### 管理命令

```bash
# 查看状态
.\deploy.ps1 status     # Windows
./deploy.sh status      # Linux/macOS

# 查看日志
.\deploy.ps1 logs       # Windows
./deploy.sh logs        # Linux/macOS

# 停止服务
.\deploy.ps1 stop       # Windows
./deploy.sh stop        # Linux/macOS

# 数据备份
.\deploy.ps1 backup     # Windows
./deploy.sh backup      # Linux/macOS
```

### 生产环境特性

- **Nginx 反向代理**: 提供负载均衡和静态文件服务
- **健康检查**: 自动监控应用状态
- **数据持久化**: 自动备份上传文件和配置
- **SSL 支持**: 可配置 HTTPS 证书
- **性能优化**: Gzip 压缩和缓存策略

详细部署文档请参考: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
## 使用指南

### 1. 文件上传
- 点击"文件上传"标签页
- 选择符合格式要求的Excel文件
- 填写情况说明(必填，500字以内)
- 点击"上传并分析"按钮

### 2. 数据表格查看
- 上传成功后，切换到"数据表格"标签页
- 查看7个维度的统计表格
- 数据实时更新，支持排序和筛选

### 3. 图表看板分析
- 切换到"图表看板"标签页
- 查看顶部数字卡片统计
- 浏览各类饼图和柱状图
- 查看重点院校人才统计文本

## Excel文件格式要求

### 必需字段
文件必须包含以下14个字段：

| 字段名 | 说明 | 示例 |
|--------|------|------|
| 序号 | 记录序号 | 1, 2, 3... |
| 姓名 | 学生姓名 | 张三 |
| 性别 | 性别信息 | 男/女 |
| 年龄 | 年龄 | 23 |
| 出生日期 | 出生日期 | 2000-01-01 |
| 政治面貌 | 政治面貌 | 中共党员/共青团员 |
| 籍贯 | 籍贯信息 | 江西省-萍乡市 |
| 应聘状态 | 签约状态 | 两方协议/三方协议 |
| 应聘职位 | 应聘职位 | 软件工程师 |
| 最高学历 | 学历层次 | 本科/硕士/博士 |
| 最高学历专业 | 专业名称 | 计算机科学与技术 |
| 专业类型 | 专业分类 | 工学/理学 |
| 最高学历毕业院校 | 毕业院校 | 清华大学 |
| 最高学历毕业院校类别 | 院校类别 | C9联盟/985/211 |

### 数据增强规则

系统会自动生成以下衍生字段：

1. **是否为海外院校**: 根据院校类别是否包含"海外院校"判断
2. **院校类别分类**: 按优先级排序(QS1-50 > QS100 > C9联盟 > 985 > 211...)
3. **籍贯省份**: 提取籍贯中"-"前的省份信息
4. **出生年代**: 根据出生日期划分为90后/95后/00后/05后

## API接口文档

### 上传文件
```http
POST /api/upload
Content-Type: multipart/form-data

file: Excel文件
description: 情况说明文本
```

### 获取统计数据
```http
GET /api/statistics
```

### 获取上传历史
```http
GET /api/upload-history
```

完整的API文档可在启动服务后访问: http://localhost:8000/docs

## 项目结构

```
2025-06-10CampusTalentInsight/
├── main.py                 # 主应用文件
├── pyproject.toml         # 项目配置和依赖
├── README.md              # 项目说明文档
├── static/                # 静态资源目录
│   ├── index.html         # 前端主页面
│   ├── tailwind.min.css   # TailwindCSS样式
│   ├── echarts.min.js     # ECharts图表库
│   └── fontawesome/       # FontAwesome图标
│       ├── css/
│       └── webfonts/
├── uploads/               # 上传文件存储目录
└── 2025届校园招聘-外发制作数据看板.xlsx  # 示例数据文件
```

## 开发指南

### 代码规范
- 使用Black进行代码格式化
- 使用MyPy进行类型检查
- 使用Flake8进行代码质量检查
- 注释覆盖率≥30%

### 运行测试
```bash
# 代码格式化
uv run black .

# 类型检查
uv run mypy main.py

# 代码质量检查
uv run flake8 main.py

# 运行测试
uv run pytest
```

### 性能优化
- 图片使用WebP格式并压缩
- 实现懒加载（滚动至视口1/2时加载）
- 首屏加载时间<1.5s
- 响应式设计，移动端友好

## 浏览器兼容性

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 许可证

MIT License

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues]()

---

**注意**: 本项目仅用于教育和学习目的，请确保在使用时遵守相关的数据隐私和安全规定。