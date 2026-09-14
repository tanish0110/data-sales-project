-- Staging layer: light cleanup only, no business logic yet.
-- One row per reported week.

with source as (

    select * from {{ source('raw', 'raw_weekly_summary') }}

),

renamed as (

    select
        week_start_date,
        -- pulls the numeric week number out of strings like 'Week 1 (01-Jun)'
        try_cast(regexp_extract(week, 'Week (\d+)', 1) as integer) as week_number,
        gross_margin_                          as gross_margin_pct,
        conversion_rate,
        avg_bill_value                         as reported_avg_bill_value,
        total_orders_week                      as reported_total_orders,
        marketing_spends                       as marketing_spend

    from source

)

select * from renamed
