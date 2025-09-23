# Logistics Demo Data Structure Skeleton
# Raw Data Format Guidelines for Comprehensive Demo Datasets

## Overview
This document defines the standardized raw data structure for creating realistic logistics demo datasets that simulate real-world data sources (Motive ELD, Alvys TMS, fuel networks, maintenance systems). All datasets should follow this structure to ensure consistency and agent compatibility.

## Data Philosophy
- **Raw Data Only**: No pre-calculated reports or formatted outputs
- **Realistic Complexity**: Data should require processing and analysis by agents
- **Cross-System Integration**: Data points that connect across multiple platforms
- **Performance Spectrum**: Include high, average, and low performers across all metrics
- **Token Efficiency**: Compact but comprehensive data representation

---

## 1. Fleet & Vehicle Master Data

### Vehicle Registry (`vehicles.json`)
```json
Structure:
- vehicle_id, make, model, year, vin
- vehicle_type, engine_type, fuel_capacity
- acquisition_date, mileage, engine_hours
- assigned_driver_id, current_status
- insurance_info, registration_details
```

### Trailer Registry (`trailers.json`)
```json
Structure:
- trailer_id, trailer_type, capacity, year
- current_location, assigned_truck
- inspection_status, maintenance_due
- specialized_equipment_flags
```

---

## 2. Real-Time Operational Data (Motive ELD Simulation)

### GPS Tracking Data (`gps_tracking.json`)
```json
Structure:
- timestamp, vehicle_id, driver_id
- latitude, longitude, speed, heading
- odometer_reading, engine_status
- current_load_id, route_status
```

### Hours of Service Logs (`hos_logs.json`)
```json
Structure:
- timestamp, driver_id, duty_status
- location, odometer_reading
- remaining_drive_time, remaining_duty_time
- violation_flags, break_requirements
```

### Driver Performance Events (`driver_events.json`)
```json
Structure:
- timestamp, driver_id, vehicle_id
- event_type, severity, duration
- location, speed_at_event
- coaching_flag, safety_score_impact
```

---

## 3. Load & Route Management (Alvys TMS Simulation)

### Load Master Data (`loads.json`)
```json
Structure:
- load_id, customer_id, load_type
- pickup_location, delivery_location
- scheduled_pickup, scheduled_delivery
- actual_pickup, actual_delivery
- revenue, weight, distance
- assigned_driver, assigned_vehicle
- load_status, exception_codes
```

### Route Performance (`route_history.json`)
```json
Structure:
- load_id, route_segments
- planned_vs_actual_time, fuel_consumed
- tolls, permits, detention_time
- driver_performance_score
```

---

## 4. Customer Data (Alvys TMS Simulation)

### Customer Master (`customers.json`)
```json
Structure:
- customer_id, company_name, industry
- contract_terms, payment_terms
- rate_structure, volume_commitments
- service_requirements, special_handling
```

### Customer Transaction History (`customer_transactions.json`)
```json
Structure:
- transaction_id, customer_id, load_id
- invoice_amount, payment_date
- service_scores, complaint_flags
- relationship_status, growth_indicators
```

---

## 5. Fuel Management Data

### Fuel Transactions (`fuel_transactions.json`)
```json
Structure:
- transaction_id, timestamp, vehicle_id, driver_id
- fuel_network, station_id, location
- gallons_purchased, price_per_gallon
- total_cost, discounts_applied
- odometer_reading, fuel_efficiency_calc
```

### Fuel Network Pricing (`fuel_pricing.json`)
```json
Structure:
- timestamp, network_name, region
- base_price, fleet_discount
- location_id, grade_type
- market_conditions, pricing_trends
```

---

## 6. Maintenance & Fleet Health Data

### Maintenance Records (`maintenance_history.json`)
```json
Structure:
- service_id, vehicle_id, service_date
- service_type, mileage_at_service
- parts_cost, labor_cost, total_cost
- service_provider, warranty_info
- next_service_due, preventive_flag
```

### Vehicle Diagnostics (`vehicle_diagnostics.json`)
```json
Structure:
- timestamp, vehicle_id, diagnostic_code
- system_affected, severity_level
- resolution_status, cost_impact
- predictive_maintenance_flag
```

### DOT Compliance Tracking (`dot_compliance.json`)
```json
Structure:
- vehicle_id, inspection_date, expiration_date
- inspector_id, location, results
- violations, corrective_actions
- reinspection_required, compliance_score
```

---

## 7. Financial Transaction Data

### Cost Allocation (`cost_records.json`)
```json
Structure:
- transaction_id, load_id, cost_category
- amount, allocation_method
- accounting_period, profit_center
- driver_settlements, owner_operator_splits
```

### Revenue Recognition (`revenue_records.json`)
```json
Structure:
- revenue_id, load_id, customer_id
- base_rate, accessorials, fuel_surcharge
- detention_pay, total_revenue
- collection_status, margin_analysis
```

---

## 8. Driver Master Data

### Driver Registry (`drivers.json`)
```json
Structure:
- driver_id, name, employment_type (company/owner_operator)
- license_info, medical_cert_expiration
- hire_date, performance_rating
- assigned_vehicle, home_terminal
- contact_info, emergency_contacts
```

### Driver Qualifications (`driver_qualifications.json`)
```json
Structure:
- driver_id, certification_type, issue_date, expiration_date
- training_records, safety_scores
- violation_history, drug_test_records
- performance_reviews, coaching_notes
```

---

## Data Generation Guidelines

### Performance Distribution
- **Top Performers (15%)**: Exceptional metrics across categories
- **Above Average (25%)**: Better than fleet average performance
- **Average Performers (35%)**: At or near fleet benchmarks
- **Below Average (20%)**: Areas needing improvement
- **Poor Performers (5%)**: Significant coaching/intervention needed

### Time Period Coverage
- **Historical Data**: 12-18 months for trend analysis
- **Current Operations**: Real-time/recent data for immediate decisions
- **Seasonal Variations**: Reflect industry seasonality patterns
- **Market Conditions**: Various economic and fuel price scenarios

### Cross-System Data Integrity
- **Consistent Timestamps**: Ensure data alignment across systems
- **Referential Integrity**: IDs must match across related datasets
- **Realistic Correlations**: Performance metrics should correlate logically
- **Exception Handling**: Include data gaps and system outages realistically

### Token Efficiency Considerations
- **Compact Field Names**: Use abbreviated but clear field names
- **Efficient Data Types**: Optimize numeric precision and string lengths
- **Strategic Sampling**: Representative data samples vs. exhaustive records
- **Hierarchical Structure**: Nested data where appropriate to reduce redundancy

---

## Dataset Naming Convention
- `dataset_[number]` for directory structure
- Consistent JSON file naming across all datasets
- Version control for dataset iterations
- Clear documentation of dataset parameters and assumptions

This skeleton ensures all demo datasets maintain consistency, realism, and agent compatibility while optimizing for demonstration effectiveness and token efficiency.