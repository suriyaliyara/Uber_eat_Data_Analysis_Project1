
# Uber Eats Bangalore: Market Intelligence & Data Engineering

### Project Overview
This project is a comprehensive **End-to-End Data Engineering and Analytics** solution for the Bangalore restaurant market. It processes large-scale restaurant and order data to provide actionable insights for business stakeholders, such as identifying premium locations and evaluating the ROI of platform features.

---

### The Tech Stack
* **Language:** Python 3.x
* **Data Processing:** Pandas (ETL Pipeline)
* **Database:** SQLite (Relational Data Modeling)
* **Dashboard:** Streamlit (Business Intelligence UI)


---

### Data Architecture & Sources
The project integrates multi-format data sources to simulate a real-world big data environment:
1.  **Restaurant Data (CSV):** Detailed information on locations, cuisines, and costs.
2.  **Order Data (JSON):** Key-value pair data representing customer engagement and transaction types.

---

### Pipeline Workflow (ETL)
1.  **Extraction:** Loading raw CSV and JSON files into the Python environment.
2.  **Transformation:** * Handling missing values and removing duplicates.
    * Data type standardization (Rates, Costs, and Phone numbers).
    * Implementing **Weighted Average Rating** logic to ensure data accuracy.
3.  **Loading:** Creating a structured SQLite database and migrating cleaned DataFrames into relational tables.
4.  **Analysis:** Executing SQL queries to solve specific business problems (e.g., Price Segment vs. Satisfaction).

---

### Key Business Insights
* **Feature Impact:** Analyzed how **Table Booking** and **Online Ordering** correlate with a ~0.26 point increase in customer ratings.
* **Market Segmentation:** Identified the **Mid-Price (₹400-800)** segment as the "Sweet Spot" for partner success.
* **Geospatial Performance:** Ranked Bangalore neighborhoods based on weighted satisfaction scores to guide new branch onboarding.

---

###  How to Run the Project
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/uber-eats-analysis.git](https://github.com/your-username/uber-eats-analysis.git)
Install dependencies:

Bash
pip install pandas streamlit plotly
Run the Dashboard:

Bash
streamlit run app.py