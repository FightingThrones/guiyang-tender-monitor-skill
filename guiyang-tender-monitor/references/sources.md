# Data Sources

This skill discovers tender and procurement opportunities through a mix of official platforms, public search, and regional buyer sites.

## National Sources

- 中国政府采购网: `ccgp.gov.cn`
- 全国公共资源交易平台: `ggzy.gov.cn`
- 中国招标投标公共服务平台: `cebpubservice.com`
- 军队采购网: `plap.mil.cn`
- 国铁采购平台: `cg.95306.cn`
- Public procurement channels of universities, hospitals, disease control centers, SOEs, and public institutions

## Built-in Target Source Pool

The structured source pool lives in:

```text
data/target_sources.csv
```

The first batch includes national and provincial public-resource/government-procurement entry points from the user-provided source list, including Beijing, Hebei, Shanxi, Inner Mongolia, Liaoning, Jilin, Heilongjiang, Shanghai, Jiangsu, Zhejiang, Fujian, Jiangxi, Henan, Hubei, Hunan, Guangdong, Guangxi, Hainan, Sichuan, Guizhou, Yunnan, Tibet, Shaanxi, Gansu, Qinghai, Ningxia, and Xinjiang.

## Included Regional Examples

Guizhou/Guiyang/Tongren/Sinan remain included as regional examples because the original workflow was built for these markets:

- 贵州省公共资源交易平台
- 贵阳市公共资源交易平台
- 铜仁市公共资源交易中心
- 思南县政府采购公告
- 贵州高校、医院、疾控、国企采购公告

## Discovery Rules

Aggregator and search-result links are treated as leads only. Before bidding, always verify:

- Original official announcement
- Procurement method
- Registration and response deadlines
- Budget or maximum price
- Buyer and agency information
- Qualification requirements
- SME or small/micro-enterprise policy clauses

## Risk Notes

The report may include false positives. Human review is required before any commercial follow-up or bidding decision.
