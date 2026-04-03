#pip install streamlit pandas ftfy

import streamlit as st
import pandas as pd
import sqlite3

# 1. Page Setup
st.set_page_config(page_title="UberEats Strategic Insights",layout="wide")

# 2. Database Connection & Data Loading
# Load the master data

conn = sqlite3.connect('uber_eats_analysis.db')
df_res = pd.read_sql_query("SELECT * FROM restaurants", conn)
#df_ord = pd.read_sql_query("SELECT * FROM orders", conn)

# 3. Sidebar - Dynamic Filters
st.sidebar.header("Business Filters")

city_list = sorted(df_res['city'].dropna().unique())
selected_cities = st.sidebar.multiselect("Select City", options=city_list)


# Filter: location
location_list = sorted(df_res['location'].dropna().unique())
selected_location = st.sidebar.multiselect("Select location", options=location_list)

# Filter: rest_type
type_list = sorted(df_res['rest_type'].dropna().unique())
selected_types = st.sidebar.multiselect("Select Rest_type", options=type_list)

# Filter: Category
cat_list = sorted(df_res['category'].dropna().unique())
selected_cats = st.sidebar.multiselect("Select Category", options=cat_list)


# Filter: Online Order , Booking 
col1, col2 , col3, col4 = st.sidebar.columns(4)
online_choice = col1.radio("Online Order", ["All", "Yes", "No"])
book_choice = col2.radio("Book Table", ["All", "Yes", "No"])


# 4. Applying Dynamic Logic
df_filtered = df_res.copy()#The original Master List stays safe in your filing cabinet.

if selected_cities:
    df_filtered = df_filtered[df_filtered['city'].isin(selected_cities)]

if selected_location:
    df_filtered = df_filtered[df_filtered['location'].isin(selected_location)]

if selected_types:
    df_filtered = df_filtered[df_filtered['rest_type'].isin(selected_types)]
    
if selected_cats:
    df_filtered = df_filtered[df_filtered['category'].isin(selected_cats)]

if online_choice != "All":
    df_filtered = df_filtered[df_filtered['online_order'] == online_choice]

if book_choice != "All":
    df_filtered = df_filtered[df_filtered['book_table'] == book_choice]


# 5. Main Dashboard Display
st.title(" UberEats Market Analysis Dashboard")
st.markdown("---")

# High-Level Metrics
m1, m2, m3, m4 = st.columns(4)

m1.metric("Active Restaurants", len(df_filtered['name']))
m2.metric("Avg Rating", f"{df_filtered['rate'].mean():.2f}")
m3.metric("Avg Votes", f"{df_filtered['votes'].mean():.2f}")
m4.metric("Avg Cost (2 ppl)", f"₹{df_filtered['cost'].mean():.0f}")

st.divider()

# ---  Restaurant List ---
st.subheader("Filtered Restaurant List")
# Displaying names ,cuisines,disk_liked found in the current filter
display_cols = ['name', 'cuisines','dish_liked']
# Check if columns exist before showing table
existing_cols = [c for c in display_cols if c in df_filtered.columns]
st.dataframe(df_filtered[existing_cols].reset_index(drop=True) , use_container_width=True)
st.divider()

# 6. Deep Dive SQL Analysis
st.title("Restaurants data Analysis Questions ")

queries = {
    "1. Highest average rating location":"""SELECT location, ROUND(AVG(rate), 2) AS avg_rating,
                                            sum(votes) as total_votes FROM restaurants where rate > 0 and votes>0
                                            GROUP BY location  ORDER BY avg_rating DESC limit(10)""",
    "2. Over-saturated restaurants":"select location,count(*)as rest_count from restaurants group by location order by rest_count desc limit(10); ",
    "3. Online ordering performance(rating)":"select online_order, round(avg(rate),2)as avg_rate from restaurants where rate > 0 group by online_order;",
    "4. Higher customer ratings(table booking)":"select book_table, round(avg(rate),2)as rating from restaurants where rate > 0 group by book_table; ",
    "5. Customer satisfaction price range":"""select case
                             when cost <= 400 then 'low-price(<400)'
                             when cost >400 and cost <= 1500 then 'mid-price(400-1500)'
                             else 'premium-price (>1500)'
                             end as price_segment,  
                        SUM(votes) AS total_votes,COUNT(*) AS restaurant_count
                        FROM restaurants
                        WHERE rate > 0 AND votes > 0 GROUP BY price_segment ORDER BY total_votes DESC;""",
    "6. Price_segment performance(low,mid,permium)":"""select case
                             when cost <= 400 then 'low-price(<400)'
                             when cost >400 and cost <= 1500 then 'mid-price(400-1500)'
                             else 'premium-price (>1500)'
                             end as price_segment,
                    ROUND(avg(rate),2)as avg_rating
                    FROM restaurants
                    WHERE rate > 0
                    GROUP BY price_segment ORDER BY avg_rating DESC;""",
    "7. Most common cuisines":"select cuisines,count(*)as rest_count from restaurants group by cuisines order by rest_count desc limit(10);",
    "8. Quality Cuisines (Cuisines by rating)":"""select cuisines,round(avg(rate),2)as avg_rating,count(*)as rest_count
                                    from restaurants where rate >0 group by cuisines  order by avg_rating  desc limit(10);""",
    "9. Find demand cuisines(High rating but Low volume)":"""select cuisines,round(avg(rate),2)as avg_rating,count(*)as rest_count from restaurants
                                    where rate >0
                                    group by cuisines having rest_count < 5 order by avg_rating desc limit(10);""",
    "10. Restaurant cost vs rating":"""select cost,
                  round(avg(rate),2)as avg_rating
                  from restaurants
                  where rate >0
                  group by cost
                  order by cost desc, avg_rating desc limit(10); """,
    "11. Premium Restaurant Locations":""" select location,round(avg(rate),2)as avg_rate,count(*)as rest_count,votes
                  from restaurants
                  where cost > 1500 and rate >= 3 and votes > 500
                  group by cost having rest_count < 5
                 order by avg_rate desc,votes desc limit(20); """,              
    "12. Indicates areas(High demand but low quality)":"""  select location,round(avg(rate),2)as avg_rating,sum(votes) as total_votes,
                  count(*)as rest_count
                  from restaurants where rate < 3
                  group by location order by total_votes desc limit(10)"""
                  
}

selected_q = st.selectbox("Choose a Business Case:", list(queries.keys()))

# Run Selected Query
#conn = sqlite3.connect('uber_eats_analysis.db')
df_result = pd.read_sql_query(queries[selected_q], conn)
st.write(df_result)

#-------------orders --------------
st.title("Order Data  Analysis Questions")

queries1 = {
    "1.payment gateway (Card vs. Cash) to optimize":""" select payment_method, count(*) as order_count, sum(order_value) as total_revenue
                    from orders
                    group by payment_method
                    order by total_revenue DESC; """,
    "2. Demand Forecasting(delivery drivers needs)":"""select order_date, sum(order_value) as daily_revenue
                  from orders
                  group by order_date
                  order by daily_revenue desc limit(10);""",
    "3. Loyalty Analysis( discounts at Premium)":"""select r.category, o.discount_used, count(o.order_id)
                  from restaurants r
                  join orders o ON r.name = o.name
                  where r.cost > 1500
                  group by r.category, o.discount_used ;""",
    "4. The most actual orders(price)":""" SELECT r.cost, COUNT(o.order_id) as total_orders
                    from restaurants r
                    join orders o ON r.name = o.name
                    group by r.cost
                    order by total_orders desc limit(5);""",
    "5. Online vs Offline Efficiency":"""select r.online_order, round(avg(o.order_value), 2) as avg_spend
                    from restaurants r
                    join orders o ON r.name = o.name
                    group by r.online_order;"""
}
selected_q1 = st.selectbox("Choose a Business Case:", list(queries1.keys()))
df_result1 = pd.read_sql_query(queries1[selected_q1], conn)
st.write(df_result1)
conn.commit()
conn.close()
