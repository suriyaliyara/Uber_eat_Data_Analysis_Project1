# STEP 1: Run this in a separate cell first
#-m pip install ftfy
#pip install streamlit pandas ftfy
#python -m pip install ftfy streamlit pandas

import streamlit as st
import pandas as pd
import sqlite3

# 1. Page Setup
st.set_page_config(page_title="UberEats Strategic Insights", layout="wide")

# 2. Database Connection & Data Loading
def get_all_data():
    try:
        conn = sqlite3.connect('uber_eats_analysis.db')
        # Load Tables
        df_res = pd.read_sql_query("SELECT * FROM restaurants", conn)
        df_ord = pd.read_sql_query("SELECT * FROM orders", conn)
        conn.commit()
        conn.close()

        # Merge Restaurants and Orders on the 'name' column
        df_master = pd.merge(df_res, df_ord, on='name', how='left')
        return df_master
    
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()

# Load the master data
df = get_all_data()

# 3. Sidebar - Dynamic Filters
st.sidebar.header("Business Filters")


# Filter: location
location_list = sorted(df['location'].dropna().unique())
selected_location = st.sidebar.multiselect("Select location", options=location_list)


# Filter: Category
cat_list = sorted(df['category'].dropna().unique())
selected_cats = st.sidebar.multiselect("Select Category", options=cat_list)

# Filter: Online Order , Booking , payment_method & discount_used
col1, col2 , col3, col4 = st.sidebar.columns(4)
online_choice = col1.radio("Online Order", ["All", "Yes", "No"])
book_choice = col2.radio("Book Table", ["All", "Yes", "No"])
discount_choice = col1.radio("Discount used", ["All", "Yes", "No"])
payment_choice = col2.radio("Payment Method", ["All", "Cash", "Card","UPI"])

# 4. Applying Dynamic Logic
df_filtered = df.copy()#The original Master List stays safe in your filing cabinet.

if selected_location:
    df_filtered = df_filtered[df_filtered['location'].isin(selected_location)]
    
if selected_cats:
    df_filtered = df_filtered[df_filtered['category'].isin(selected_cats)]

if online_choice != "All":
    df_filtered = df_filtered[df_filtered['online_order'] == online_choice]

if book_choice != "All":
    df_filtered = df_filtered[df_filtered['book_table'] == book_choice]

if discount_choice != "All":
    df_filtered = df_filtered[df_filtered['discount_used'] == discount_choice]    
    
if payment_choice != "All":
    df_filtered = df_filtered[df_filtered['payment_method'] == payment_choice] 

# 5. Main Dashboard Display
st.title(" UberEats Strategic Insights Dashboard")
st.markdown("---")

# High-Level Metrics
m1, m2, m3, m4 = st.columns(4)

m1.metric("Active Restaurants", len(df_filtered['name'].unique()))
m2.metric("Avg Rating", f"{df_filtered['rate'].mean():.2f}")
m3.metric("Avg Votes", f"{df_filtered['votes'].mean():.2f}")
m4.metric("Avg Cost (2 ppl)", f"₹{df_filtered['cost'].mean():.0f}")

st.divider()

# ---  Restaurant List ---
st.subheader("Filtered Restaurant List")
# Displaying only unique names found in the current filter
display_cols = ['name', 'cuisines','dish_liked']
# Check if columns exist before showing table
existing_cols = [c for c in display_cols if c in df_filtered.columns]
st.dataframe(df_filtered[existing_cols].drop_duplicates().reset_index(drop=True) , use_container_width=True)

st.divider()

# 6. Deep Dive SQL Analysis
st.subheader("Strategic Analysis Questions")

queries = {
    "1. Highest average rating location":"""SELECT location,ROUND(SUM(rate * votes) / SUM(votes), 2) AS weighted_avg_rating, ROUND(AVG(rate), 2) AS avg_rating,
                                            sum(votes) as total_votes FROM restaurants where rate > 0 and votes >0
                                            GROUP BY location ORDER BY weighted_avg_rating DESC limit(10)""",
    "2. Over-saturated restaurants":"select location,count(*)as rest_count from restaurants group by location order by rest_count desc limit(10); ",
    "3. Online ordering performance(rating)":"select online_order, round(avg(rate),2)as avg_rate from restaurants where rate > 0 group by online_order;",
    "4. Higher customer ratings(table booking)":"select book_table, round(avg(rate),2)as ratingfrom restaurants where rate > 0 group by book_table; ",
    "5. Customer satisfaction price range":"""select case
                             when cost <= 400 then 'low-price(<400)'
                             when cost >400 and cost <= 1500 then 'mid-price(400-800)'
                             else 'premium-price (>1500)'
                             end as price_segment,  
                            SUM(votes) AS total_votes,COUNT(*) AS restaurant_count
                            FROM restaurants
                            WHERE rate > 0 AND votes > 0 GROUP BY price_segment ORDER BY total_votes DESC;""",
    "6. Price_segment performance(low,mid,permium)":"""s select case
                             when cost <= 400 then 'low-price(<400)'
                             when cost >400 and cost <= 800 then 'mid-price(400-800)'
                             else 'premium-price (>800)'
                             end as price_segment,
                        -- The Weighted Average Formula:
                            ROUND(SUM(rate * votes) / SUM(votes), 2) AS weighted_avg_rating,
                            SUM(votes) AS total_votes,COUNT(*) AS restaurant_count
                            FROM restaurants WHERE rate > 0 AND votes > 0
                            GROUP BY price_segment ORDER BY weighted_avg_rating DESC;""",
    "7. Most common cuisines":"select cuisines,count(*)as rest_count from restaurants group by cuisines order by rest_count desc limit(10);",
    "8. Quality Cuisines (Cuisines by rating)":"""select cuisines,round(avg(rate),2)as rating,count(*)as rest_count
                                    from restaurants where rate >0 group by cuisines having rest_count >30 order by rating  desc limit(10);""",
    "9. Find demand cuisines(High rating but Low volume)":"""select cuisines,round(avg(rate),2)as avg_rating,count(*)as rest_count from restaurants
                                    where rate >0
                                    group by cuisines having rest_count < 15 order by avg_rating  desc limit(10);""",
    "10. Performance of features(Online vs Booking)":"""SELECT CASE
                                    WHEN online_order = 'Yes' AND book_table = 'Yes' THEN 'Both Features'
                                    WHEN online_order = 'Yes' OR book_table = 'Yes' THEN 'One Feature'
                                    ELSE 'No Features'
                                    END as feature_set,
                                    COUNT(*) as rest_count,ROUND(AVG(rate), 2) as avg_rating,SUM(votes) as total_votes
                                    FROM restaurants
                                    WHERE rate > 0
                                    GROUP BY feature_set ORDER BY avg_rating DESC; """,
    "11. Premium Restaurant Locations":""" select location,count(*)as rest_count,
                                    round(avg(cost),2)as avg_cost,sum(votes) as total_votes
                                    from restaurants
                                    where cost > 800
                                    group by location having rest_count >10 order by avg_cost desc, total_votes limit(10); """,
                  
    "12. Top performance(By price_segment)":"""select name,location,cost,rate,votes,price_segment,rank
                                    from(select name,location,cost,rate,votes,
                                    case
                                        when cost <= 400 then 'low-price'
                                        when cost >400 and cost <=800 then 'mid-price'
                                        else 'premium-price'
                                        end as price_segment,row_number()over(partition by
                                    case
                                        when cost <= 400 then 'low-price'
                                        when cost >400 and cost <=800 then 'mid-price'
                                        else 'premium-price'
                                        end order by rate desc,votes desc)as rank

                                    from restaurants where rate > 0) 
                                    where rank <=3 order by price_segment, rank;"""
                  
}

selected_q = st.selectbox("Choose a Business Case:", list(queries.keys()))

#

# Run Selected Query
conn = sqlite3.connect('uber_eats_analysis.db')
df_result = pd.read_sql_query(queries[selected_q], conn)
st.write(df_result)
# 
st.subheader("Order Data  Analysis Questions")

queries1 = {
    "1.payment gateway (Card vs. Cash) to optimize":""" SELECT payment_method, COUNT(*) as order_count, SUM(order_value) as total_revenue
                    FROM orders
                    GROUP BY payment_method
                    ORDER BY total_revenue DESC; """,
    "2. Demand Forecasting(total order value per day)":"""SELECT order_date, SUM(order_value) as daily_revenue
                  FROM orders
                  GROUP BY order_date
                  ORDER BY daily_revenue desc limit(10);""",
    "3. Loyalty Analysis( discounts at Premium)":"""SELECT r.category, o.discount_used, COUNT(o.order_id)
                  FROM restaurants r
                  left JOIN orders o ON r.name = o.name
                  WHERE r.cost > 800
                  GROUP BY r.category, o.discount_used order by COUNT(o.order_id) desc;""",
    "4. The most actual orders(price)":""" SELECT r.cost, COUNT(o.order_id) as total_orders
                    FROM restaurants r
                    JOIN orders o ON r.name = o.name
                    GROUP BY r.cost
                    ORDER BY total_orders DESC LIMIT 5;""",
    "5. Online vs Offline Efficiency":"""SELECT r.online_order, ROUND(AVG(o.order_value), 2) as avg_spend
                    FROM restaurants r
                    JOIN orders o ON r.name = o.name
                    GROUP BY r.online_order;"""
}
selected_q1 = st.selectbox("Choose a Business Case:", list(queries1.keys()))
df_result1 = pd.read_sql_query(queries1[selected_q1], conn)
st.write(df_result1)
conn.commit()
conn.close()

# Display SQL Result



# 7. Raw Data Explorer
#with st.expander("See Raw Filtered Data"):
#     st.dataframe(df_filtered, use_container_width=True)
    


