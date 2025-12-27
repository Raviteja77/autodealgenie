# Infrastructure Migration Guide

## Overview

This guide helps you migrate from Kafka+MongoDB to RabbitMQ+PostgreSQL JSONB infrastructure.

## Breaking Changes

### 1. Message Broker: Kafka → RabbitMQ

**What changed:**
- Kafka and Zookeeper services have been replaced with RabbitMQ
- Message queue implementation changed from `aiokafka` to `aio-pika`
- Queue names remain the same: `deals` and `notifications`

**Migration steps:**

1. **Update environment variables:**
   - Remove: `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_CONSUMER_GROUP`, `KAFKA_TOPIC_*`
   - Add: `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`, `RABBITMQ_VHOST`

2. **Update Docker Compose:**
   ```bash
   docker-compose down
   docker volume rm autodealgenie_kafka_data autodealgenie_zookeeper_data
   docker-compose up -d
   ```

3. **No data migration needed** - Message queues are ephemeral

### 2. Document Store: MongoDB → PostgreSQL JSONB

**What changed:**
- MongoDB collections migrated to PostgreSQL tables with JSONB columns
- Three collections affected:
  - `user_preferences` → `user_preferences` table
  - `search_history` → `search_history` table
  - `ai_responses` → `ai_responses` table

**Migration steps:**

1. **Export existing MongoDB data (optional, do this FIRST if you want to preserve data):**
   
   If you have existing MongoDB data you want to preserve, export it before removing MongoDB:

   a. **Export MongoDB data:**
   ```bash
   # Export user_preferences
   docker-compose exec mongodb mongoexport \
     --db autodealgenie \
     --collection user_preferences \
     --out /tmp/user_preferences.json

   # Export search_history
   docker-compose exec mongodb mongoexport \
     --db autodealgenie \
     --collection search_history \
     --out /tmp/search_history.json

   # Export ai_responses
   docker-compose exec mongodb mongoexport \
     --db autodealgenie \
     --collection ai_responses \
     --out /tmp/ai_responses.json
   ```

   b. **Copy files from container:**
   ```bash
   docker cp autodealgenie-mongodb:/tmp/user_preferences.json ./
   docker cp autodealgenie-mongodb:/tmp/search_history.json ./
   docker cp autodealgenie-mongodb:/tmp/ai_responses.json ./
   ```

2. **Update environment variables:**
   - Remove: `MONGODB_URL`, `MONGODB_DB_NAME`

3. **Deploy new code and restart services:**
   ```bash
   git pull
   docker-compose down
   docker-compose up -d
   ```

4. **Run database migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Import MongoDB data into PostgreSQL (optional):**
   
   If you exported MongoDB data in step 1, import it now:
   ```python
   import json
   from sqlalchemy import create_engine
   from sqlalchemy.orm import Session
   from app.models.jsonb_data import UserPreference, SearchHistory, AIResponse
   
   engine = create_engine("postgresql://user:pass@localhost/autodealgenie")
   
   with Session(engine) as session:
       # Migrate user_preferences
       with open("user_preferences.json") as f:
           for line in f:
               doc = json.loads(line)
               pref = UserPreference(
                   user_id=doc["user_id"],
                   preferences=doc["preferences"],
                   created_at=doc["created_at"],
                   updated_at=doc.get("updated_at")
               )
               session.add(pref)
       
       # Similar for search_history and ai_responses...
       session.commit()
   ```

6. **Clean up MongoDB volume (optional):**
   ```bash
   docker volume rm autodealgenie_mongodb_data
   ```

## Service Changes

### RabbitMQ Management UI

RabbitMQ includes a built-in management UI:
- URL: http://localhost:15672
- Username: `autodealgenie`
- Password: `autodealgenie_password`

### Monitoring

Prometheus now scrapes RabbitMQ metrics:
- Exporter endpoint: http://localhost:9419
- Metrics are automatically available in Grafana

## Testing the Migration

1. **Verify services are healthy:**
   ```bash
   curl http://localhost:8000/health/detailed
   ```

2. **Check RabbitMQ queues:**
   - Visit http://localhost:15672
   - Navigate to Queues tab
   - Verify `deals` and `notifications` queues exist

3. **Test message publishing:**
   ```python
   # Use the RabbitMQ producer service
   from app.services.rabbitmq_producer import rabbitmq_producer
   
   await rabbitmq_producer.send_deal_event({
       "deal_id": 123,
       "action": "created"
   })
   ```

4. **Verify PostgreSQL JSONB tables:**
   ```sql
   SELECT * FROM user_preferences LIMIT 5;
   SELECT * FROM search_history LIMIT 5;
   SELECT * FROM ai_responses LIMIT 5;
   ```

## Rollback Procedure

If you need to rollback:

1. **Revert code changes:**
   ```bash
   git checkout main
   ```

2. **Restore old services:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. **Downgrade database:**
   ```bash
   docker-compose exec backend alembic downgrade -1
   ```

## Performance Notes

### RabbitMQ vs Kafka

**Advantages:**
- Simpler deployment (no Zookeeper dependency)
- Lower resource usage
- Built-in management UI
- Better for traditional message queue patterns

**Considerations:**
- Lower throughput for extremely high-volume scenarios
- Different persistence guarantees

### PostgreSQL JSONB vs MongoDB

**Advantages:**
- Single database technology to maintain
- ACID transactions across relational and JSON data
- Powerful JSONB operators and indexing
- Reduced operational complexity

**Considerations:**
- Slightly higher storage overhead for deeply nested documents
- Different query syntax (SQL vs MongoDB query language)

## Support

For issues or questions about the migration:
1. Check application logs: `docker-compose logs backend`
2. Review RabbitMQ logs: `docker-compose logs rabbitmq`
3. Open an issue on GitHub with migration-related questions
