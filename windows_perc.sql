Create or replace table order_category_percentiles AS
with completed_orders AS (
    select
        o.order_id,
        o.customer_id,
        c.name as customer_name,
        c.city,
        c.segment,
        o.branch,
         o.category,
        CAST(o.order_date AS DATE) aS order_date,
        CAST(o.amount AS DOUBLE) as amount
    from read_csv_auto('orders.csv') O
    inner join read_csv_auto('customers.csv') c
        on o.customer_id = c.customer_id
    where o.status = 'completed'
)
SELECT
    order_id,
    customer_id,
    customer_name,
    city,
    segment,
    branch,
    category,
    order_date,
    amount,
    NTILE(4) OVER (
        PARTITION BY category
        ORDER BY amount ASC
    ) AS spend_quartile,
    ROUND(
        PERCENT_RANK() OVER (
            PARTITION BY category
            ORDER BY amount ASC
        ),4
    ) AS category_percent_rank,
    ROUND(
        CUME_DIST() OVER (
            PARTITION BY category
            ORDER BY amount ASC
        ), 4
    )  AS category_cume_dist
    FROM completed_orders;