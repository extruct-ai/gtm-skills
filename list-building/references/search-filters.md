# Search Filters Reference

Filters for `GET /v1/companies/search`. Pass as JSON string in `filters` param.

## Structure

```json
{
  "include": { ... },
  "exclude": { ... },
  "range": { ... }
}
```

All sections optional.

## Include / Exclude

| Field | Type | Example |
|-------|------|---------|
| `country` | string[] | `["United States", "Germany"]` |
| `city` | string[] | `["San Francisco", "Berlin"]` |
| `size` | string[] | `["11-50", "51-200"]` |

## Size Buckets

`1-10`, `11-50`, `51-200`, `201-500`, `501-1000`, `1001-5000`, `5001-10000`, `10001+`

## Range

| Field | Type | Example |
|-------|------|---------|
| `founded` | `{min, max}` | `{"min": 2018, "max": 2024}` |

## Common Country Lists

**EU + UK:**
```python
EU_COUNTRIES = [
    "United Kingdom", "Germany", "France", "Netherlands", "Sweden",
    "Spain", "Italy", "Ireland", "Belgium", "Austria", "Denmark",
    "Finland", "Poland", "Portugal", "Czech Republic", "Romania",
    "Hungary", "Estonia", "Lithuania", "Latvia", "Luxembourg",
    "Norway", "Switzerland",
]
```

## Example

```python
filters = json.dumps({
    "include": {
        "size": ["11-50", "51-200", "201-500"],
        "country": ["United States"] + EU_COUNTRIES,
    },
    "exclude": {
        "city": ["San Francisco"]
    },
    "range": {
        "founded": {"min": 2015}
    }
})
```
