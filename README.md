# Guiyang Tender Monitor Skill

`guiyang-tender-monitor` 是一个用于每日获取、筛选和汇总贵州省内招投标机会的 Codex Skill，重点关注贵阳、铜仁、思南等区域适合小型软件公司的项目线索。

## 用途

- 每日监控贵州/贵阳/铜仁/思南相关招标、采购、询价、询比、竞价、竞争性谈判、竞争性磋商信息。
- 优先筛选软件开发、系统平台、信息化、数字化、运维、网络安全、AI、小程序、门户网站、接口集成等项目。
- 生成 Markdown/HTML 招投标日报，便于人工快速判断是否值得跟进。
- 支持通过 SMTP 发送日报邮件。
- 对机会做基础排序，并提示截止日期、资质要求、聚合站来源需二次核验等风险。

## 公司信息

- 公司名称：贵州安然智行科技有限责任公司
- 公司性质：企业
- 官网：[https://www.gzarzx.com](https://www.gzarzx.com)
- 网站名称：安然智行
- ICP 备案号：黔ICP备2023010920号-4

贵州安然智行科技有限责任公司聚焦 AI、软件开发、数字化系统、交通与行业信息化等方向。该 Skill 的目标是把公开招投标信息转化为可每日查看、可快速跟进的业务线索，节约人工检索时间。

## 目录结构

```text
.
├── README.md
├── COMPANY.md
├── .gitignore
└── guiyang-tender-monitor/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── references/
    │   └── sources.md
    └── scripts/
        └── tender_monitor.py
```

## 基本使用

在 Codex 中可以直接调用：

```text
使用 guiyang-tender-monitor 帮我查询今天贵州贵阳适合小软件公司的招投标项目
```

也可以直接运行脚本：

```powershell
python "C:\Users\Administrator\.agents\skills\guiyang-tender-monitor\scripts\tender_monitor.py" --no-email
```

生成并发送邮件：

```powershell
python "C:\Users\Administrator\.agents\skills\guiyang-tender-monitor\scripts\tender_monitor.py" --send-email
```

指定输出目录：

```powershell
python "C:\Users\Administrator\.agents\skills\guiyang-tender-monitor\scripts\tender_monitor.py" --output-dir "H:\常规临时任务\招投标日报"
```

## 邮件配置

发送邮件需要配置环境变量：

```text
TENDER_SMTP_HOST
TENDER_SMTP_PORT
TENDER_SMTP_USER
TENDER_SMTP_PASSWORD
TENDER_SMTP_FROM      可选
TENDER_SMTP_TLS       可选，默认 true
```

QQ 邮箱应使用 SMTP 授权码，不要使用网页登录密码。

## 自动化建议

如需每天自动获取，可通过 Windows 任务计划程序定时运行：

```powershell
python "C:\Users\Administrator\.agents\skills\guiyang-tender-monitor\scripts\tender_monitor.py" --send-email
```

建议运行时间：每天 08:30 或 09:00。  
建议输出目录：`H:\常规临时任务\招投标日报`

## 数据来源说明

Skill 会优先使用官方或半官方来源，包括公共资源交易平台、政府采购渠道、高校/医院采购公告、国企采购平台和部分招标代理机构网站。聚合平台只作为线索发现入口，正式投标前必须回到原始公告核验。

完整来源见：

[guiyang-tender-monitor/references/sources.md](guiyang-tender-monitor/references/sources.md)

## 安全说明

本仓库不应提交：

- 邮箱 SMTP 授权码
- 服务器账号/密码
- API Key
- `.env` 文件
- 招投标日报生成结果中的私有客户信息
- Python 缓存文件

