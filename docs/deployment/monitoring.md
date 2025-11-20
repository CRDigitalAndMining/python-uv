# Monitoring and Logging

Configure application monitoring, logging, and observability for production environments using Azure Monitor and Application Insights.

## Overview

This project uses **Azure Monitor** with **Application Insights** for production observability. The `tools.logger` module automatically sends structured logs when `IS_LOCAL=false`.

## Azure Application Insights Setup

### Create Application Insights Resource

```bash
# Variables
RESOURCE_GROUP=myapp-rg
LOCATION=eastus
APP_INSIGHTS_NAME=myapp-insights

# Create Application Insights
az monitor app-insights component create \
  --app $APP_INSIGHTS_NAME \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web

# Get connection string
CONNECTION_STRING=$(az monitor app-insights component show \
  --app $APP_INSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --query connectionString \
  --output tsv)

echo "Connection String: $CONNECTION_STRING"

# Get instrumentation key (legacy)
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app $APP_INSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey \
  --output tsv)

echo "Instrumentation Key: $INSTRUMENTATION_KEY"
```

### Configure Application

Set the connection string as an environment variable:

```bash
# For Container Apps
az containerapp update \
  --name myapp \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    AZURE_MONITOR_CONNECTION_STRING="$CONNECTION_STRING"

# For Docker
docker run -e AZURE_MONITOR_CONNECTION_STRING="$CONNECTION_STRING" myapp:latest

# In .env (production)
AZURE_MONITOR_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/
IS_LOCAL=false
```

## Logging with tools.logger

The Logger module automatically handles production logging:

```python
from tools.config import Settings
from tools.logger import Logger, LogType

settings = Settings()
logger = Logger(
    __name__,
    log_type=LogType.LOCAL if settings.IS_LOCAL else LogType.AZURE_MONITOR,
    connection_string=settings.get("AZURE_MONITOR_CONNECTION_STRING") if not settings.IS_LOCAL else None
)

# All logs automatically go to Application Insights in production
logger.info("Application started")
logger.warning("High memory usage detected")
logger.error("Database connection failed")
```

### Structured Logging

The `AzureMonitorFormatter` sends structured JSON logs:

```python
# Logs include:
# - timestamp (ISO 8601)
# - level (INFO, WARNING, ERROR, etc.)
# - message
# - module name
# - function name
# - line number
# - stack traces (for exceptions)

logger.info("User login", extra={
    "user_id": user_id,
    "ip_address": request.client.host,
    "user_agent": request.headers.get("user-agent")
})
```

## Performance Monitoring with Timer

Track function execution times:

```python
from tools.tracer import Timer

@Timer("database_query")
def get_users():
    # Timer automatically logs execution time to Application Insights
    return db.query(User).all()

# Or as context manager
with Timer("api_request"):
    response = requests.get(external_api_url)
```

## Viewing Logs in Azure Portal

### 1. Navigate to Application Insights

1. Go to [Azure Portal](https://portal.azure.com)
2. Find your Application Insights resource
3. Navigate to "Logs" under Monitoring

### 2. Query Logs with KQL

```kusto
// View all logs from last hour
traces
| where timestamp > ago(1h)
| project timestamp, message, severityLevel
| order by timestamp desc

// Filter by log level
traces
| where severityLevel >= 2  // Warning and above
| order by timestamp desc

// Search for specific text
traces
| where message contains "database"
| project timestamp, message, severityLevel

// Group by severity
traces
| summarize count() by severityLevel
| render piechart

// Track Timer execution times
traces
| where message contains "executed in"
| extend duration_ms = extract(@"executed in ([\d\.]+) ms", 1, message)
| project timestamp, duration_ms
| render timechart
```

### 3. View Exceptions

```kusto
exceptions
| where timestamp > ago(24h)
| project timestamp, type, outerMessage, details
| order by timestamp desc
```

### 4. Performance Metrics

```kusto
// Request duration
requests
| where timestamp > ago(1h)
| summarize avg(duration), percentile(duration, 95) by name
| render barchart

// Failed requests
requests
| where success == false
| summarize count() by resultCode
| render piechart
```

## Application Insights Features

### 1. Live Metrics

View real-time telemetry:
- Incoming request rate
- Failed request rate
- Server response time
- Server CPU usage
- Server memory usage

Access: Application Insights → Live Metrics

### 2. Availability Tests

Monitor endpoint availability:

```bash
# Create availability test
az monitor app-insights web-test create \
  --resource-group $RESOURCE_GROUP \
  --name "$APP_INSIGHTS_NAME-health-check" \
  --location $LOCATION \
  --kind ping \
  --web-test "<WebTest>...</WebTest>" \
  --frequency 300 \
  --timeout 30 \
  --enabled true
```

### 3. Alerts

Create alerts for critical conditions:

```bash
# Alert on high error rate
az monitor metrics alert create \
  --name "High Error Rate" \
  --resource-group $RESOURCE_GROUP \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/components/$APP_INSIGHTS_NAME \
  --condition "count requests/failed > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email me@example.com
```

### 4. Application Map

Visualize dependencies and performance:

Access: Application Insights → Application Map

Shows:
- Component relationships
- Average duration
- Failure rates
- External dependencies

### 5. Performance Profiling

Identify performance bottlenecks:

Access: Application Insights → Performance → Profiler

## Custom Metrics

Track application-specific metrics:

```bash
uv add azure-monitor-opentelemetry-exporter
```

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

# Setup metrics
exporter = AzureMonitorMetricExporter(connection_string=connection_string)
meter_provider = MeterProvider(metric_readers=[exporter])
metrics.set_meter_provider(meter_provider)

meter = metrics.get_meter(__name__)

# Create custom metrics
request_counter = meter.create_counter(
    "app.requests",
    description="Number of requests"
)

response_time = meter.create_histogram(
    "app.response_time",
    description="Response time in ms"
)

# Record metrics
request_counter.add(1, {"endpoint": "/api/users"})
response_time.record(123.45, {"endpoint": "/api/users"})
```

## Log Retention

Configure data retention:

```bash
# Set retention to 90 days
az monitor app-insights component update \
  --app $APP_INSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --retention-time 90
```

Default retention: 90 days
Maximum retention: 730 days (2 years)

## Best Practices

### 1. Use Appropriate Log Levels

```python
logger.debug("Detailed diagnostic info")  # Development only
logger.info("Normal application flow")     # General events
logger.warning("Unexpected but handled")   # Potential issues
logger.error("Error occurred")            # Errors that were handled
logger.critical("System unusable")        # Critical failures
```

### 2. Add Context to Logs

```python
# ✅ Good - includes context
logger.info(f"User {user_id} updated profile", extra={
    "user_id": user_id,
    "fields_updated": ["email", "name"],
    "ip_address": ip
})

# ❌ Less useful
logger.info("Profile updated")
```

### 3. Don't Log Sensitive Data

```python
# ❌ Never log passwords, tokens, or PII
logger.info(f"User logged in with password: {password}")

# ✅ Safe logging
logger.info(f"User {user_id} logged in successfully")
```

### 4. Use Sampling for High-Volume Apps

```python
# Configure sampling in Azure Monitor
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    connection_string=connection_string,
    sampling_ratio=0.1  # Sample 10% of telemetry
)
```

### 5. Monitor Key Metrics

Essential metrics to track:
- Response time (p50, p95, p99)
- Error rate
- Request throughput
- CPU and memory usage
- Dependency call duration
- Exception rate

## Alerting Strategy

### Critical Alerts (Immediate Action)

- Application completely down
- Error rate > 50%
- All requests failing
- Out of memory

```bash
az monitor metrics alert create \
  --name "Critical: App Down" \
  --resource-group $RESOURCE_GROUP \
  --scopes $RESOURCE_ID \
  --condition "count requests/failed > 100" \
  --window-size 5m \
  --severity 0
```

### Warning Alerts (Investigation Needed)

- Response time > 2s (p95)
- Error rate > 5%
- High CPU usage (>80%)
- High memory usage (>85%)

### Info Alerts (Nice to Know)

- Response time increasing
- New exceptions appearing
- Unusual traffic patterns

## Troubleshooting

### Logs Not Appearing

1. **Check connection string**:
   ```bash
   # Verify format
   echo $AZURE_MONITOR_CONNECTION_STRING
   # Should include both InstrumentationKey and IngestionEndpoint
   ```

2. **Verify IS_LOCAL is false**:
   ```python
   from tools.config import Settings
   settings = Settings()
   print(f"IS_LOCAL: {settings.IS_LOCAL}")  # Should be False
   ```

3. **Wait 2-5 minutes**: Initial telemetry takes time to appear

4. **Check network connectivity**: Ensure app can reach Azure

### High Telemetry Costs

1. **Enable sampling**: Reduce data volume
2. **Adjust log levels**: Use INFO/WARNING in production, not DEBUG
3. **Filter noisy logs**: Exclude health check endpoints
4. **Set appropriate retention**: Don't keep logs longer than needed

## Monitoring Checklist

- [ ] Application Insights created
- [ ] Connection string configured
- [ ] Logging enabled (IS_LOCAL=false)
- [ ] Log levels appropriate for production
- [ ] Sensitive data not logged
- [ ] Alerts configured for critical metrics
- [ ] Application Map reviewed
- [ ] Performance baselines established
- [ ] Retention policy configured
- [ ] Cost budget set

## Next Steps

- [Azure Deployment](azure.md) - Deploy with monitoring enabled
- [Logger Guide](../guides/tools/logger.md) - Detailed logging documentation
- [Tracer Guide](../guides/tools/tracer.md) - Performance monitoring

## Resources

- [Application Insights Documentation](https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [KQL Query Language](https://docs.microsoft.com/azure/data-explorer/kusto/query/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Azure Monitor Pricing](https://azure.microsoft.com/pricing/details/monitor/)
