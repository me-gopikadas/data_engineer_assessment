import pandas as pd
from src.extract import extract_valid_objects
from src.transform import (
    normalize_properties,
    normalize_leads,
    normalize_valuation,
    normalize_hoa,
    normalize_rehab,
    normalize_taxes
)
from src.load import MySQLLoader


RAW_JSON = "./data/fake_property_data_new.json"
CLEAN_NDJSON = "./data/clean_data_new.ndjson"

# Extract
print("ETL PIPELINE STARTED")
extract_valid_objects(RAW_JSON, CLEAN_NDJSON)

# Extract
df = pd.read_json("./data/clean_data_new.ndjson", lines=True)
print("✔ Extract completed")

# Transform
props = normalize_properties(df)
dup = props[props.duplicated(subset=["external_id"], keep=False)]
print("\n DUPLICATE external_id rows found:", dup.shape)
print(dup.head(10)[["external_id"]])

leads = normalize_leads(df)
valuation = normalize_valuation(df)
hoa = normalize_hoa(df)
rehab = normalize_rehab(df)
taxes = normalize_taxes(df)

print("Transform completed")
print("props rows:", props.shape)
print("leads rows:", leads.shape)
print("valuation rows:", valuation.shape)
print("hoa rows:", hoa.shape)
print("rehab rows:", rehab.shape)
print("taxes rows:", taxes.shape)

# Load
loader = MySQLLoader(
    user="db_user",
    password="6equj5_db_user",
    host="localhost:3306",
    database="home_db"
)
loader.run_sql_script("./sql/create_tables.sql")
# Load main table
loader.load_properties(props)

# Build external_id → property_id map
id_map = loader.build_external_id_map()

# Add FK to child tables
leads = loader.add_property_id(leads, id_map)
leads = leads.drop(columns=["property_title"], errors="ignore")
valuation = loader.add_property_id(valuation, id_map)
hoa = loader.add_property_id(hoa, id_map)
rehab = loader.add_property_id(rehab, id_map)
taxes = loader.add_property_id(taxes, id_map)

# Load child tables
loader.load_child_table(leads, "leads")
loader.load_child_table(valuation, "valuation")
loader.load_child_table(hoa, "hoa")
loader.load_child_table(rehab, "rehab")
loader.load_child_table(taxes, "taxes")

print("ALL DATA LOADED INTO MYSQL SUCCESSFULLY!")