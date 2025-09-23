# TMSApiTools - Development Specification

## Overview
Multi-platform Transportation Management System (TMS) integration toolset for Agent C framework, enabling unified access to load management, customer data, carrier information, and financial operations across major TMS platforms.

## Tool Class Structure
```python
class TMSApiTools(BaseToolset):
    name = "TMSApiTools"
    description = "Transportation Management System API integration for logistics operations"
    category = "logistics_integration"
    supported_platforms = ["alvys", "oracle_tm", "ascend", "mcleod", "tmw_suite", "mercurygate"]
```

## Core Functions Required

### Load Management Functions
- `get_load_details(load_id, platform)` - Complete load information
- `get_load_status(load_id, platform)` - Current load status and tracking
- `search_loads(filters, platform)` - Find loads by criteria
- `get_load_documents(load_id, platform)` - BOL, POD, rate confirmations
- `update_load_status(load_id, status, platform)` - Status updates
- `get_loads_by_date_range(start_date, end_date, platform)` - Load history

### Customer Management Functions
- `get_customer_details(customer_id, platform)` - Customer profile data
- `get_customer_loads(customer_id, date_range, platform)` - Customer load history
- `get_customer_performance_metrics(customer_id, platform)` - Service metrics
- `get_customer_payment_terms(customer_id, platform)` - Financial terms
- `search_customers(filters, platform)` - Customer search functionality

### Carrier Management Functions
- `get_carrier_details(carrier_id, platform)` - Carrier profile information
- `get_carrier_performance(carrier_id, date_range, platform)` - Performance metrics
- `get_carrier_rates(carrier_id, lane, platform)` - Rate information
- `search_available_carriers(lane, equipment_type, platform)` - Carrier availability
- `get_carrier_insurance_status(carrier_id, platform)` - Insurance verification

### Financial & Billing Functions
- `get_invoice_details(invoice_id, platform)` - Invoice information
- `generate_customer_invoice(load_id, platform)` - Invoice creation
- `get_accounts_receivable(customer_id, platform)` - AR status
- `get_carrier_payment_status(load_id, platform)` - Payment tracking
- `get_profit_analysis(load_id, platform)` - Load profitability
- `get_financial_summary(date_range, platform)` - Financial reporting

### Route & Planning Functions
- `optimize_route(stops, constraints, platform)` - Route optimization
- `get_route_details(route_id, platform)` - Route information
- `calculate_mileage(origin, destination, platform)` - Distance calculations
- `get_fuel_stops(route_id, platform)` - Fuel stop recommendations
- `validate_route_feasibility(route_params, platform)` - Route validation

## Standardized Response Format
```json
{
    "success": true,
    "platform": "alvys|oracle_tm|ascend|etc",
    "timestamp": "ISO_8601_format",
    "data_type": "load|customer|carrier|financial|route",
    "record_id": "unique_identifier",
    "data": {
        // Normalized platform data
    },
    "metadata": {
        "confidence_score": 0.98,
        "data_freshness_seconds": 60,
        "source_system": "platform_name",
        "api_version": "v2.1",
        "record_count": 1
    },
    "pagination": {
        "page": 1,
        "total_pages": 5,
        "total_records": 247
    },
    "errors": [],
    "warnings": []
}
```

## Platform-Specific Data Models

### Load Data Standard
```json
{
    "load_id": "L123456",
    "customer_id": "CUST001",
    "status": "in_transit|delivered|pending|cancelled",
    "pickup": {
        "location": "123 Main St, Chicago, IL",
        "appointment": "2024-01-15T08:00:00Z",
        "actual": "2024-01-15T08:15:00Z"
    },
    "delivery": {
        "location": "456 Oak Ave, Detroit, MI",
        "appointment": "2024-01-16T14:00:00Z",
        "actual": null
    },
    "equipment_type": "van|flatbed|reefer|tanker",
    "weight": 45000,
    "commodity": "Electronics",
    "rate": 2500.00,
    "carrier": {
        "id": "CARR001",
        "name": "ABC Trucking",
        "driver": "John Smith"
    }
}
```

### Customer Data Standard
```json
{
    "customer_id": "CUST001",
    "name": "Acme Manufacturing",
    "contact_info": {
        "primary_contact": "Jane Doe",
        "phone": "+1-555-0123",
        "email": "jane@acme.com"
    },
    "payment_terms": "NET30",
    "credit_limit": 50000.00,
    "performance_metrics": {
        "on_time_percentage": 95.5,
        "average_days_to_pay": 28,
        "total_loads_ytd": 156
    }
}
```

## Authentication & Security

### Multi-Platform Auth Management
```python
class TMSAuthManager:
    """Handles authentication across TMS platforms"""
    
    auth_methods = {
        "alvys": "oauth2",
        "oracle_tm": "basic_auth",
        "ascend": "api_key",
        "mcleod": "session_token",
        "tmw_suite": "jwt",
        "mercurygate": "oauth2"
    }
```

### Security Requirements
- **Platform-specific authentication** (OAuth2, API keys, session tokens)
- **Encrypted credential storage** with rotation support
- **Request signing** for sensitive operations
- **Audit logging** for all financial transactions
- **Role-based access control** per platform capabilities
- **Data masking** for sensitive customer/financial information

## Error Handling & Recovery

### TMS-Specific Errors
```python
class TMSApiError(Exception):
    """Base exception for TMS API errors"""

class LoadNotFoundError(TMSApiError):
    """Load ID not found in system"""

class CustomerAccessDeniedError(TMSApiError):
    """Insufficient permissions for customer data"""

class RateCalculationError(TMSApiError):
    """Route/rate calculation failed"""

class IntegrationSyncError(TMSApiError):
    """Data synchronization issues between systems"""

class BusinessRuleViolationError(TMSApiError):
    """Operation violates business rules"""
```

### Retry & Recovery Logic
- **Intelligent retry** for transient failures
- **Circuit breaker pattern** for platform outages
- **Data consistency checks** across platforms
- **Fallback to cached data** when appropriate
- **Manual intervention alerts** for critical failures

## Performance Optimization

### Caching Strategy
```python
class TMSDataCache:
    """Smart caching for TMS data based on volatility"""
    
    cache_durations = {
        "load_status": 120,        # 2 minutes
        "customer_details": 3600,  # 1 hour
        "carrier_rates": 1800,     # 30 minutes
        "route_optimization": 900, # 15 minutes
        "financial_data": 300      # 5 minutes
    }
```

### Batch Operations
- `get_multiple_load_status(load_ids, platform)` - Batch load queries
- `bulk_customer_search(criteria_list, platform)` - Multiple customer lookups
- `batch_rate_calculations(route_list, platform)` - Bulk rate calculations
- `mass_status_updates(updates_list, platform)` - Bulk status changes

## Configuration Requirements

### Environment Variables
```bash
# Alvys Configuration
ALVYS_CLIENT_ID=your_client_id
ALVYS_CLIENT_SECRET=your_client_secret
ALVYS_API_BASE_URL=https://api.alvysapp.com/v1

# Oracle TM Configuration
ORACLE_TM_USERNAME=your_username
ORACLE_TM_PASSWORD=your_password
ORACLE_TM_API_BASE_URL=https://your-instance.oraclecloud.com/tm/api

# Ascend Configuration
ASCEND_API_KEY=your_api_key
ASCEND_API_BASE_URL=https://api.ascendtms.com/v2

# Performance Settings
TMS_API_RATE_LIMIT_PER_MINUTE=200
TMS_API_TIMEOUT_SECONDS=45
TMS_BATCH_SIZE_LIMIT=100
```

### Platform Adapters Required
```python
class AlvysAdapter:
    base_url = "https://api.alvysapp.com/v1"
    auth_type = "oauth2"
    supports_webhooks = True
    max_batch_size = 50

class OracleTMAdapter:
    base_url = "https://{instance}.oraclecloud.com/tm/api"
    auth_type = "basic_auth"
    supports_webhooks = False
    max_batch_size = 25

class AscendAdapter:
    base_url = "https://api.ascendtms.com/v2"
    auth_type = "api_key"
    supports_webhooks = True
    max_batch_size = 100
```

## Data Synchronization & Consistency

### Cross-Platform Reconciliation
- **Load status synchronization** across multiple TMS platforms
- **Customer data consistency** validation
- **Rate discrepancy detection** and alerting
- **Financial data reconciliation** between systems
- **Automated conflict resolution** where possible

### Real-Time Updates
- **Webhook integration** for supported platforms
- **Polling mechanisms** for platforms without webhooks
- **Event-driven updates** for critical status changes
- **Delta synchronization** to minimize data transfer

## Agent Integration Examples

### Agent Configuration
```yaml
# Agent configuration
tools:
  - TMSApiTools

# Agent usage in persona
{{ tool_section('tms_api') }}
{{ collapsible_section('tms_advanced', 'Advanced TMS operations available') }}
```

### Sample Agent Function Calls
```python
# Load management
get_load_details(load_id="L123456", platform="alvys")
search_loads(filters={"status": "in_transit", "customer": "ACME"}, platform="oracle_tm")

# Customer operations
get_customer_performance_metrics(customer_id="CUST001", platform="ascend")
get_customer_loads(customer_id="CUST001", date_range={"start": "2024-01-01", "end": "2024-01-31"}, platform="alvys")

# Financial operations
get_profit_analysis(load_id="L123456", platform="alvys")
get_accounts_receivable(customer_id="CUST001", platform="oracle_tm")
```

## Testing Requirements

### Unit Testing
- **Mock API responses** for each TMS platform
- **Data normalization validation** across platforms
- **Error handling scenarios** for each platform
- **Authentication flow testing**
- **Rate limiting behavior validation**

### Integration Testing
- **Real API connectivity** with test environments
- **Cross-platform data consistency** verification
- **Performance benchmarking** under load
- **Failover and recovery** testing
- **Data synchronization accuracy**

### Business Logic Testing
- **Load lifecycle workflows**
- **Customer billing processes**
- **Carrier assignment logic**
- **Route optimization accuracy**
- **Financial calculation validation**

## Success Metrics
- **Response time**: <10 seconds for complex queries
- **Data accuracy**: >99.8% verified against source systems
- **Cross-platform consistency**: >98% data alignment
- **Uptime**: 99.95% availability target
- **Batch operation efficiency**: >90% successful completion rate

## Business Value Delivered
This tool enables agents to provide **unified TMS functionality** regardless of the underlying platform, allowing users to ask questions like:
- *"Show me all loads for ACME Corp this month"*
- *"What's the profit margin on load L123456?"*
- *"Find available carriers for Chicago to Detroit lane"*
- *"Generate invoice for completed load L789012"*

**Without users needing to know which TMS platform contains the data or how to navigate each system's unique interface.**