# Vellamo Quartile Engine (`vellamo-quartile-engine`)

**High-Speed OLAP Statistical Segmentation & Window Analytics Pipeline in DuckDB and Python**

---

## 1. Executive Summary & Problem Statement

In multi-branch retail and wholesale operations, evaluating customer transactions using static, arbitrary spending cutoffs (e.g., *"Every order above KES 3,000 is VIP"*) introduces severe analytical distortion. Different product lines exhibit distinct price floors, ceilings, and purchasing velocities—meaning an outlier order in **Accessories** does not share the same statistical distribution as an outlier in **Men's Wear** or **Shoes**.

Furthermore, traditional SQL `GROUP BY` aggregations collapse row-level transaction history into summary averages, destroying individual receipt visibility. Conversely, attempting to calculate relative percentile standings via self-joins or correlated subqueries across hundreds of thousands of rows triggers $O(N^2)$ performance bottlenecks.

**Vellamo Quartile Engine** solves this by leveraging **DuckDB's vectorized columnar OLAP engine** and **advanced SQL distribution window functions** (`NTILE`, `PERCENT_RANK`, and `CUME_DIST`). In a single sequential pass over **500,000 raw retail records**, the pipeline dynamically normalizes, buckets, and scores **424,823 completed orders** against their respective product category probability distributions without losing individual transaction granularity.

---

## 2. Dataset Architecture & Scope

The pipeline ingests and joins two primary relational datasets via zero-copy CSV streaming:

### `orders.csv` (500,000 Fact Records)
* **Completed Orders Processed:** `424,823` (excluding `37,670` pending and `37,507` cancelled transactions)
* **Retail Branches (8):** Vellamo CBD, Vellamo Westlands, Vellamo Karen, Vellamo Nyali, Vellamo City Mall, Vellamo Rupa's Mall, Vellamo Westside Mall, Vellamo Mega Plaza
* **Product Categories (7):** Accessories, Bags, Jewelry, Kids Wear, Men's Wear, Shoes, Women's Wear
* **Transaction Value Range:** KES 200.02 to KES 5,000.00

### `customers.csv` (20,000 Dimension Records)
* **Customer Segments (3):** Retail (`6,768`), Wholesale (`6,687`), Online (`6,545`)
* **Urban Hubs (5):** Mombasa (`4,131`), Nairobi (`4,049`), Nakuru (`3,972`), Kisumu (`3,931`), Eldoret (`3,917`)

---

## 3. Mathematical & SQL Window Function Specification

All statistical window operations are partitioned by `category` and ordered by `amount ASC` (`OVER (PARTITION BY category ORDER BY amount ASC)`):

1. **Equal-Bucket Quartile Stratification (`NTILE(4)`):**
   Slices each ordered category partition into 4 equal 25% statistical buckets:
   * **Quartile 1:** Bottom 25% (Low-ticket baseline)
   * **Quartile 2:** 25% – 50% (Lower-mid tier, below category median)
   * **Quartile 3:** 50% – 75% (Upper-mid tier, above category median)
   * **Quartile 4:** Top 25% (High-ticket / VIP Whale tier)

2. **Relative Standing (`PERCENT_RANK()`):**
   Computes the exact relative percentile rank of an order within its product category on a scale from `0.0000` to `1.0000`:
   $$\text{PERCENT\_RANK} = \frac{\text{rank} - 1}{\text{total\_category\_rows} - 1}$$
   Indicates the exact percentage of orders in the same category that fall strictly below the current order's KES value.

3. **Cumulative Probability Distribution (`CUME_DIST()`):**
   Computes the cumulative distribution probability (`> 0.0000` to `1.0000`):
   $$\text{CUME\_DIST} = \frac{\text{count of category rows with amount } \le \text{ current row}}{\text{total\_category\_rows}}$$
   Captures the exact proportion of category volume sitting at or below a given transaction value.

---

## 4. Pipeline Architecture & Repository Structure

```text
day45_window_analytics/
├── window_percentiles.sql       # Core DDL/DML analytical window query
├── run_analytics.py             # Python + DuckDB execution & MotherDuck sync runner
├── quartile_audit_summary.csv   # Verified 28-row statistical boundary audit output
├── .gitignore                   # Excludes heavy raw CSVs and binary .duckdb files
└── README.md                    # Project documentation and benchmark results"# retail_spend_stratifier" 
