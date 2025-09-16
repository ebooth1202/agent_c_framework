# ELDApiTools - Development Specification

## Overview
Comprehensive ELD platform integration toolset for Agent C framework, enabling seamless access to vehicle tracking, driver HOS monitoring, and fleet management data across multiple ELD platforms.

## Tool Class Structure
```python
class ELDApiTools(BaseToolset):
    name = "ELDApiTools"
    description = "Electronic Logging Device API integration for fleet management"
    category = "logistics_integration"
    supported_platforms = ["motive", "samsara", "omnitracs", "keeptruckin"]
```

## Core Functions Required

### Vehicle Data Functions
- `get_vehicle_location(vehicle_id, platform)` - Real-time GPS coordinates
- `get_vehicle_health_status(vehicle_id, platform)` - Diagnostic data
- `calculate_eta(vehicle_id, destination, platform)` - ETA calculations
- `get_route_distance(origin, destination, platform)` - Distance calculations

### Driver & Compliance Functions
- `get_driver_hos_status(driver_id, platform)` - Hours of Service tracking
- `get_hos_violations(platform, date_range)` - Compliance violations
- `get_safety_events(vehicle_id, platform, date_range)` - Safety incidents
- `get_dvir_reports(vehicle_id, platform, date_range)` - Inspection reports

### Fleet Management Functions
- `get_fleet_overview(platform, filters)` - Fleet-wide status
- `get_fuel_efficiency_data(vehicle_id, platform, date_range)` - MPG metrics
- `get_driver_performance_metrics(driver_id, platform, date_range)` - Performance data

## Standardized Response Format
```json
{
    "success": true,
    "platform": "motive|samsara|etc",
    "timestamp": "ISO_8601_format",
    "data_type": "location|health|hos|eta|distance",
    "vehicle_id": "fleet_identifier",
    "data": {
        // Normalized platform data
    },
    "metadata": {
        "confidence_score": 0.95,
        "data_freshness_seconds": 30,
        "source_system": "platform_name"
    },
    "errors": [],
    "warnings": []
}
```

## Authentication & Security
- **OAuth2/API Key management** per platform
- **Secure credential storage** (encrypted)
- **Token refresh automation**
- **Request signing** where required
- **Role-based access control**

## Error Handling
- `AuthenticationError` - Auth failures
- `RateLimitError` - API limits exceeded  
- `DataNotFoundError` - Missing data
- `PlatformUnavailableError` - Service outages
- **Automatic retry logic** with exponential backoff

## Performance Features
- **Smart caching** (30s for location, 5min for health, 1hr for fuel)
- **Batch operations** for multiple vehicles/drivers
- **Rate limit management**
- **Connection pooling**

## Configuration Requirements
```bash
# Environment Variables
MOTIVE_CLIENT_ID=your_client_id
MOTIVE_CLIENT_SECRET=your_client_secret
SAMSARA_API_TOKEN=your_api_token
ELD_API_RATE_LIMIT_PER_MINUTE=100
ELD_API_TIMEOUT_SECONDS=30
```

## Platform Adapters Needed
- **MotiveAdapter** - OAuth2, REST API
- **SamsaraAdapter** - API Key, GraphQL support
- **OmnitracsAdapter** - Custom auth, XML responses
- **KeepTruckinAdapter** - JWT tokens, JSON API

## Testing Requirements
- **Unit tests** with mocked API responses
- **Integration tests** with real API connectivity
- **Error scenario testing**
- **Performance benchmarking**
- **Cross-platform data validation**

## Agent Integration
```yaml
# Agent configuration
tools:
  - ELDApiTools

# Agent usage
{{ tool_section('eld_api') }}
```

## Success Metrics
- **Response time**: <5 seconds for standard queries
- **Data accuracy**: >99.5% verified against source
- **Uptime**: 99.9% availability target
- **Cache hit rate**: >80% for repeated queries

This tool enables the Transpo_Logistics_World agents to access real ELD data seamlessly across multiple platforms with consistent interfaces and robust error handling.