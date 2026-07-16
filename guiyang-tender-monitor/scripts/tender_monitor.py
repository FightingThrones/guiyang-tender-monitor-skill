#!/usr/bin/env python3
"""Monitor nationwide SME-friendly tender opportunities and optionally email a report."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import email.message
import html
import json
import os
import re
import smtplib
import ssl
import sys
import textwrap
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
try:
    import winreg
except ImportError:  # pragma: no cover
    winreg = None


DEFAULT_RECIPIENT = os.getenv("TENDER_DEFAULT_RECIPIENT", "")
DEFAULT_OUTPUT_DIR = Path("reports")
REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET_SOURCES_CSV = REPO_ROOT / "data" / "target_sources.csv"

SOFTWARE_TERMS = [
    "软件", "系统", "平台", "信息化", "运维", "开发", "定制开发", "数字化",
    "大数据", "数据", "AI", "人工智能", "小程序", "门户", "接口", "网络安全",
    "等保", "测评", "校园网", "认证", "档案数字化",
]

MODE_TERMS = [
    "网上竞价", "竞价", "询价", "询比", "竞争性谈判", "竞争性磋商",
    "采购公告", "磋商公告", "谈判公告", "询比采购公告",
]

BUYER_TERMS = [
    "高校", "学院", "大学", "医院", "疾控", "教育局", "人社", "国企", "公共资源", "招采",
    "政府采购", "事业单位", "中小企业", "小微企业", "科技局", "工信", "政务服务", "数据局",
]

REGION_TERMS = [
    "全国", "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
    "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南", "广东",
    "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "内蒙古", "广西", "西藏",
    "宁夏", "新疆", "香港", "澳门", "台湾", "贵阳", "铜仁", "思南", "深圳", "广州",
    "杭州", "南京", "成都", "武汉", "西安", "长沙", "郑州", "合肥", "南昌", "昆明",
]

HARDWARE_NOISE_TERMS = [
    "热水系统", "空气源", "窗帘", "垃圾清运", "家具", "仪器", "设备采购",
    "小型设备", "搬迁", "服装", "工作服", "医用耗材", "试剂", "装修",
    "改造工程", "绿化", "保洁", "物业", "体检", "食堂", "电梯",
    "道闸", "门禁", "热泵",
]

NON_PROJECT_TERMS = [
    "直接源抓取失败", "同步至", "通知", "成交公告", "中标公告", "结果公告", "废标公告", "流标公告",
]

OFFICIAL_DOMAINS = [
    "ccgp.gov.cn",
    "ggzy.gov.cn",
    "cebpubservice.com",
    "chinabidding.com.cn",
    "ctbpsp.com",
    "plap.mil.cn",
    "ggzy.guizhou.gov.cn",
    "ggzy.guiyang.gov.cn",
    "ggzy.gov.cn",
    "gzu.edu.cn",
    "gyu.edu.cn",
    "gufe.edu.cn",
    "gznc.edu.cn",
    "gmc.edu.cn",
    "gzy.edu.cn",
    "gzqy.cn",
    "gzscdc.org.cn",
    "gzsdsrmyy.cn",
    "chinamae.com",
    "prechina.net",
    "ygzcfwy.net",
    "gzbpa.org.cn",
    "gzxyld.cn",
    "gzwh.com",
    "e-gzwh.com",
    "gzgczb.cn",
    "plap.mil.cn",
    "cg.gt.cn",
    "trggzy.cn",
    "trs.gov.cn",
    "sinan.gov.cn",
    "gztrc.edu.cn",
    "trzy.edu.cn",
    "trsrmyy.cn",
    "trsdermyy.com",
]

DIRECT_SOURCES = [
    ("中国政府采购网", "http://www.ccgp.gov.cn/cggg/dfgg/"),
    ("全国公共资源交易平台", "http://www.ggzy.gov.cn/information/html/a/"),
    ("中国招标投标公共服务平台", "https://www.cebpubservice.com/"),
    ("军队采购网", "https://www.plap.mil.cn/"),
    ("贵阳学院招标采购", "https://www.gyu.edu.cn/xwzl/zbcg.htm"),
    ("贵州财经大学招标采购", "https://www.gufe.edu.cn/index/zbcg.htm"),
    ("贵州师范学院学校采购", "https://www.gznc.edu.cn/"),
    ("贵州医科大学招标采购", "https://www.gmc.edu.cn/xwzx/zbcg.htm"),
    ("贵州中医药大学国资处", "https://gzc.gzy.edu.cn/"),
    ("贵州轻工职业大学", "https://www.gzqy.cn/"),
    ("贵州省疾控中心招标采购", "https://www.gzscdc.org.cn/xxgk/zbcg"),
    ("贵州省第三人民医院招标信息", "https://gzsdsrmyy.cn/pagePc/page6/4.html"),
    ("铜仁学院采购招标", "https://www.gztrc.edu.cn/xxgk/cgzb.htm"),
    ("铜仁学院招投标专栏", "https://www.gztrc.edu.cn/cwc/ztbzl.htm"),
    ("铜仁职业技术学院招标采购", "https://www.trzy.edu.cn/"),
    ("思南县政府采购招标公告", "https://www.sinan.gov.cn/zwgk/zdlygk/zfcg_5777742/zbgg_5777743/"),
    ("铜仁市第二人民医院通知通告", "https://www.trsdermyy.com/index.php?a=lists&c=index&catid=67&m=content"),
    ("铜仁市公共资源交易中心", "https://www.trggzy.cn/"),
    ("贵州贵财招标", "https://www.gzgczb.cn/ArticleList.aspx?ClassCode=JZXCS"),
    ("贵州卫虹招标", "https://www.e-gzwh.com/Bidding/"),
    ("贵州兴业利达", "https://www.gzxyld.cn/"),
    ("贵州阳光产权交易所", "https://www.prechina.net/project/projectlist.html"),
]


def load_target_sources(path: Path = TARGET_SOURCES_CSV) -> list[tuple[str, str]]:
    if not path.exists():
        return []
    sources: list[tuple[str, str]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                name = (row.get("name") or "").strip()
                url = (row.get("url") or "").strip()
                if name and url:
                    sources.append((name, url))
    except Exception:
        return []
    return sources


def source_pool() -> list[tuple[str, str]]:
    seen: set[str] = set()
    sources: list[tuple[str, str]] = []
    for name, url in load_target_sources() + DIRECT_SOURCES:
        key = normalize_url(url)
        if key and key not in seen:
            seen.add(key)
            sources.append((name, url))
    return sources


def official_domains() -> set[str]:
    domains = set(OFFICIAL_DOMAINS)
    for _, url in load_target_sources():
        netloc = urllib.parse.urlparse(url).netloc.lower()
        if netloc:
            domains.add(netloc)
    return domains

SEARCH_QUERIES = [
    '"软件开发" "竞争性磋商公告" 2026 采购',
    '"信息化" "竞争性磋商公告" 2026 采购',
    '"系统运维" "采购公告" 2026',
    '"数字化" "询比采购公告" 2026',
    '"数据治理" "竞争性磋商" 2026',
    '"网络安全" "询价公告" 2026',
    '"小程序" "采购公告" 2026',
    '"AI" "采购公告" "软件" 2026',
    '"政务服务" "系统" "竞争性磋商公告" 2026',
    '"高校" "平台" "竞争性磋商公告" 2026',
    '"医院" "信息化" "竞争性磋商公告" 2026',
    '"国企" "软件" "询比采购" 2026',
    'site:ccgp.gov.cn "软件开发" "竞争性磋商公告" "2026"',
    'site:ccgp.gov.cn "信息化" "采购公告" "2026"',
    'site:ggzy.gov.cn "软件" "采购公告" "2026"',
    'site:cebpubservice.com "系统" "招标公告" "2026"',
    'site:ggzy.guizhou.gov.cn "软件" "竞争性磋商公告" "2026"',
    'site:ggzy.guiyang.gov.cn "软件" "采购公告" "2026"',
    'site:gmc.edu.cn "采购公告" "软件" "2026"',
    'site:gyu.edu.cn "系统" "竞争性磋商公告" "2026"',
    'site:gznc.edu.cn "平台" "竞争性磋商公告" "2026"',
    'site:gufe.edu.cn "系统" "竞争性磋商公告" "2026"',
    '"铜仁" "软件" "竞争性磋商公告" 2026 采购',
    '"铜仁市" "系统" "采购公告" 2026',
    '"思南县" "软件" "竞争性磋商" 2026',
    '"思南县" "信息化" "采购公告" 2026',
    '"铜仁学院" "系统" "竞争性磋商公告" 2026',
    '"铜仁职业技术学院" "软件" "采购公告" 2026',
    '"铜仁市人民医院" "信息化" "软件" "采购公告" 2026',
    'site:sinan.gov.cn "采购公告" "软件" "2026"',
    'site:gztrc.edu.cn "系统" "竞争性磋商公告" "2026"',
    'site:ggzy.guizhou.gov.cn "铜仁" "软件" "采购公告" "2026"',
]


def fetch_url(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 TenderMonitor/1.0"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def decode_page(raw: bytes) -> str:
    for encoding in ("utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def bing_rss(query: str, count: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"q": query, "format": "rss", "count": str(count)})
    url = f"https://www.bing.com/search?{params}"
    raw = fetch_url(url)
    root = ET.fromstring(raw)
    items = []
    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        desc = item.findtext("description") or ""
        pub_date = item.findtext("pubDate") or ""
        items.append(
            {
                "title": html.unescape(strip_tags(title)).strip(),
                "url": link.strip(),
                "snippet": html.unescape(strip_tags(desc)).strip(),
                "published": pub_date.strip(),
                "query": query,
            }
        )
    return items


def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value or "")


def page_to_text(page: str) -> str:
    page = re.sub(r"<script\b.*?</script>", " ", page, flags=re.IGNORECASE | re.DOTALL)
    page = re.sub(r"<style\b.*?</style>", " ", page, flags=re.IGNORECASE | re.DOTALL)
    text = html.unescape(strip_tags(page))
    return re.sub(r"\s+", " ", text).strip()


def direct_source_items(max_sources: int | None = None) -> list[dict]:
    items: list[dict] = []
    anchor_pattern = re.compile(
        r"<a\b[^>]*href=[\"'](?P<href>[^\"']+)[\"'][^>]*>(?P<title>.*?)</a>",
        re.IGNORECASE | re.DOTALL,
    )
    date_pattern = re.compile(r"20\d{2}[-年/.]\d{1,2}[-月/.]\d{1,2}日?")
    pool = source_pool()
    sources = pool[:max_sources] if max_sources else pool
    for source_name, url in sources:
        try:
            page = decode_page(fetch_url(url, timeout=25))
        except Exception as exc:  # noqa: BLE001
            items.append(
                {
                    "title": f"直接源抓取失败：{source_name}",
                    "url": url,
                    "snippet": str(exc),
                    "published": "",
                    "query": source_name,
                    "score": -999,
                    "reasons": ["直接源失败"],
                }
            )
            continue
        for match in anchor_pattern.finditer(page):
            title = html.unescape(strip_tags(match.group("title"))).strip()
            title = re.sub(r"\s+", " ", title)
            if len(title) < 6:
                continue
            href = urllib.parse.urljoin(url, html.unescape(match.group("href")).strip())
            around = page[max(0, match.start() - 120) : min(len(page), match.end() + 160)]
            around_text = html.unescape(strip_tags(around))
            dates = date_pattern.findall(around_text)
            snippet = f"{source_name}；{around_text.strip()[:260]}"
            item = {
                "title": title,
                "url": href,
                "snippet": snippet,
                "published": " ".join(dates[:2]),
                "query": source_name,
            }
            title_has_software = any(term.lower() in title.lower() for term in SOFTWARE_TERMS)
            title_has_hardware_noise = any(term in title for term in HARDWARE_NOISE_TERMS)
            if is_procurement_like(item) and title_has_software and not title_has_hardware_noise:
                items.append(item)
    return items


def score_item(item: dict) -> tuple[int, list[str]]:
    text = f"{item.get('title', '')} {item.get('snippet', '')} {item.get('url', '')}"
    score = 0
    reasons: list[str] = []

    for term in SOFTWARE_TERMS:
        if term.lower() in text.lower():
            score += 3
            reasons.append(term)
    for term in MODE_TERMS:
        if term in text:
            score += 4
            reasons.append(term)
    for term in BUYER_TERMS:
        if term in text:
            score += 2
            reasons.append(term)
    for term in REGION_TERMS:
        if term in text:
            score += 1
            reasons.append(term)

    domain = urllib.parse.urlparse(item.get("url", "")).netloc.lower()
    if any(d in domain for d in official_domains()):
        score += 4
        reasons.append("官方/准官方来源")
    if any(term in text for term in ["全国", "政府采购", "公共资源", "中小企业", "小微企业"]):
        score += 2
    if "中标" in text or "成交公告" in text or "结果公告" in text:
        score -= 3
        reasons.append("可能是结果公告")
    if "2026" in text:
        score += 1
    if any(term in text for term in ["旅游", "景点", "攻略", "百科", "软件下载", "下载站"]):
        score -= 20
        reasons.append("噪声风险")
    if any(term in text for term in HARDWARE_NOISE_TERMS):
        score -= 10
        reasons.append("偏硬件/工程/后勤")

    return score, sorted(set(reasons), key=reasons.index)


def is_procurement_like(item: dict) -> bool:
    text = f"{item.get('title', '')} {item.get('snippet', '')} {item.get('url', '')}"
    has_trade_mode = any(term in text for term in MODE_TERMS) or (
        ("招标" in text or "采购" in text) and ("公告" in text or "项目" in text)
    )
    has_software = any(term.lower() in text.lower() for term in SOFTWARE_TERMS)
    has_location = any(place in text for place in REGION_TERMS) or any(
        domain in urllib.parse.urlparse(item.get("url", "")).netloc.lower()
        for domain in official_domains()
    )
    has_noise = any(term in text for term in ["旅游", "景点", "攻略", "百科", "软件下载", "下载站"])
    return has_trade_mode and has_software and has_location and not has_noise


def extract_amount(text: str) -> str:
    patterns = [
        r"(?:预算金额|预算价|最高限价|项目预算|采购预算|采购控制价|拦标价|采购限价)[：:\s]*人民币?\s*([0-9,.]+)\s*(万元|元)",
        r"(?:预算金额|预算价|最高限价|项目预算|采购预算|采购控制价|拦标价|采购限价)[^0-9]{0,20}([0-9,.]+)\s*(万元|元)",
        r"([0-9,.]+)\s*万元",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 2:
                return f"{match.group(1)}{match.group(2)}"
            return f"{match.group(1)}万元"
    return ""


def extract_project_type(text: str) -> str:
    for term in ["网上竞价", "竞价", "询价", "询比采购", "询比", "竞争性谈判", "竞争性磋商", "公开招标", "单一来源"]:
        if term in text:
            return term
    return "未识别"


def extract_dates(text: str) -> list[str]:
    patterns = [
        r"20\d{2}[年/-]\s*\d{1,2}[月/-]\s*\d{1,2}(?:日)?(?:\s*\d{1,2}[:：]\d{2})?",
        r"20\d{2}-\d{1,2}-\d{1,2}(?:\s*\d{1,2}[:：]\d{2})?",
    ]
    dates: list[str] = []
    for pattern in patterns:
        dates.extend(re.findall(pattern, text))
    valid_dates = [value for value in dates if parse_date(value)]
    return sorted(set(valid_dates))


def extract_field(text: str, labels: list[str], max_len: int = 90) -> str:
    for label in labels:
        pattern = rf"{label}[：:\s]*([^。；;\n\r]{{1,{max_len}}})"
        match = re.search(pattern, text)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip(" ：:，,。")
    return ""


def parse_date(value: str) -> dt.datetime | None:
    if not value:
        return None
    cleaned = value.replace("年", "-").replace("月", "-").replace("日", "")
    cleaned = cleaned.replace("/", "-").replace("：", ":")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    match = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})(?:\s*(\d{1,2}):(\d{2}))?", cleaned)
    if not match:
        return None
    year, month, day, hour, minute = match.groups()
    try:
        return dt.datetime(
            int(year),
            int(month),
            int(day),
            int(hour or 23),
            int(minute or 59),
            tzinfo=dt.timezone(dt.timedelta(hours=8)),
        )
    except ValueError:
        return None


def extract_deadlines(text: str) -> dict[str, str]:
    fields = {
        "file_time": extract_deadline_near(text, ["获取采购文件时间", "获取磋商文件时间", "获取谈判文件时间", "报名时间", "获取文件时间"]),
        "response_deadline": extract_deadline_near(text, ["响应文件提交截止时间", "提交投标文件截止时间", "投标截止时间", "响应截止时间", "报价截止时间"]),
        "opening_time": extract_deadline_near(text, ["开标时间", "开启时间", "谈判时间", "磋商时间"]),
    }
    return {key: value for key, value in fields.items() if value}


def extract_deadline_near(text: str, labels: list[str]) -> str:
    date_pattern = r"20\d{2}[年/-]\s*\d{1,2}[月/-]\s*\d{1,2}(?:日)?(?:\s*\d{1,2}[:：]\d{2})?"
    for label in labels:
        match = re.search(rf"{label}.{{0,120}}?({date_pattern})", text)
        if match and parse_date(match.group(1)):
            return match.group(1)
    return ""


def determine_status(text: str, dates: list[str], deadlines: dict[str, str]) -> str:
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    if any(term in text for term in ["中标公告", "成交公告", "结果公告", "废标公告", "流标公告"]):
        return "已出结果/已结束"
    response_dt = parse_date(deadlines.get("response_deadline", "")) or parse_date(deadlines.get("opening_time", ""))
    file_dt = parse_date(deadlines.get("file_time", ""))
    if response_dt:
        if response_dt >= now:
            return f"进行中，截止 {response_dt.strftime('%Y-%m-%d %H:%M')}"
        return f"可能已过期，截止 {response_dt.strftime('%Y-%m-%d %H:%M')}"
    if file_dt and file_dt >= now:
        return f"还可获取文件，至 {file_dt.strftime('%Y-%m-%d %H:%M')}"
    parsed_dates = [parsed for parsed in (parse_date(value) for value in dates) if parsed]
    future_dates = [value for value in parsed_dates if value >= now]
    if future_dates:
        return f"进行中，最近日期 {min(future_dates).strftime('%Y-%m-%d %H:%M')}"
    if parsed_dates:
        return f"需核验，最近公告日期 {max(parsed_dates).strftime('%Y-%m-%d')}"
    return "需打开公告核验"


def evaluate_suitability(item: dict, detail_text: str) -> tuple[str, str]:
    title = item.get("title", "")
    text = f"{title} {detail_text}"
    score = item.get("score", 0)
    strengths: list[str] = []
    risks: list[str] = []
    if any(term in text for term in ["定制开发", "软件开发", "平台", "系统", "信息化", "运维", "数字化", "AI", "大数据"]):
        strengths.append("软件/系统交付匹配")
        score += 8
    if any(term in text for term in ["中小企业", "小微企业", "专门面向中小企业", "价格扣除", "政府采购促进中小企业"]):
        strengths.append("中小企业政策友好")
        score += 5
    if any(term in text for term in ["高校", "学院", "大学", "医院", "疾控"]):
        strengths.append("事业单位项目")
        score += 4
    if any(term in text for term in ["网上竞价", "询价", "询比", "竞争性谈判"]):
        strengths.append("价格因素更明显")
        score += 4
    if "竞争性磋商" in text:
        strengths.append("方案+报价综合竞争")
        score += 2
    if any(term in text for term in ["等保测评", "等级保护测评", "保密", "涉密", "CMA", "CNAS", "测评机构"]):
        risks.append("可能要求专项资质/合作方")
        score -= 8
    if any(term in title for term in HARDWARE_NOISE_TERMS):
        risks.append("偏硬件/工程/后勤")
        score -= 12
    if "已出结果" in item.get("status", "") or "可能已过期" in item.get("status", ""):
        risks.append("时效风险")
        score -= 20
    if any(term in title for term in NON_PROJECT_TERMS):
        risks.append("非可投项目/公告噪声")
        score -= 20

    level = "高" if score >= 32 else "中" if score >= 22 else "低"
    note_parts = strengths[:2] + risks[:2]
    return level, "；".join(note_parts) if note_parts else "需人工核验公告要求"


def enrich_item(item: dict) -> dict:
    detail_text = ""
    url = item.get("url") or ""
    item["detail_fetch"] = "未抓取"
    if url:
        try:
            detail_text = page_to_text(decode_page(fetch_url(url, timeout=25)))
            item["detail_fetch"] = "成功"
        except Exception as exc:  # noqa: BLE001
            detail_text = f"{item.get('title', '')} {item.get('snippet', '')}"
            item["detail_fetch"] = f"失败：{exc}"
    combined = f"{item.get('title', '')} {item.get('snippet', '')} {detail_text}"
    item["type"] = extract_project_type(combined)
    item["amount"] = extract_amount(combined) or "未识别"
    item["dates"] = extract_dates(combined)
    item["deadlines"] = extract_deadlines(combined)
    item["buyer"] = extract_party(combined, ["采购人信息", "采购人", "采购单位", "招标人"]) or "未识别"
    item["agency"] = extract_party(combined, ["采购代理机构信息", "采购代理机构", "代理机构", "招标代理"]) or "未识别"
    item["status"] = determine_status(combined, item["dates"], item["deadlines"])
    item["suitability"], item["suitability_note"] = evaluate_suitability(item, combined)
    item["detail_excerpt"] = combined[:800]
    return item


def extract_party(text: str, labels: list[str]) -> str:
    for label in labels:
        patterns = [
            rf"{label}[^。；;]{{0,40}}名称[：:\s]*([^。；;，,\n\r]{{2,80}})",
            rf"{label}[：:\s]*([^。；;，,\n\r]{{2,80}})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if not match:
                continue
            value = re.sub(r"\s+", " ", match.group(1)).strip(" ：:，,。")
            value = re.split(r"\s*(?:地址|联系人|联系电话|联系方式|电话)[：:]", value)[0].strip(" ：:，,。")
            if any(noise in value for noise in ["指定地点", "指定", "信息 名称"]):
                continue
            return value
    return ""


def is_actionable_project(item: dict) -> bool:
    title = item.get("title") or ""
    if any(term in title for term in NON_PROJECT_TERMS):
        return False
    return True


def discover(days: int, limit_per_query: int, max_queries: int | None = None, max_direct_sources: int | None = None) -> list[dict]:
    seen: set[str] = set()
    results: list[dict] = []
    for item in direct_source_items(max_sources=max_direct_sources):
        if not is_actionable_project(item):
            continue
        key = normalize_url(item.get("url", ""))
        if not key or key in seen:
            continue
        seen.add(key)
        score, reasons = score_item(item)
        item["score"] = score + 3
        item["reasons"] = sorted(set((item.get("reasons") or []) + reasons + ["直接源"]), key=((item.get("reasons") or []) + reasons + ["直接源"]).index)
        if item["score"] >= 8:
            results.append(enrich_item(item))

    queries = SEARCH_QUERIES[:max_queries] if max_queries else SEARCH_QUERIES
    for query in queries:
        try:
            items = bing_rss(query, count=limit_per_query)
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "title": f"查询失败：{query}",
                    "url": "",
                    "snippet": str(exc),
                    "published": "",
                    "query": query,
                    "score": -999,
                    "reasons": ["查询失败"],
                }
            )
            continue
        for item in items:
            if not is_actionable_project(item):
                continue
            key = normalize_url(item.get("url", ""))
            if not key or key in seen:
                continue
            seen.add(key)
            score, reasons = score_item(item)
            item["score"] = score
            item["reasons"] = reasons
            if score >= 8 and is_procurement_like(item):
                results.append(enrich_item(item))

    suitability_rank = {"高": 0, "中": 1, "低": 2}
    results.sort(key=lambda x: (suitability_rank.get(x.get("suitability", "低"), 3), -x.get("score", 0)))
    return results


def demo_items() -> list[dict]:
    """Return deterministic, sanitized sample opportunities for screenshots and demos."""
    samples = [
        {
            "title": "某市政务服务中心智能客服与工单管理系统采购项目",
            "url": "https://example.com/tenders/demo-government-service",
            "snippet": "竞争性磋商公告。项目面向中小企业，采购智能客服、工单管理、接口集成与运维服务。",
            "published": "2026-07-16",
            "query": "demo",
            "score": 38,
            "reasons": ["软件", "系统", "竞争性磋商", "中小企业政策友好", "官方/准官方来源"],
            "type": "竞争性磋商",
            "amount": "86万元",
            "dates": ["2026-08-20 17:00"],
            "deadlines": {"response_deadline": "2026-08-20 17:00"},
            "buyer": "某市政务服务中心",
            "agency": "某市政府采购中心",
            "status": "进行中，截止 2026-08-20 17:00",
            "suitability": "高",
            "suitability_note": "软件/系统交付匹配；中小企业政策友好",
            "detail_fetch": "演示数据",
            "detail_excerpt": "脱敏演示数据，用于展示报告结构和成功运行结果。",
        },
        {
            "title": "某高校数据治理与可视化平台建设项目",
            "url": "https://example.com/tenders/demo-university-data",
            "snippet": "采购公告。建设数据治理、数据看板、统一接口和后续运维服务。",
            "published": "2026-07-16",
            "query": "demo",
            "score": 31,
            "reasons": ["数据", "平台", "高校", "采购公告"],
            "type": "采购公告",
            "amount": "48万元",
            "dates": ["2026-08-05 10:00"],
            "deadlines": {"response_deadline": "2026-08-05 10:00"},
            "buyer": "某高校信息化办公室",
            "agency": "某采购代理有限公司",
            "status": "进行中，截止 2026-08-05 10:00",
            "suitability": "中",
            "suitability_note": "软件/系统交付匹配；事业单位项目",
            "detail_fetch": "演示数据",
            "detail_excerpt": "脱敏演示数据，用于展示报告结构和成功运行结果。",
        },
    ]
    return samples


def public_example_items() -> list[dict]:
    """Return curated real public tender links for reproducible public screenshots."""
    return [
        {
            "title": "2026年江门市城市管理和综合执法局指挥中心及政务信息化系统运维采购公告",
            "url": "https://www.jiangmen.gov.cn/bmpd/jmscsglhzhzfj/zwgk/tzgg/content/post_3493509.html",
            "snippet": "公开采购公告。采购内容包括智慧化城市管理信息系统、供水用水一体化服务管理平台、城市节水管理信息系统、智慧排水管理信息系统等系统运维服务。",
            "published": "2026-05-19",
            "query": "public-example",
            "score": 36,
            "reasons": ["政务信息化", "系统运维", "采购公告", "公开网页"],
            "type": "采购公告",
            "amount": "未识别",
            "dates": ["2026-05-19"],
            "deadlines": {},
            "buyer": "江门市城市管理和综合执法局",
            "agency": "未识别",
            "status": "需打开公告核验",
            "suitability": "高",
            "suitability_note": "软件/系统交付匹配；政务信息化运维",
            "detail_fetch": "公开网页样例",
            "detail_excerpt": "来源为公开政府网站公告，用于展示项目报告效果。",
        },
        {
            "title": "2026年“深圳市政府外办出国管理系统运维服务”项目采购公告",
            "url": "https://fao.sz.gov.cn/xxgk/tzgg/content/post_1635173.html",
            "snippet": "公开采购公告。为保障深圳智慧外事管理服务系统安全、稳定、高效运行，采购专业运维服务。",
            "published": "2025-12-01",
            "query": "public-example",
            "score": 34,
            "reasons": ["系统", "运维", "政府采购", "公开网页"],
            "type": "采购公告",
            "amount": "未识别",
            "dates": ["2025-12-01"],
            "deadlines": {},
            "buyer": "深圳市人民政府外事办公室",
            "agency": "未识别",
            "status": "需打开公告核验",
            "suitability": "中",
            "suitability_note": "软件/系统交付匹配；需核验资质门槛",
            "detail_fetch": "公开网页样例",
            "detail_excerpt": "来源为公开政府网站公告，用于展示项目报告效果。",
        },
        {
            "title": "山西税务2026年管理决策支持风险与信用等系统运维项目第2次采购招标公告",
            "url": "https://shanxi.chinatax.gov.cn/son/detail/cz-11404-2828-1822059",
            "snippet": "公开招标公告。采购内容包括基础软件运维、应用软件运维和相关系统运行保障。",
            "published": "2026-06-23",
            "query": "public-example",
            "score": 32,
            "reasons": ["系统运维", "公开招标", "税务系统", "公开网页"],
            "type": "公开招标",
            "amount": "445.43万元",
            "dates": ["2026-07-14 15:00"],
            "deadlines": {"response_deadline": "2026-07-14 15:00"},
            "buyer": "国家税务总局山西省税务局",
            "agency": "未识别",
            "status": "可能已过期，截止 2026-07-14 15:00",
            "suitability": "中",
            "suitability_note": "软件/系统交付匹配；时效风险",
            "detail_fetch": "公开网页样例",
            "detail_excerpt": "来源为公开政府网站公告，用于展示项目报告效果。",
        },
    ]


def normalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urllib.parse.urlparse(url)
    clean = parsed._replace(fragment="", query="").geturl()
    return clean.rstrip("/")


def make_report(items: list[dict], output_dir: Path) -> tuple[Path, Path, Path, str, str]:
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    date_label = now.strftime("%Y-%m-%d")
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"全国中小企业软件招采机会日报-{date_label}.md"
    html_path = output_dir / f"全国中小企业软件招采机会日报-{date_label}.html"
    json_path = output_dir / f"全国中小企业软件招采机会日报-{date_label}.json"

    active = [i for i in items if i.get("suitability") in ("高", "中")]
    leads = [i for i in items if i.get("suitability") == "低"]

    lines = [
        f"# 全国中小企业软件招采机会日报 - {date_label}",
        "",
        f"生成时间：{now.strftime('%Y-%m-%d %H:%M:%S')} 北京时间",
        "",
        "说明：本报告面向全国中小企业，重点筛选软件开发、系统平台、信息化、数字化、运维、网络安全、AI、小程序、接口集成等可承接项目。第三方聚合站线索必须回到采购人官网、公共资源平台或交易平台核验原公告。",
        "",
        f"高/中适合度项目：{len(active)} 条；低适合度或需核验项目：{len(leads)} 条。",
        "",
        "## 目前最值得看的项目",
        "",
        "| 项目 | 类型 | 金额 | 状态 | 适合度 | 采购人/代理 |",
        "|---|---:|---:|---|---|---|",
    ]
    lines.extend(format_table_rows(active))
    lines.extend(["", "## 低适合度或需核验线索", ""])
    lines.extend(format_items(leads))
    lines.extend(["", "## 详情", ""])
    lines.extend(format_items(active))
    lines.extend(["", "## 今日检索关键词", ""])
    for query in SEARCH_QUERIES:
        lines.append(f"- {query}")
    lines.append("")

    report_text = "\n".join(lines)
    html_body = build_email_html(items, now)
    md_path.write_text(report_text, encoding="utf-8")
    html_path.write_text(html_body, encoding="utf-8")
    json_path.write_text(
        json.dumps({"generated_at": now.isoformat(), "items": items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return md_path, json_path, html_path, report_text, html_body


def format_table_rows(items: list[dict]) -> list[str]:
    if not items:
        return ["| 暂未发现匹配度足够高的新线索 | - | - | - | - | - |"]
    rows = []
    for item in items:
        title = item.get("title") or "(无标题)"
        url = item.get("url") or ""
        buyer = item.get("buyer") or "未识别"
        agency = item.get("agency") or "未识别"
        rows.append(
            "| "
            + " | ".join(
                [
                    f"[{title}]({url})",
                    item.get("type") or "未识别",
                    item.get("amount") or "未识别",
                    item.get("status") or "需核验",
                    f"{item.get('suitability', '低')}，{item.get('suitability_note', '')}",
                    f"{buyer} / {agency}",
                ]
            )
            + " |"
        )
    return rows


def format_items(items: list[dict]) -> list[str]:
    if not items:
        return ["暂未发现匹配度足够高的新线索。"]
    lines: list[str] = []
    for idx, item in enumerate(items, 1):
        title = item.get("title") or "(无标题)"
        url = item.get("url") or ""
        snippet = item.get("snippet") or ""
        amount = item.get("amount") or "未识别"
        dates = "；".join(item.get("dates") or []) or "未识别"
        reasons = "、".join(item.get("reasons") or []) or "关键词匹配"
        score = item.get("score", 0)
        source = urllib.parse.urlparse(url).netloc or "未知来源"
        deadlines = item.get("deadlines") or {}
        lines.extend(
            [
                f"### {idx}. {title}",
                "",
                f"- 匹配分：{score}",
                f"- 来源：{source}",
                f"- 类型：{item.get('type') or '未识别'}",
                f"- 金额：{amount}",
                f"- 状态：{item.get('status') or '需核验'}",
                f"- 适合度：{item.get('suitability', '低')}，{item.get('suitability_note', '')}",
                f"- 采购人：{item.get('buyer') or '未识别'}",
                f"- 代理机构：{item.get('agency') or '未识别'}",
                f"- 文件/截止/开标：{deadlines or '未识别'}",
                f"- 日期线索：{dates}",
                f"- 命中原因：{reasons}",
                f"- 链接：{url}",
                f"- 摘要：{snippet[:260]}",
                "",
            ]
        )
    return lines


def build_email_html(items: list[dict], now: dt.datetime) -> str:
    rows = []
    for idx, item in enumerate(items[:30], 1):
        level = item.get("suitability", "低")
        badge_color = {"高": "#166534", "中": "#92400e", "低": "#64748b"}.get(level, "#64748b")
        rows.append(
            "<tr>"
            f"<td>{idx}</td>"
            f"<td><a href=\"{esc_attr(item.get('url', ''))}\">{esc(item.get('title') or '(无标题)')}</a>"
            f"<div class=\"meta\">{esc(urllib.parse.urlparse(item.get('url', '')).netloc or '未知来源')}</div></td>"
            f"<td>{esc(item.get('type') or '未识别')}</td>"
            f"<td>{esc(item.get('amount') or '未识别')}</td>"
            f"<td>{esc(item.get('status') or '需核验')}</td>"
            f"<td><span style=\"color:{badge_color};font-weight:700\">{esc(level)}</span><div class=\"meta\">{esc(item.get('suitability_note') or '')}</div></td>"
            f"<td>{esc(item.get('buyer') or '未识别')}<div class=\"meta\">代理：{esc(item.get('agency') or '未识别')}</div></td>"
            "</tr>"
        )
    if not rows:
        rows.append("<tr><td colspan=\"7\">暂未发现匹配度足够高的新线索。</td></tr>")
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, "Microsoft YaHei", sans-serif; color: #111827; line-height: 1.55; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; }}
    h1 {{ font-size: 22px; margin: 0 0 8px; }}
    .summary {{ margin: 10px 0 18px; color: #374151; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 9px 10px; vertical-align: top; text-align: left; }}
    th {{ background: #f3f4f6; font-weight: 700; white-space: nowrap; }}
    tr:nth-child(even) td {{ background: #fafafa; }}
    a {{ color: #075985; text-decoration: none; font-weight: 700; }}
    .meta {{ color: #6b7280; font-size: 12px; margin-top: 4px; }}
    .note {{ background: #fff7ed; border: 1px solid #fed7aa; padding: 10px 12px; margin: 16px 0; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>全国中小企业软件招采机会日报 - {esc(now.strftime('%Y-%m-%d'))}</h1>
    <div class="summary">生成时间：{esc(now.strftime('%Y-%m-%d %H:%M:%S'))} 北京时间。面向全国中小企业，优先识别软件开发、信息化、数字化、运维、网络安全等可承接机会；已打开公告详情页，提取类型、金额、状态、适合度、采购人和代理机构。</div>
    <div class="note">提醒：竞争性磋商通常不是最低价中标，而是综合评分；更接近低价优先的是网上竞价、询价、竞争性谈判。所有线索投标前仍需回原公告核验。</div>
    <table>
      <thead>
        <tr><th>#</th><th>项目</th><th>类型</th><th>金额</th><th>状态</th><th>适合度</th><th>采购人/代理</th></tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </div>
</body>
</html>"""


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=False)


def esc_attr(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def send_email(recipient: str, subject: str, body: str, attachments: list[Path], html_body: str | None = None) -> None:
    host = getenv_tender("TENDER_SMTP_HOST")
    port = int(getenv_tender("TENDER_SMTP_PORT", "587"))
    user = getenv_tender("TENDER_SMTP_USER")
    password = getenv_tender("TENDER_SMTP_PASSWORD")
    sender = getenv_tender("TENDER_SMTP_FROM") or user
    use_tls = getenv_tender("TENDER_SMTP_TLS", "true").lower() != "false"

    missing = [
        name
        for name, value in {
            "TENDER_SMTP_HOST": host,
            "TENDER_SMTP_USER": user,
            "TENDER_SMTP_PASSWORD": password,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError("Missing SMTP environment variables: " + ", ".join(missing))

    msg = email.message.EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    msg.add_alternative(html_body or markdown_to_simple_html(body), subtype="html")

    for path in attachments:
        msg.add_attachment(
            path.read_bytes(),
            maintype="application",
            subtype="octet-stream",
            filename=path.name,
        )

    if port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as server:
            server.login(user, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=30) as server:
            if use_tls:
                server.starttls(context=ssl.create_default_context())
            server.login(user, password)
            server.send_message(msg)


def getenv_tender(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    if winreg is None:
        return default
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return str(value) if value else default
    except OSError:
        return default


def markdown_to_simple_html(markdown: str) -> str:
    escaped = html.escape(markdown)
    escaped = re.sub(r"^# (.+)$", r"<h1>\1</h1>", escaped, flags=re.MULTILINE)
    escaped = re.sub(r"^## (.+)$", r"<h2>\1</h2>", escaped, flags=re.MULTILINE)
    escaped = re.sub(r"^### (.+)$", r"<h3>\1</h3>", escaped, flags=re.MULTILINE)
    escaped = escaped.replace("\n", "<br>\n")
    return f"<html><body>{escaped}</body></html>"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Monitor nationwide SME-friendly software and digitalization tender opportunities.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            SMTP env vars:
              TENDER_SMTP_HOST TENDER_SMTP_PORT TENDER_SMTP_USER TENDER_SMTP_PASSWORD
              Optional: TENDER_SMTP_FROM TENDER_SMTP_TLS
            """
        ),
    )
    parser.add_argument("--recipient", default=DEFAULT_RECIPIENT)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--days", type=int, default=14, help="Reserved freshness window for report context.")
    parser.add_argument("--limit-per-query", type=int, default=10)
    parser.add_argument("--max-queries", type=int, help="Limit search queries for quick real-data runs.")
    parser.add_argument("--max-direct-sources", type=int, help="Limit direct sources for quick real-data runs.")
    parser.add_argument("--demo", action="store_true", help="Use sanitized sample data and skip network fetching.")
    parser.add_argument("--public-examples", action="store_true", help="Use curated real public tender links for screenshots.")
    parser.add_argument("--send-email", action="store_true")
    parser.add_argument("--no-email", action="store_true")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    if args.demo:
        items = demo_items()
    elif args.public_examples:
        items = public_example_items()
    else:
        items = discover(
            days=args.days,
            limit_per_query=args.limit_per_query,
            max_queries=args.max_queries,
            max_direct_sources=args.max_direct_sources,
        )
    md_path, json_path, html_path, report, html_body = make_report(items, output_dir)
    print(f"Report written: {md_path}")
    print(f"Data written: {json_path}")
    print(f"HTML written: {html_path}")

    if args.send_email and not args.no_email:
        subject = f"全国中小企业软件招采机会日报 {dt.datetime.now().strftime('%Y-%m-%d')}"
        try:
            send_email(args.recipient, subject, report[:12000], [md_path, json_path, html_path], html_body=html_body)
            print(f"Email sent to: {args.recipient}")
        except Exception as exc:  # noqa: BLE001
            error_path = output_dir / "last-email-error.txt"
            error_path.write_text(str(exc), encoding="utf-8")
            print(f"Email failed: {exc}", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
