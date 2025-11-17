# etl/transform.py
import pandas as pd
from pandas import json_normalize

def normalize_properties(df):
    # Columns coming from cleaned JSON
    prop_cols = [
        "Property_Title","Address","Market","Flood","Street_Address","City","State","Zip",
        "Property_Type","Highway","Train","Tax_Rate","SQFT_Basement","HTW","Pool","Commercial",
        "Water","Sewage","Year_Built","SQFT_MU","SQFT_Total","Parking","Bed","Bath","BasementYesNo",
        "Layout","Rent_Restricted","Neighborhood_Rating","Latitude","Longitude","Subdivision",
        "School_Average"
    ]

    props = df[prop_cols].copy()

    # Clean SQFT_Total ("5649 sqft" -> 5649)
    props["SQFT_Total"] = (
        props["SQFT_Total"].astype(str)
        .str.replace(" sqft", "", regex=False)
        .str.strip()
    )
    props["SQFT_Total"] = pd.to_numeric(props["SQFT_Total"], errors="coerce")

    # Proper renaming
    props = props.rename(columns={
        "Property_Title": "property_title",
        "Address": "address",
        "Market": "market",
        "Flood": "flood",
        "Street_Address": "street_address",
        "City": "city",
        "State": "state",
        "Zip": "zip",
        "Property_Type": "property_type",
        "Highway": "highway",
        "Train": "train",
        "Tax_Rate": "tax_rate",
        "SQFT_Basement": "sqft_basement",
        "HTW": "htw",
        "Pool": "pool",
        "Commercial": "commercial",
        "Water": "water",
        "Sewage": "sewage",
        "Year_Built": "year_built",
        "SQFT_MU": "sqft_mu",
        "SQFT_Total": "sqft_total",
        "Parking": "parking",
        "Bed": "bed",
        "Bath": "bath",
        "BasementYesNo": "basement_yes_no",
        "Layout": "layout",
        "Rent_Restricted": "rent_restricted",
        "Neighborhood_Rating": "neighborhood_rating",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Subdivision": "subdivision",
        "School_Average": "school_average"
    })

    # Natural key
    props["external_id"] = props["property_title"].astype(str).str.strip()
    props["property_title"] = props["property_title"].astype(str).str.strip()

    # Final column ordering
    ordered_cols = [
        "external_id","property_title","address","market","flood","street_address","city","state","zip",
        "property_type","highway","train","tax_rate","sqft_basement","htw","pool","commercial","water",
        "sewage","year_built","sqft_mu","sqft_total","parking","bed","bath","basement_yes_no","layout",
        "rent_restricted","neighborhood_rating","latitude","longitude","subdivision","school_average"
    ]

    props = props[ordered_cols]
    props = props.drop_duplicates(subset=["external_id"])

    return props


def normalize_leads(df):
    lead_cols = ["Property_Title","Reviewed_Status","Most_Recent_Status","Source","Occupancy","Net_Yield","IRR","Selling_Reason","Seller_Retained_Broker","Final_Reviewer"]
    leads = df[lead_cols].copy().rename(columns={
        "Property_Title":"property_title",
        "Reviewed_Status":"reviewed_status",
        "Most_Recent_Status":"most_recent_status",
        "Source":"source",
        "Occupancy":"occupancy",
        "Net_Yield":"net_yield",
        "IRR":"irr",
        "Selling_Reason":"selling_reason",
        "Seller_Retained_Broker":"seller_retained_broker",
        "Final_Reviewer":"final_reviewer"
    })
    # add external_id
    leads["external_id"] = leads["property_title"].str.strip()
    # Keep only rows that have at least one not-null lead field (avoid creating empty leads)
    leads = leads.dropna(subset=["reviewed_status","most_recent_status","source","net_yield","irr","selling_reason","final_reviewer"], how="all")
    return leads

def explode_array(df, array_col, prefix_map=None):
    """
    Explode a column containing list-of-dicts into a flattened dataframe.
    prefix_map: optional dict to rename nested fields to desired columns
    returns df with external_id and flattened fields.
    """
    records = []
    for _, row in df.iterrows():
        ext = row.get("Property_Title")
        arr = row.get(array_col)
        if not arr:
            continue
        for item in arr:
            flat = item.copy()
            flat["external_id"] = str(ext).strip()
            records.append(flat)
    if not records:
        return pd.DataFrame()
    out = json_normalize(records)
    if prefix_map:
        out = out.rename(columns=prefix_map)
    return out

# Example wrappers:
def normalize_valuation(df):
    prefix_map = {
        "List_Price":"list_price",
        "Previous_Rent":"previous_rent",
        "Zestimate":"zestimate",
        "ARV":"arv",
        "Expected_Rent":"expected_rent",
        "Rent_Zestimate":"rent_zestimate",
        "Low_FMR":"low_fmr",
        "High_FMR":"high_fmr",
        "Redfin_Value":"redfin_value"
    }
    val = explode_array(df, "Valuation", prefix_map)
    # cast numeric cols
    num_cols = ["list_price","previous_rent","zestimate","arv","expected_rent","rent_zestimate","low_fmr","high_fmr","redfin_value"]
    for c in num_cols:
        if c in val.columns:
            val[c] = pd.to_numeric(val[c], errors="coerce")
    return val

def normalize_hoa(df):
    prefix_map = {"HOA":"hoa_amount","HOA_Flag":"hoa_flag"}
    hoa = explode_array(df, "HOA", prefix_map)
    if "hoa_amount" in hoa.columns:
        hoa["hoa_amount"] = pd.to_numeric(hoa["hoa_amount"], errors="coerce")
    return hoa

def normalize_rehab(df):
    prefix_map = {
        "Underwriting_Rehab":"underwriting_rehab",
        "Rehab_Calculation":"rehab_calculation",
        "Paint":"paint","Flooring_Flag":"flooring_flag","Foundation_Flag":"foundation_flag",
        "Roof_Flag":"roof_flag","HVAC_Flag":"hvac_flag","Kitchen_Flag":"kitchen_flag",
        "Bathroom_Flag":"bathroom_flag","Appliances_Flag":"appliances_flag","Windows_Flag":"windows_flag",
        "Landscaping_Flag":"landscaping_flag","Trashout_Flag":"trashout_flag"
    }
    rehab = explode_array(df, "Rehab", prefix_map)
    # cast numeric
    for c in ["underwriting_rehab","rehab_calculation"]:
        if c in rehab.columns:
            rehab[c] = pd.to_numeric(rehab[c], errors="coerce")
    return rehab

def normalize_taxes(df):
    taxes = df[["Property_Title","Taxes"]].copy().rename(columns={"Property_Title":"external_id","Taxes":"taxes_amount"})
    taxes["taxes_amount"] = pd.to_numeric(taxes["taxes_amount"], errors="coerce")
    taxes = taxes.dropna(subset=["taxes_amount"])
    return taxes
