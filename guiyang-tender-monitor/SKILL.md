---
name: guiyang-tender-monitor
description: Daily monitoring workflow for finding Guizhou tenders, especially Guiyang, Tongren, and Sinan County, including bidding, inquiry, competitive negotiation, competitive consultation, online bidding, and small procurement opportunities suitable for a small software development company. Use when asked to search, monitor, summarize, or email Guizhou/Guiyang/Tongren/Sinan software, IT, digitalization, platform, system development, O&M, cybersecurity, college, hospital, government, or state-owned-enterprise procurement opportunities.
---

# Guiyang Tender Monitor

Use this skill to monitor concrete procurement opportunities in Guizhou, especially Guiyang, Tongren, and Sinan County, for a small software development company.

## Primary Workflow

1. Run `scripts/tender_monitor.py`.
2. Review the generated Markdown report in `reports/`.
3. If email delivery is requested, send the report with SMTP environment variables.
4. Prefer official source links when available; use aggregator links only as discovery leads.

## Script

Run from any directory:

```powershell
python "C:\Users\Administrator\.agents\skills\guiyang-tender-monitor\scripts\tender_monitor.py" --send-email
```

Useful options:

```powershell
python "...\tender_monitor.py" --days 14 --no-email
python "...\tender_monitor.py" --recipient "1690069811@qq.com" --send-email
python "...\tender_monitor.py" --output-dir "H:\常规临时任务\招投标日报"
```

## Email Configuration

The script sends mail only when these environment variables are set:

- `TENDER_SMTP_HOST`
- `TENDER_SMTP_PORT`
- `TENDER_SMTP_USER`
- `TENDER_SMTP_PASSWORD`
- Optional: `TENDER_SMTP_FROM`
- Optional: `TENDER_SMTP_TLS` (`true` by default)

For QQ Mail, use the SMTP authorization code, not the login password.

## Search Scope

The default search scope covers:

- Guizhou and Guiyang public resource/government procurement platforms
- Tongren city and Sinan County government procurement/public resource channels
- Universities and colleges in Guiyang/Guizhou
- Hospitals, disease control centers, and health institutions
- State-owned enterprise procurement platforms such as Qianyun/Zhaocai and Guiyang SOE procurement
- Public tender service platforms and local agency sites
- Discovery aggregators for lead generation

Priority terms:

- Software: `软件`, `系统`, `平台`, `信息化`, `运维`, `开发`, `定制开发`, `数字化`, `数据`, `AI`, `小程序`, `门户`, `接口`
- Procurement modes: `网上竞价`, `竞价`, `询价`, `询比`, `竞争性谈判`, `竞争性磋商`, `采购公告`
- Target buyers: `贵阳`, `铜仁`, `思南`, `思南县`, `贵州`, `高校`, `学院`, `大学`, `医院`, `疾控`, `国企`

## Reporting Rules

Rank opportunities higher when they:

- Are located in Guiyang or Guizhou
- Are located in Tongren or Sinan County
- Match software/IT/digitalization/system/O&M keywords
- Use online bidding, inquiry, inquiry comparison, competitive negotiation, or small competitive consultation
- Are below roughly 500,000 RMB
- Are from colleges, hospitals, government departments, or local state-owned enterprises
- Have future or still-active registration/deadline dates

Flag risks when:

- The deadline has passed
- The project appears to require special credentials such as equal protection assessment certification, secrecy qualification, construction/security integration, or manufacturer authorization
- The source is an aggregator and must be verified against the official announcement
