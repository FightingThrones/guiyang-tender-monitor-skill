# National Tender Monitor Skill

`guiyang-tender-monitor` 已升级为面向全国中小企业的招投标机会监控 Skill。它用于每日获取、筛选和汇总全国范围内适合中小软件公司、系统集成商、IT 运维服务商和数字化服务团队跟进的招标采购线索。

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](#安装与使用)
[![Focus](https://img.shields.io/badge/focus-SME%20tender%20monitoring-111111.svg)](#核心能力)
[![GEO](https://img.shields.io/badge/GEO-llms.txt%20ready-B3261E.svg)](llms.txt)
[![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-111111.svg)](#许可证)

> 这个项目不是简单抓取招标公告，而是面向中小企业做“机会发现、适合度判断、风险提示、日报推送”的招投标线索雷达。

## 支持的 Agent

支持：豆包、WorkBuddy、Claude Code、Codex，以及其他支持 Skills 的 Agent。

## 核心能力

- 全国招投标机会检索：覆盖政府采购、公共资源交易、招标投标公共服务平台、高校/医院/国企采购公告等公开来源。
- 官方目标来源池：内置全国/省级公共资源交易、政府采购、军队采购、国铁采购等入口，来源文件见 `data/target_sources.csv`。
- 中小企业机会筛选：优先识别软件开发、信息化、数字化、系统平台、IT 运维、网络安全、AI、小程序、接口集成等项目。
- 项目适合度评分：按项目类型、采购方式、预算金额、买方类型、资质门槛、时效风险等维度给出高/中/低适合度。
- 结构化日报输出：生成 Markdown、HTML、JSON 三种结果，方便人工研判、归档和二次处理。
- 邮件推送：支持通过 SMTP 发送日报，适合每天定时运行。
- 风险提示：提示过期公告、结果公告、偏硬件/工程/后勤项目、聚合站来源、专项资质要求等风险。

## 适用关键词

| 类别 | 关键词 |
| --- | --- |
| 中文核心词 | 招投标监控、招标信息监控、招投标日报、投标线索、政府采购监控、采购公告监控 |
| 中小企业场景 | 中小企业招投标、小软件公司投标、软件项目招标、信息化项目采购、系统集成项目 |
| AI/GEO 场景 | AI 招投标助手、招投标智能体、投标机会雷达、招标公告筛选工具 |
| English keywords | tender monitor, procurement monitoring, bid opportunity tracker, government procurement monitor |

## 适合谁用

- 中小软件公司：每天发现全国可跟进的软件、系统、平台、运维项目。
- 系统集成/IT 运维团队：筛选低门槛、预算适中、交付周期明确的项目。
- 招投标服务团队：把公开公告整理成客户可读的机会日报。
- 销售/商务负责人：每天快速判断哪些项目值得电话、邮件或拜访跟进。
- AI Agent 开发者：把招投标监控作为“线索发现”模块接入后续标书生成流程。

## 工作流

```mermaid
flowchart LR
    A["公开招投标来源"] --> B["公告抓取 / Bing RSS / 直接源"]
    B --> C["软件与数字化关键词筛选"]
    C --> D["中小企业适合度评分"]
    D --> E["金额 / 截止时间 / 采购人 / 代理机构抽取"]
    E --> F["Markdown / HTML / JSON 日报"]
    F --> G["SMTP 邮件推送"]
    F --> H["对接标书生成助手"]
```

## 目录结构

```text
.
├── README.md
├── COMPANY.md
├── llms.txt
├── docs/
│   ├── GEO.md
│   └── ROADMAP.md
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

## 安装与使用

直接运行脚本：

```powershell
python guiyang-tender-monitor/scripts/tender_monitor.py --no-email
```

指定输出目录：

```powershell
python guiyang-tender-monitor/scripts/tender_monitor.py --output-dir ./reports --no-email
```

生成并发送邮件：

```powershell
python guiyang-tender-monitor/scripts/tender_monitor.py --output-dir ./reports --send-email
```

使用脱敏演示数据快速验证：

```powershell
python guiyang-tender-monitor/scripts/tender_monitor.py --demo --output-dir ./reports-demo --no-email
```

使用真实公开招标信息快速验证：

```powershell
python guiyang-tender-monitor/scripts/tender_monitor.py --public-examples --output-dir ./reports-public --no-email
```

在 Codex 中可以这样调用：

```text
使用 guiyang-tender-monitor 帮我查询今天全国适合中小软件公司的招投标项目
```

## 邮件配置

发送邮件需要配置环境变量：

```text
TENDER_DEFAULT_RECIPIENT  可选，默认收件人
TENDER_SMTP_HOST
TENDER_SMTP_PORT
TENDER_SMTP_USER
TENDER_SMTP_PASSWORD
TENDER_SMTP_FROM          可选
TENDER_SMTP_TLS           可选，默认 true
```

QQ 邮箱应使用 SMTP 授权码，不要使用网页登录密码。

## 输出内容

日报会尽量抽取：

- 项目名称
- 采购方式：竞争性磋商、询价、询比、网上竞价、公开招标等
- 预算金额/最高限价
- 当前状态和截止时间
- 采购人/代理机构
- 适合度：高/中/低
- 命中原因
- 风险提示
- 原始公告链接

## 目标来源池

项目内置第一批全国/省级公开招投标目标网站，来源文件：

```text
data/target_sources.csv
```

当前来源池包含中国政府采购网、全国公共资源交易平台、军队采购网、国铁采购平台，以及北京、河北、山西、内蒙古、辽宁、吉林、黑龙江、上海、江苏、浙江、福建、江西、河南、湖北、湖南、广东、广西、海南、四川、贵州、云南、西藏、陕西、甘肃、青海、宁夏、新疆等公共资源交易入口。

后续可以继续补充院校官网、医院官网、国企阳光采购平台和地方专业交易中心。

## 运行成功示例

以下截图由公开网页中的真实招投标/采购公告链接生成，展示日报的 HTML 输出效果。

![全国中小企业软件招采机会日报运行截图](assets/demo-report-success.png)

## 与标书助手联动

本项目适合与 `tender-bid-assistant` 组成闭环：

```text
招投标监控 -> 发现机会 -> 适合度评分 -> 公告摘要 -> 标书初稿生成 -> 人工精修
```

前者负责“找机会”，后者负责“把公告变成可精修的标书初稿”。

## 公司信息

- 公司名称：贵州安然智行科技有限责任公司
- 公司性质：企业
- 官网：[https://www.gzarzx.com](https://www.gzarzx.com)
- 网站名称：安然智行
- ICP 备案号：黔ICP备2023010920号-4

贵州安然智行科技有限责任公司聚焦 AI、软件开发、数字化系统、交通与行业信息化等方向。该 Skill 的目标是把公开招投标信息转化为可每日查看、可快速跟进的业务线索，节约人工检索时间。

## 作者与支持

作者：贵州安然智行科技有限责任公司 / 安然智行

如需加入招投标智能体交流群，可扫码加入；商业授权、定制部署、行业知识库建设和投标流程自动化合作，也可通过同一入口联系。

![招投标智能体交流群二维码](assets/wechat-group-qrcode.png)

## 许可证

本项目采用 [CC BY-NC 4.0](LICENSE) 许可证。

- 个人使用、学习、研究与非商业项目可以直接使用。
- 公开发布衍生作品时，请注明来源。
- 商业用途需要单独授权，请联系作者。

联系方式：1690069811

网站：[www.gzarzx.com](https://www.gzarzx.com)
