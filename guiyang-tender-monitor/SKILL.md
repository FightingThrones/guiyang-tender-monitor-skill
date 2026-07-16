---
name: guiyang-tender-monitor
description: Nationwide tender monitoring workflow for small and medium-sized companies. Finds software, IT, digitalization, platform development, O&M, cybersecurity, AI, mini-program, data, government procurement, hospital, university, SOE, and public-resource trading opportunities across China; generates Markdown/HTML/JSON daily reports and optional SMTP email delivery.
---

# National Tender Monitor

Use this skill to monitor nationwide tender and procurement opportunities suitable for small and medium-sized software, IT operations, system integration, and digitalization companies.

Although the skill name remains `guiyang-tender-monitor` for compatibility, the workflow now targets national opportunities. Guizhou/Guiyang is only one regional example, not the full scope.

## Primary Workflow

1. Run `scripts/tender_monitor.py`.
2. Review the generated Markdown, HTML, and JSON report in `reports/`.
3. If email delivery is requested, send the report with SMTP environment variables.
4. Prefer official source links when available; use aggregator links only as discovery leads.

## Script

Run from the repository root:

```powershell
python guiyang-tender-monitor/scripts/tender_monitor.py --output-dir ./reports --no-email
```

Useful options:

```powershell
python guiyang-tender-monitor/scripts/tender_monitor.py --limit-per-query 20 --no-email
python guiyang-tender-monitor/scripts/tender_monitor.py --recipient "your@email.com" --send-email
python guiyang-tender-monitor/scripts/tender_monitor.py --output-dir ./reports --send-email
```

## Email Configuration

The script sends mail only when these environment variables are set:

- `TENDER_SMTP_HOST`
- `TENDER_SMTP_PORT`
- `TENDER_SMTP_USER`
- `TENDER_SMTP_PASSWORD`
- Optional: `TENDER_DEFAULT_RECIPIENT`
- Optional: `TENDER_SMTP_FROM`
- Optional: `TENDER_SMTP_TLS` (`true` by default)

For QQ Mail, use the SMTP authorization code, not the login password.

## Search Scope

The default search scope covers:

- National government procurement and public resource trading platforms
- China Tendering and Bidding Public Service Platform style sources
- Universities, colleges, hospitals, disease control centers, and public institutions
- Local government, SOE, and public-service procurement channels
- Regional opportunities in Guizhou/Guiyang/Tongren/Sinan as one included subset

Priority terms:

- Software: `软件`, `系统`, `平台`, `信息化`, `运维`, `开发`, `定制开发`, `数字化`, `数据`, `AI`, `小程序`, `门户`, `接口`
- Procurement modes: `网上竞价`, `竞价`, `询价`, `询比`, `竞争性谈判`, `竞争性磋商`, `采购公告`, `招标公告`
- Buyer types: `政府采购`, `高校`, `学院`, `大学`, `医院`, `疾控`, `国企`, `事业单位`, `数据局`, `政务服务`
- SME-friendly signals: `中小企业`, `小微企业`, `价格扣除`, `专门面向中小企业`

## Reporting Rules

Rank opportunities higher when they:

- Match software/IT/digitalization/system/O&M keywords
- Are suitable for small or medium-sized companies
- Use online bidding, inquiry, inquiry comparison, competitive negotiation, or small competitive consultation
- Have future or still-active registration/deadline dates
- Come from official or semi-official procurement channels
- Are from colleges, hospitals, government departments, or local state-owned enterprises

Flag risks when:

- The deadline has passed
- The project appears to require special credentials such as equal protection assessment certification, secrecy qualification, construction/security integration, or manufacturer authorization
- The source is an aggregator and must be verified against the official announcement
- The project is mostly hardware, construction, logistics, property, canteen, medical consumables, or renovation work
