# Dataset 1 Access Information
# For Agent Integration and Testing

## Data File Locations
All raw data files are located at: `//logistics_project/demo/dataset_1/`

## Available Data Files:
- `vehicles.json` - Fleet vehicle registry and specifications
- `drivers.json` - Driver information and performance tiers
- `trailers.json` - Trailer inventory and current assignments
- `customers.json` - Customer contracts and relationship data
- `loads.json` - Active and recent load assignments
- `fuel_transactions.json` - Recent fuel purchase records
- `gps_tracking.json` - Real-time vehicle positioning
- `hos_logs.json` - Hours of Service compliance status
- `maintenance_history.json` - Vehicle service and repair records

## Data Integration Notes:
- All IDs are consistent across files for cross-reference
- Performance spectrum implemented (top performers to poor performers)
- Real-time timestamps for operational scenarios
- Token-optimized structure for efficient processing

## Sample Queries Ready for Testing:
1. Driver location: "Where is driver Martinez?"
2. Fuel efficiency: "Who has the worst fuel efficiency?"
3. HOS compliance: "Any drivers approaching HOS limits?"
4. Maintenance: "Show me vehicles needing maintenance"
5. Report generation: "Generate an Excel report of load performance"