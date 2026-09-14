-- Staging layer: light cleanup only, no business logic yet.
-- One row per order.

with source as (

    select * from {{ source('raw', 'raw_transactions') }}

),

renamed as (

    select
        order_id,
        customer_id,
        order_datetime,
        date_parsed                        as order_date,
        device_type,
        channel,
        order_quantity,
        sale                                as order_revenue,
        nps_survey,
        -- convenient week bucket for joining against the weekly summary later
        date_trunc('week', date_parsed)    as week_start_date

    from source

)

select * from renamed
