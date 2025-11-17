-- properties (main)
CREATE TABLE IF NOT EXISTS properties (
  property_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  external_id VARCHAR(512) UNIQUE,
  property_title VARCHAR(512),          -- Property_Title used as natural key
  address VARCHAR(512),
  market VARCHAR(128),
  flood VARCHAR(64),
  street_address VARCHAR(255),
  city VARCHAR(128),
  state VARCHAR(64),
  zip VARCHAR(32),
  property_type VARCHAR(64),
  highway VARCHAR(64),
  train VARCHAR(64),
  tax_rate DECIMAL(8,4),
  sqft_basement INT,
  htw VARCHAR(16),
  pool VARCHAR(16),
  commercial VARCHAR(16),
  water VARCHAR(64),
  sewage VARCHAR(64),
  year_built INT,
  sqft_mu INT,
  sqft_total VARCHAR(64),
  parking VARCHAR(128),
  bed INT,
  bath INT,
  basement_yes_no VARCHAR(16),
  layout VARCHAR(64),
  rent_restricted VARCHAR(8),
  neighborhood_rating INT,
  latitude DOUBLE,
  longitude DOUBLE,
  subdivision VARCHAR(255),
  school_average DECIMAL(5,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- leads
CREATE TABLE IF NOT EXISTS leads (
  lead_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  property_id BIGINT NOT NULL,
  reviewed_status VARCHAR(128),
  most_recent_status VARCHAR(128),
  source VARCHAR(128),
  occupancy VARCHAR(128),
  net_yield DECIMAL(8,4),
  irr DECIMAL(8,4),
  selling_reason VARCHAR(255),
  seller_retained_broker VARCHAR(255),
  final_reviewer VARCHAR(255),
  FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE
);

-- valuation
CREATE TABLE IF NOT EXISTS valuation (
  valuation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  property_id BIGINT NOT NULL,
  list_price DECIMAL(18,2),
  previous_rent DECIMAL(12,2),
  zestimate DECIMAL(18,2),
  arv DECIMAL(18,2),
  expected_rent DECIMAL(12,2),
  rent_zestimate DECIMAL(12,2),
  low_fmr DECIMAL(12,2),
  high_fmr DECIMAL(12,2),
  redfin_value DECIMAL(18,2),
  raw_json JSON,
  FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE
);

-- hoa
CREATE TABLE IF NOT EXISTS hoa (
  hoa_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  property_id BIGINT NOT NULL,
  hoa_amount DECIMAL(12,2),
  hoa_flag VARCHAR(16),
  raw_json JSON,
  FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE
);

-- rehab
CREATE TABLE IF NOT EXISTS rehab (
  rehab_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  property_id BIGINT NOT NULL,
  underwriting_rehab DECIMAL(18,2),
  rehab_calculation DECIMAL(18,2),
  paint VARCHAR(16),
  flooring_flag VARCHAR(16),
  foundation_flag VARCHAR(16),
  roof_flag VARCHAR(16),
  hvac_flag VARCHAR(16),
  kitchen_flag VARCHAR(16),
  bathroom_flag VARCHAR(16),
  appliances_flag VARCHAR(16),
  windows_flag VARCHAR(16),
  landscaping_flag VARCHAR(16),
  trashout_flag VARCHAR(16),
  raw_json JSON,
  FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE
);

-- taxes
CREATE TABLE IF NOT EXISTS taxes (
  taxes_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  property_id BIGINT NOT NULL,
  taxes_amount DECIMAL(18,2),
  FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE
);
