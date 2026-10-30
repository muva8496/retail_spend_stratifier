import os
import duckdb

# 1. Connect to local DuckDB database file
con = duckdb.connect("vellamo_analytics.duckdb")

# 2. Read and execute the SQL window script
with open(r"C:\Users\Musa\OneDrive\Desktop\day45_window_analytics\windows_perc.sql ") as f:
  sql_script = f.read()

print("Executing window functions on 500,000 orders...")
con.execute(sql_script)

# 3. Query and display the quartile audit summary in Anaconda Prompt
audit_query = """
SELECT 
    category,
    spend_quartile,
    COUNT(*) AS orders,
    ROUND(MIN(amount), 2) AS min_kes,
    ROUND(MAX(amount), 2) AS max_kes,
    ROUND(AVG(amount), 2) AS avg_kes
FROM order_category_percentiles
GROUP BY category, spend_quartile
ORDER BY category, spend_quartile
"""
df_summary = con.execute(audit_query).df()
print("\n--- QUARTILE AUDIT SUMMARY ---")
print(df_summary.to_string(index=False))

# 4. Export lightweight audit CSV for GitHub oversight
con.execute(
    f"COPY ({audit_query}) TO 'quartile_audit_summary.csv' (HEADER, DELIMITER"
    " ',');"
)
print("\nSaved quartile_audit_summary.csv successfully.")

# 5. Optional: Push to MotherDuck if MOTHERDUCK_TOKEN is set in your environment
if os.getenv("MOTHERDUCK_TOKEN"):
  print("Syncing table to MotherDuck...")
  con.execute("ATTACH 'md:';")
  con.execute(
      "CREATE OR REPLACE TABLE my_db.order_category_percentiles AS SELECT *"
      " FROM order_category_percentiles;"
  )
  print("MotherDuck sync complete!")

con.close()