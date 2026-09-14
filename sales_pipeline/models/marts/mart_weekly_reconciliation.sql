-- Reconciliation mart: independently recalculates weekly totals from raw
-- transactions and compares them against the company's reported Weekly
-- Summary. This is a data-quality safety net, not just a report.

with tx_weekly as (

    select
        week_start_date,
        count(order_id)        as calculated_total_orders,
        avg(order_revenue)     as calculated_avg_bill_value

    from {{ ref('stg_transactions') }}
    group by 1

),

reported as (

    select * from {{ ref('stg_weekly_summary') }}

)

select
    coalesce(t.week_start_date, r.week_start_date) as week_start_date,
    r.week_number,
    t.calculated_total_orders,
    r.reported_total_orders,
    t.calculated_total_orders - r.reported_total_orders            as orders_diff,
    round(t.calculated_avg_bill_value, 2)                          as calculated_avg_bill_value,
    r.reported_avg_bill_value,
    round(t.calculated_avg_bill_value - r.reported_avg_bill_value, 2) as avg_bill_value_diff,
    case
        when t.calculated_total_orders = r.reported_total_orders
             and abs(t.calculated_avg_bill_value - r.reported_avg_bill_value) < 1
        then 'MATCH'
        else 'MISMATCH'
    end as reconciliation_status

from tx_weekly t
full outer join reported r using (week_start_date)
order by week_start_date
