-- Marketing channel performance mart.

select
    channel,
    count(order_id)                                                       as total_orders,
    sum(order_revenue)                                                    as total_revenue,
    round(avg(order_revenue), 2)                                          as avg_order_value,
    round(sum(order_revenue) / sum(sum(order_revenue)) over (), 4)        as revenue_share

from {{ ref('stg_transactions') }}
where channel is not null
group by channel
order by total_revenue desc
