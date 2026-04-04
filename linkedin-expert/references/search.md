# LinkedIn Search & Boolean Operators

## Table of Contents
1. [Boolean Syntax](#boolean-syntax)
2. [People Search Filters](#people-search-filters)
3. [Job Search Filters](#job-search-filters)
4. [Content Search](#content-search)
5. [Company Search](#company-search)
6. [Sales Navigator Search (50+ Filters)](#sales-navigator-search)

---

## Boolean Syntax

LinkedIn supports Boolean operators in all search bars. **Operators must be uppercase.**

| Operator | Usage | Example |
|---|---|---|
| `AND` | Both terms required (default between words) | `Python AND machine learning` |
| `OR` | Either term | `"Account Executive" OR "Account Manager"` |
| `NOT` | Exclude term | `Python NOT manager` |
| `"quotes"` | Exact phrase match | `"machine learning engineer"` |
| `(parentheses)` | Group expressions | `(Java OR Python) AND (engineer OR developer) NOT manager` |

**Important:** The `+` and `-` shorthand operators are NOT officially supported. Use AND/NOT instead.

**Sales Navigator limit:** ~15 Boolean operators per query.

---

## People Search Filters

Available to free users:

- **Connections:** 1st, 2nd, 3rd+ degree
- **Location:** City, region, country
- **Current company**
- **Past company**
- **School / University**
- **Industry**
- **Profile language**
- **Service categories** (for freelancers/consultants)

**Recruiter search adds:** Open to Work status, self-reported contract availability, skill assessment scores, pipeline status.

**Example people search:** Find marketing directors at mid-size SaaS companies in Austin who are 2nd-degree connections:
- Keywords: `"marketing director" OR "VP marketing"`
- Industry: Software/Technology
- Location: Austin, Texas
- Connections: 2nd degree

---

## Job Search Filters

See [jobs.md](jobs.md) for complete job search filter details.

Quick Boolean example in Jobs:
- `"product manager" OR "product owner" NOT "senior" NOT "director"`
- Combine with Location: Remote, Date: Past 24 hours, Easy Apply off for lower competition

---

## Content Search

Search for posts, articles, and newsletters:

- **Keyword search** — scans post text, article titles, and author names
- **Date filter** — past 24 hours, week, month
- **From your connections** toggle — see what people you follow have posted
- **Content type** — posts, articles (separate tabs in results)

**Use case:** Monitor what your target audience is talking about. Search a topic, filter to "Past week," and read top comments to find warm outreach opportunities.

---

## Company Search

- **Industry**
- **Company size** (employee count)
- **Location**
- **Has job openings** toggle

**On a Company Page:** See follower count, employee count trend, recent hires (by title), recent posts, and who in your network works there. Use "People" tab to find specific decision-makers.

---

## Sales Navigator Search (50+ Filters)

Sales Navigator unlocks far more granular filtering than standard LinkedIn search:

**Lead (People) Filters:**
- Seniority level (individual contributor → C-suite)
- Job function (Marketing, Finance, Engineering, etc.)
- Years in current role / years at current company
- Company headcount and headcount growth %
- Geographic region (DMA-level precision)
- Technology used (CRM, marketing stack, etc.)
- LinkedIn activity: recently posted, changed jobs, mentioned in news
- Buyer Intent signals (accounts actively researching solutions like yours)

**Account (Company) Filters:**
- Company revenue range
- Funding stage and recent funding events
- Industry and sub-industry
- Headcount and headcount growth trend
- Technology used
- Posted in last 30 days

**Spotlights filter (high-value outreach triggers):**
- Changed jobs in last 90 days
- Posted on LinkedIn in last 30 days
- Mentioned in the news recently

These warm signal filters are the core advantage of Sales Navigator over standard search.

For full Sales Navigator feature details, see [sales-navigator.md](sales-navigator.md).
