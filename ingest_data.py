# STEP 1: Run this in a separate cell first

import pandas as pd
import re #regular expression
import ftfy # "It used the ftfy library to handle text encoding issues.
import streamlit as st
import sqlite3

# --- RULE 1: ENCODING FIX (The "Café" Mess) ---
def rule_1_encoding(text):
    if pd.isna(text): return text
    # ftfy untangles "CafÃƒÂƒÃ‚Â..." back to "Cafe" or "Café"
    return ftfy.fix_text(str(text)) #fix_text is function

 # --- RULE 2: NAME SANITIZATION ---
def rule_2_names(text):
    if pd.isna(text): return text
    # Removes unwanted symbols like # but keeps letters and numbers
    text = re.sub(r'[^a-zA-Z0-9 ]', '', str(text))#Before Python can perform a search-and-replace, it must be 100% sure the data is a String(Purpose: To ensure Data Consistency)
    return re.sub(r'\s+', ' ', text).strip() #This looks at the very beginning and the very end of the text. If there are any spaces hanging off the edges, it cuts them off.
    #r = Tells Python to ignore the "Special" meaning and keep it Raw
    #\s = Find Spaces \d = Find Digits \w = Find Words

# --- RULE 3: PHONE NUMBER SEPARATOR (The "\r\n" Issue) ---
def rule_3_phone(text):
    if pd.isna(text): return text
    # Replace line breaks with a comma
    text = str(text).replace('\r', ' ').replace('\n', ', ')
    # Add comma before a '+' if it's stuck to a number
    text = re.sub(r'(\d)\s*\+', r'\1, +', text)
    # Keep digits, +, and commas
    text = re.sub(r'[^0-9+, ]', '', text)
    return re.sub(r'\s+', ' ', text).strip().strip(',')

# --- RULE 4: RATINGS (4.1/5 -> 4.1) ---
def rule_4_rate(text):
    if pd.isna(text): return text
    val = str(text).split('/')[0].strip()
    # Handle "NEW" or "-" values common in Uber Eats data
    return val if val not in ['NEW', '-'] else "0"

# --- RULE 5: LISTS (Cuisines, Dish Liked) ---
def rule_5_lists(text):
    if pd.isna(text): return text
    # Keeps letters, numbers, and commas so you can split them later
    return re.sub(r'[^a-zA-Z0-9, ]', '', str(text)).strip()

# --- RULE 6: APPROX COST (1,200 -> 1200) ---
def rule_6_cost(text):
    if pd.isna(text): return text
    # Remove commas and non-numeric characters for math analysis
    return re.sub(r'[^0-9.]', '', str(text))

    

    # --- EXECUTION: APPLYING RULES TO COLUMNS ---

def uber_eats_master_cleaner(df_rest):

    # Apply Encoding & Name Cleanup
    if 'name' in df_rest.columns:
        df_rest['name'] = df_rest['name'].apply(rule_1_encoding)

    # Apply Phone Cleanup
    if 'phone' in df.columns:
        df_rest['phone'] = df_rest['phone'].apply(rule_3_phone)

    # Apply Rate Cleanup
    if 'rate' in df.columns:
        df_rest['rate'] = df_rest['rate'].apply(rule_4_rate)

    # Apply List Cleanup
    for col in ['rest_type', 'dish_liked', 'cuisines']:
        if col in df.columns:
            df_rest[col] = df_rest[col].apply(rule_5_lists)

    # Apply Cost Cleanup
    cost_col = 'approx_cost(for two people)'
    if cost_col in df.columns:
        df_rest[cost_col] = df_rest[cost_col].apply(rule_6_cost)

    # General Cleanup for Location/City/Online Order
    for col in ['location', 'listed_in(city)', 'online_order', 'book_table']:
        if col in df.columns:
            df_rest[col] = df_rest[col].apply(rule_2_names)

    return df_rest

# --- RUNNING THE PIPELINE ---
df = pd.read_csv(r"C:\Users\Niruban\Documents\Suriya\HCLGUVI\Project_1\Raw_File\Uber_Eats_data.csv")

#"C:\Users\Niruban\Documents\Suriya\HCLGUVI\Project_1\Raw_File"
df_rest = df.drop_duplicates()
df_cleaned = uber_eats_master_cleaner(df_rest)
#Rename the Column
df_cleaned = df_cleaned.rename(columns={
    'approx_cost(for two people)': 'cost',
    'listed_in(type)': 'category',
    'listed_in(city)': 'city'
})

# Final step: Convert numeric columns to proper types
df_cleaned['rate'] = pd.to_numeric(df_cleaned['rate'], errors='coerce').fillna(0)
df_cleaned['cost'] = pd.to_numeric(df_cleaned['cost'], errors='coerce').fillna(0)
df_cleaned=df_cleaned.drop_duplicates()
print(df_cleaned.head(200)) #23151 rows × 13 columns

#Step 2
#Order Datset Load and Dat Clean
def uber_orders_cleaner(df_orders):

        # Apply Encoding & Name Cleanup
    if 'name' in df_orders.columns:
        df2['name'] = df2['name'].apply(rule_1_encoding)

    # Apply Cost Cleanup
    cost_col = 'order_value'
    if cost_col in df_orders.columns:
        df2[cost_col] = df2[cost_col].apply(rule_6_cost)

    # General Cleanup for Location/City/Online Order
    for col in ['discount_used','payment_method']:
        if col in df_orders.columns:
            df2[col] = df2[col].apply(rule_2_names)

    return df2

# --- RUNNING THE PIPELINE ---
df_orders = pd.read_json(r"C:\Users\Niruban\Documents\Suriya\HCLGUVI\Project_1\Raw_File\orders.json")
df2= df_orders.drop_duplicates()
df2["order_date"] = pd.to_datetime(df2["order_date"])
df2["order_date"] = df2["order_date"].dt.strftime("%Y-%m-%d")
df2 = df2.rename(columns={'restaurant_name': 'name'})
df1_cleaned = uber_orders_cleaner(df2)

# Final step: Convert numeric columns to proper types
df1_cleaned['order_value'] = pd.to_numeric(df1_cleaned['order_value'], errors='coerce').fillna(0)
df1_cleaned=df1_cleaned.drop_duplicates()
print(df1_cleaned.head(50))
 
#Step2:Connection Details
# 1. Connect to (or create) the permanent database file
conn = sqlite3.connect('uber_eats_analysis.db')
cursor = conn.cursor()

# Delete the old tables if they exist
cursor.execute("DROP TABLE IF EXISTS restaurants")
cursor.execute("DROP TABLE IF EXISTS orders")

# 1. Create the 'restaurants' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS restaurants (
    name TEXT,
    online_order TEXT,
    book_table TEXT,
    rate REAL,
    votes INTEGER,
    phone TEXT,
    location TEXT,
    rest_type TEXT,
    dish_liked TEXT,
    cuisines TEXT,
    cost REAL,
    category TEXT,
    city TEXT
)
''')
# 2. Create the 'orders' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    name TEXT,
    order_date TEXT,
    order_value REAL,
    discount_used TEXT,
    payment_method TEXT
)
''')

#SQLite stores dates as TEXT, REAL, or INTEGER.
# --- STEP : LOAD (TO SQLITE) ---

# 2A. IMPORTANT: Convert DataFrame to List of Tuples for the cursor
# This is the "bridge" between Pandas and SQLite
data_to_insert = list(df_cleaned.itertuples(index=False, name=None))
data_to_insert1 = list(df1_cleaned.itertuples(index=False, name=None))

# 2B. The INSERT Query
insert_query = '''
INSERT INTO restaurants (
    name, online_order, book_table, rate, votes, phone, 
    location, rest_type, dish_liked, cuisines, cost, category, city
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

insert_query1 = '''
INSERT INTO orders (
    order_id,name,order_date,order_value,discount_used,payment_method
) VALUES (?, ?, ?, ?, ?, ?)
'''

# 2C. Execute and COMMIT
cursor.executemany(insert_query, data_to_insert)
cursor.executemany(insert_query1, data_to_insert1)

print(f" Successfully cleaned and inserted {len(data_to_insert)} rows into SQLite")
print(f" Successfully cleaned and inserted {len(data_to_insert1)} rows into SQLite")

print("Database Layer Ready. Table 'restaurants and orders' created.")

# Use the cursor to count total rows
cursor.execute("SELECT COUNT(*) FROM restaurants")
row_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM orders")
row_count1 = cursor.fetchone()[0]

print(f"Total records in SQLite table: {row_count}")
print(f"Total records in original DataFrame: {len(df_cleaned)}")

print(f"Total records in SQLite table: {row_count1}")
print(f"Total records in original DataFrame: {len(df1_cleaned)}")

if row_count == len(df_cleaned):
    print("Success: All records inserted perfectly")
else:
    print("Warning: Row count mismatch.")

if row_count1 == len(df1_cleaned):
    print("Success: All records inserted perfectly")
else:
    print("Warning: Row count mismatch.")

conn.commit()
conn.close()


    


