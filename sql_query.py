#1.Which Bangalore locations have the highest average restaurant ratings?
import pandas as pd
import sqlite3

# 1. Create the Bridge
conn = sqlite3.connect('uber_eats_analysis.db')  #Open the connection ONCE at the start

# 2. Create the Worker (This is where the Cursor comes from!)

# Using 'with' automatically handles cursor.close() for you
with conn: 
    cursor = conn.cursor() 

# 3. Execute using the Cursor (The "Messenger")
    cursor.execute("""
    SELECT location,
           ROUND(AVG(rate), 2) AS avg_rating,
           sum(votes) as total_votes
    FROM restaurants
    where rate > 0
    GROUP BY location having total_votes > 50
    ORDER BY avg_rating DESC limit(10);""")

# 4. Fetch the data from the Cursor
    rows = cursor.fetchall()

# 5. Get column names from the Cursor description
# This ensures your table has the correct headers (location, avg_rating, etc.)
    columns = [column[0] for column in cursor.description]

# 6. Create the DataFrame (The "Tabular Format")
    df_results = pd.DataFrame(rows, columns=columns)


# 7. Display the result
    print("--- STRATEGIC INSIGHT: TOP 10 PREMIUM LOCATIONS ---")
# Use display() if in Jupyter/Colab or st.dataframe() if in Streamlit
    print(df_results.to_string(index=False))
#conn.close()


#cursor.execute(): Sent the logic to the SQLite engine.
#cursor.fetchall(): Grabbed the matching rows.

#cursor.description: Automatically found the column names so we didn't have to type them manually.
#1.FROM,2.GROUP BY,3.SELECT (Aggregates)	Doing the Math (AVG, COUNT),4.HAVING,5.ORDER BY,6.LIMIT

# %%
#2.Which locations are over-saturated with restaurants?
 #Business Value: Helps avoid overcrowded markets and guides smarter expansion decisions.
with conn:
    cursor = conn.cursor()
    cursor.execute(""" select location,count(*)as rest_count from restaurants
                    group by location
                    order by rest_count desc limit(10); """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %%


# %%
 #3. Does online ordering improve restaurant ratings?
 #Business Value: Evaluates the ROI of Uber Eats’ online ordering feature for partners.

with conn:
    cursor = conn.cursor()
    cursor.execute(""" select online_order, round(avg(rate),2)as avg_rate
                    from restaurants where rate > 0
                    group by online_order; """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
    #conn.close()

# %%
#4. Does table booking correlate with higher customer ratings?
#Business Value: Measures the effectiveness of table booking as a premium feature.

with conn:
    cursor = conn.cursor()
    cursor.execute(""" select book_table, round(avg(rate),2)as rating
                  from restaurants
                  where rate > 0
                  group by book_table; """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
    #conn.close()

# %%
#5. What price range delivers the best customer satisfaction?
 #Business Value: Helps define the optimal pricing segment for partner success
with conn:
    cursor = conn.cursor()
    cursor.execute(""" select cost, round(avg(rate),2)as avg_rating,
                  count(*)as rest_count
                  from restaurants
                  where rate > 0
                  group by cost
                  having rest_count >10
                  order by avg_rating desc limit(10); """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
    #conn.close()

# %%
#6.How do low, mid, and premium-priced restaurants perform in terms of ratings?
 #Business Value: Supports pricing-based market segmentation strategies.

with conn:
    cursor = conn.cursor()
    cursor.execute(""" select case
                             when cost <= 400 then 'low-price(<400)'
                             when cost >400 and cost <= 800 then 'mid-price(400-800)'
                             else 'premium-price (>800)'
                             end as price_segment,
                  round(avg(rate),2)as avg_rating
                  from restaurants
                  where rate > 0
                  group by price_segment; """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))

# %%
#7.Which cuisines are most common in Bangalore?
 #Business Value: Reveals market demand and cuisine saturation levels.
with conn:
    conn = sqlite3.connect('uber_eats_analysis.db')
    cursor = conn.cursor()
    cursor.execute(""" select cuisines,
                   count(*)as rest_count
                  from restaurants
                  group by cuisines order by rest_count desc limit(10); """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %% [markdown]
# FROM: Gets the table.
# 
# WHERE: Throws away the 0-rated rows.
# 
# GROUP BY: Sorts remaining rows into Cuisine buckets.
# 
# SELECT (COUNT/AVG): Does the math for each bucket.
# 
# HAVING: Throws away buckets with fewer than 31 restaurants.
# 
# ORDER BY: Sorts the winners to the top.
# 
# LIMIT: Gives you the Top 10.

# %%
#8. Which cuisines receive the highest average ratings?
 #Business Value: Identifies high-quality cuisine categories suitable for promotion.

with conn:
    cursor = conn.cursor()
    cursor.execute(""" select cuisines,
                  round(avg(rate),2)as rating,count(*)as rest_count
                  from restaurants
                  where rate >0
                  group by cuisines
                  having rest_count >30
                  order by rating  desc limit(10); """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))


# %%
#9. Which cuisines perform well despite having fewer restaurants?
 #Business Value: Highlights niche opportunities for differentiation
with conn:
    cursor = conn.cursor()
    cursor.execute(""" select cuisines,
                  round(avg(rate),2)as avg_rating,count(*)as rest_count
                  from restaurants
                  where rate >0
                  group by cuisines
                  having rest_count < 15
                  order by avg_rating  desc limit(10); """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %%
#10. What is the relationship between restaurant cost and rating?
 #Business Value: Determines whether higher pricing translates to better customer perception.
with conn:
    cursor = conn.cursor()
    cursor.execute(""" select cost,
                  round(avg(rate),2)as avg_rating
                  from restaurants
                  where rate >0
                  group by cost
                  order by cost  desc limit(10); """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %%
#11. Which locations are ideal for premium restaurant onboarding? where cost > 700  -- Focusing on high-end segments
 #Business Value: Combines cost, rating, and location insights to guide premium expansion
with conn:
    cursor = conn.cursor()
    cursor.execute(""" select location,
                  count(*)as rest_count,
                  round(avg(cost),2)as avg_cost,
                  sum(votes) as total_votes
                  from restaurants
                  where cost > 800
                  group by location
                  having rest_count >10 order by avg_cost desc, total_votes limit(10); """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %%
#12. Which locations show high demand but lower average ratings?
 #Business Value: Indicates areas where quality improvement initiatives are needed.
with conn:
    cursor = conn.cursor()
    cursor.execute(""" select location,
                  round(avg(rate),2)as avg_rating,
                  sum(votes) as total_votes,
                  count(*)as rest_count
                  from restaurants
                  where rate > 0
                  group by location
                  having total_votes > 1000 and avg_rating < 3.5
                  order by total_votes desc limit(10); """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %%
#13. Do restaurants offering both online ordering and table booking perform better?
 #Business Value: Validates bundled feature adoption for partners.
with conn:
    cursor = conn.cursor()
    cursor.execute(""" SELECT CASE
                WHEN online_order = 'Yes' AND book_table = 'Yes' THEN 'Both Features'
                WHEN online_order = 'Yes' OR book_table = 'Yes' THEN 'One Feature'
                ELSE 'No Features'
                END as feature_set,
                COUNT(*) as rest_count,
                ROUND(AVG(rate), 2) as avg_rating,
                SUM(votes) as total_votes
                FROM restaurants
                WHERE rate > 0
                GROUP BY feature_set ORDER BY avg_rating DESC; """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %%
#14. What combination of factors maximizes restaurant success on Uber Eats?
 #(Pricing + Location + Cuisine + Platform Features)
 #Business Value: Supports strategic partner recommendations.
with conn:
    cursor = conn.cursor()
    cursor.execute(""" select location,round(avg(cost),2) as avg_cost,
                  cuisines,rest_type,
                  online_order,book_table
                  from restaurants
                  where rate >= 4.5
                  group by cuisines,location
                  order by sum(votes) desc limit(10);""")

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#onn.close()

# %%
#15. Which restaurants are top performers within each pricing segment?
#Business Value: Helps identify benchmark partners and best practices.
with conn:
    cursor = conn.cursor()
    cursor.execute(""" select name,location,cost,rate,votes,price_segment,rank
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

                  from restaurants
                  where rate > 0) where rank <=3
                  order by price_segment, rank; """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()


# %%
#print(df_cleaned.dtypes)

# %%
 #Expectation: 'Yes' usually has higher ratings than 'No'.
#1. Revenue Leakage: Which payment method is most popular for high-value orders?
#Business Value: Helps the finance team decide which payment gateway (Card vs. Cash) to optimize.

with conn:
    cursor = conn.cursor()
    cursor.execute(""" SELECT payment_method, COUNT(*) as order_count, SUM(order_value) as total_revenue
                    FROM orders
                    GROUP BY payment_method
                    ORDER BY total_revenue DESC; """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %%
#2. Demand Forecasting: What is the total order value per day?
#Business Value: Helps the logistics team predict how many delivery drivers are needed on specific dates.

with conn:
    cursor = conn.cursor()
    cursor.execute("""SELECT order_date, SUM(order_value) as daily_revenue
                  FROM orders
                  GROUP BY order_date
                  ORDER BY daily_revenue desc limit(10);""")

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %%
#3. Loyalty Analysis: Are customers using discounts at "Premium" (High Cost) restaurants?
#Business Value: Checks if wealthy diners care about discounts or if they prioritize quality.

with conn:
    cursor = conn.cursor()
    cursor.execute("""SELECT r.category, o.discount_used, COUNT(o.order_id)
                  FROM restaurants r
                  left JOIN orders o ON r.name = o.name
                  WHERE r.cost > 800
                  GROUP BY r.category, o.discount_used order by COUNT(o.order_id) desc;""")

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %%
#4. The "Sweet Spot" Finder: Which cost range generates the most actual orders?
#Business Value: Identifies the price point that brings in the most "Cash Flow."

with conn:
    cursor = conn.cursor()
    cursor.execute(""" SELECT r.cost, COUNT(o.order_id) as total_orders
                    FROM restaurants r
                    JOIN orders o ON r.name = o.name
                    GROUP BY r.cost
                    ORDER BY total_orders DESC LIMIT 5;""")

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %%
#5. Operational Efficiency: Average order value for "Online" vs "Offline" restaurants?
#Business Value: Proves if online customers spend more than walk-in customers.

with conn:
    cursor = conn.cursor()
    cursor.execute( """SELECT r.online_order, ROUND(AVG(o.order_value), 2) as avg_spend
                    FROM restaurants r
                    JOIN orders o ON r.name = o.name
                    GROUP BY r.online_order;""")

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
#conn.close()

# %%
with conn:
    cursor = conn.cursor()
    cursor.execute( """SELECT r.online_order, ROUND(AVG(o.order_value), 2) as avg_spend
                    FROM restaurants r
                    JOIN orders o ON r.name = o.name
                    GROUP BY r.online_order;""")

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df_results = pd.DataFrame(rows, columns=columns)
    print(df_results.to_string(index=False))
conn.close()