#!/bin/bash
# Monitoring Stack Validation Script
# Tests that all monitoring components are working correctly

echo "========================================"
echo "AutoDealGenie Monitoring Stack Validator"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Helper functions
check_service() {
    local name=$1
    local url=$2
    echo -n "Testing $name... "
    
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Error: Cannot reach $url"
        ((FAILED++))
        return 1
    fi
}

check_prometheus_target() {
    local job=$1
    echo -n "Checking Prometheus target: $job... "
    
    local health=$(curl -s "http://localhost:9090/api/v1/targets" | \
                   jq -r ".data.activeTargets[] | select(.labels.job==\"$job\") | .health" 2>/dev/null)
    
    if [ "$health" == "up" ]; then
        echo -e "${GREEN}✓ UP${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ DOWN${NC}"
        echo "  Status: $health"
        ((FAILED++))
        return 1
    fi
}

check_metric_exists() {
    local metric=$1
    echo -n "Checking metric: $metric... "
    
    if curl -s "http://localhost:8000/metrics" | grep -q "$metric"; then
        echo -e "${GREEN}✓ EXISTS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ NOT FOUND${NC}"
        ((FAILED++))
        return 1
    fi
}

echo "1. Testing Service Availability"
echo "================================"
check_service "Backend" "http://localhost:8000/health"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3001/api/health"
check_service "Alertmanager" "http://localhost:9094/-/healthy"
check_service "Postgres Exporter" "http://localhost:9187/metrics"
check_service "Redis Exporter" "http://localhost:9121/metrics"
echo ""

echo "2. Testing Prometheus Targets"
echo "=============================="
check_prometheus_target "autodealgenie-backend"
check_prometheus_target "postgres"
check_prometheus_target "redis"
check_prometheus_target "prometheus"
echo ""

echo "3. Testing Metrics Endpoint"
echo "============================"
check_metric_exists "http_requests_total"
check_metric_exists "http_request_duration_seconds"
check_metric_exists "autodealgenie_app_info"
echo ""

echo "4. Testing Alert Rules"
echo "======================"
echo -n "Checking alert rules loaded... "
ALERT_COUNT=$(curl -s "http://localhost:9090/api/v1/rules" | jq '.data.groups[].rules | length' | awk '{s+=$1} END {print s}')

if [ "$ALERT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ PASS${NC} ($ALERT_COUNT rules loaded)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (No alert rules found)"
    ((FAILED++))
fi
echo ""

echo "5. Testing Grafana Datasource"
echo "=============================="
echo -n "Checking Prometheus datasource... "
DATASOURCE=$(curl -s -u admin:admin "http://localhost:3001/api/datasources" | jq -r '.[].type' 2>/dev/null)

if [ "$DATASOURCE" == "prometheus" ]; then
    echo -e "${GREEN}✓ CONFIGURED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ NOT CONFIGURED${NC}"
    ((FAILED++))
fi
echo ""

echo "6. Testing Grafana Dashboards"
echo "=============================="
echo -n "Checking dashboards loaded... "
DASHBOARD_COUNT=$(curl -s -u admin:admin "http://localhost:3001/api/search?type=dash-db" | jq '. | length' 2>/dev/null)

if [ "$DASHBOARD_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ PASS${NC} ($DASHBOARD_COUNT dashboards found)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARNING${NC} (No dashboards found, may need manual import)"
fi
echo ""

echo "7. Testing Metric Collection"
echo "============================="
echo -n "Generating test traffic... "
for i in {1..10}; do
    curl -s http://localhost:8000/health > /dev/null 2>&1
done
echo -e "${GREEN}✓ DONE${NC}"

echo -n "Waiting for Prometheus to scrape (15s)... "
sleep 15
echo -e "${GREEN}✓ DONE${NC}"

echo -n "Verifying metric increment... "
REQUESTS=$(curl -s "http://localhost:8000/metrics" | grep 'http_requests_total' | grep 'health' | awk '{print $2}' | head -1)

if [ -n "$REQUESTS" ] && [ "$REQUESTS" -gt 0 ]; then
    echo -e "${GREEN}✓ PASS${NC} (Recorded $REQUESTS requests)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (No requests recorded)"
    ((FAILED++))
fi
echo ""

echo "========================================"
echo "SUMMARY"
echo "========================================"
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Monitoring stack is working correctly.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Access Grafana at http://localhost:3001 (admin/admin)"
    echo "  2. View dashboards in the AutoDealGenie folder"
    echo "  3. Check Prometheus at http://localhost:9090"
    echo "  4. Review alerts at http://localhost:9094"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please check the errors above.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Ensure all services are running: docker-compose ps"
    echo "  2. Check logs: docker-compose logs"
    echo "  3. Verify network connectivity between containers"
    echo "  4. See monitoring/README.md for more help"
    exit 1
fi
