-- Weekly revenue vs marketing spend efficiency trend.

with tx_weekly as (

    select
        week_start_date,
        sum(order_revenue) as actual_revenue

    from {{ ref('stg_transactions') }}
    group by 1

)

select
    r.week_start_date,
    r.week_number,
    t.actual_revenue,
    r.marketing_spend,
    round(t.actual_revenue / nullif(r.marketing_spend, 0), 2)  as revenue_per_spend,
    r.conversion_rate,
    r.gross_margin_pct

from {{ ref('stg_weekly_summary') }} r
left join tx_weekly t using (week_start_date)
order by r.week_start_date
