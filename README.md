# Concurrent JSON Updates in .NET Core

This project demonstrates how to handle parallel API calls that update the same JSON string containing multiple stages in .NET Core. It provides multiple concurrency control patterns to prevent data corruption and race conditions.

## Problem Statement

When multiple API calls attempt to update the same JSON document simultaneously, several issues can occur:
- **Race Conditions**: Updates may overwrite each other
- **Data Corruption**: Partial updates may leave the JSON in an inconsistent state
- **Lost Updates**: Changes may be lost when concurrent operations conflict

## Solutions Implemented

### 1. Optimistic Concurrency Control with Versioning
- **Best for**: Low contention scenarios, read-heavy workloads
- **How it works**: Each JSON document has a version number that increments with each update
- **Benefits**: High performance for low-contention scenarios
- **Trade-offs**: May require retries in high-contention scenarios

### 2. Pessimistic Locking with SemaphoreSlim
- **Best for**: High contention scenarios, write-heavy workloads
- **How it works**: Uses per-document locks to serialize access
- **Benefits**: Guarantees consistency, no lost updates
- **Trade-offs**: Lower throughput due to serialization

### 3. Atomic Batch Updates
- **Best for**: Updating multiple related stages atomically
- **How it works**: Groups multiple stage updates into a single atomic operation
- **Benefits**: Ensures consistency across related updates
- **Trade-offs**: May increase lock contention

### 4. Producer-Consumer Pattern
- **Best for**: High-throughput scenarios with ordered processing
- **How it works**: Queues updates and processes them sequentially
- **Benefits**: High throughput, ordered processing
- **Trade-offs**: Eventual consistency, more complex architecture

### 5. Saga Pattern for Complex Workflows
- **Best for**: Complex workflows with compensation logic
- **How it works**: Breaks complex operations into steps with compensation actions
- **Benefits**: Handles complex failure scenarios gracefully
- **Trade-offs**: More complex implementation

## Key Features

### Thread-Safe Operations
- Uses `ConcurrentDictionary` for thread-safe storage
- Per-document `SemaphoreSlim` for fine-grained locking
- Deep copying to prevent external modifications

### Optimistic Concurrency Control
- Version-based conflict detection
- Automatic retry mechanisms with exponential backoff
- Clear error messages for version conflicts

### Comprehensive Error Handling
- Proper HTTP status codes (409 for conflicts, 404 for not found)
- Detailed error messages with suggestions
- Graceful degradation on failures

### Production-Ready Features
- Structured logging
- Dependency injection
- Swagger documentation
- Comprehensive unit test examples

## API Endpoints

### Basic Operations
```
GET    /api/stagedata           - Get all stage data
GET    /api/stagedata/{id}      - Get specific stage data
POST   /api/stagedata/{id}      - Create new stage data
DELETE /api/stagedata/{id}      - Delete stage data
```

### Update Operations
```
PUT    /api/stagedata/{id}/stages/{stageKey}  - Update single stage
PUT    /api/stagedata/{id}/stages             - Update multiple stages
```

### Testing
```
POST   /api/stagedata/{id}/simulate-concurrent-updates - Simulate concurrent updates
```

## Usage Examples

### Creating Stage Data
```bash
curl -X POST "https://localhost:7000/api/stagedata/workflow-123" \
  -H "Content-Type: application/json" \
  -d '{"createdBy": "user1"}'
```

### Updating a Single Stage
```bash
curl -X PUT "https://localhost:7000/api/stagedata/workflow-123/stages/preprocessing" \
  -H "Content-Type: application/json" \
  -d '{
    "stageInfo": {
      "name": "Preprocessing",
      "status": 2,
      "progress": 100,
      "data": {"processed": true}
    },
    "expectedVersion": 1,
    "updatedBy": "user1"
  }'
```

### Batch Update Multiple Stages
```bash
curl -X PUT "https://localhost:7000/api/stagedata/workflow-123/stages" \
  -H "Content-Type: application/json" \
  -d '{
    "stages": {
      "preprocessing": {
        "name": "Preprocessing",
        "status": 2,
        "progress": 100
      },
      "processing": {
        "name": "Processing", 
        "status": 1,
        "progress": 25
      }
    },
    "expectedVersion": 2,
    "updatedBy": "user1"
  }'
```

### Simulating Concurrent Updates
```bash
curl -X POST "https://localhost:7000/api/stagedata/workflow-123/simulate-concurrent-updates" \
  -H "Content-Type: application/json" \
  -d '{
    "concurrentCallsCount": 10,
    "expectedVersion": 1,
    "maxRetries": 3
  }'
```

## Running the Application

1. **Prerequisites**: .NET 8.0 SDK

2. **Build and Run**:
   ```bash
   dotnet build
   dotnet run
   ```

3. **Access Swagger UI**: Navigate to `https://localhost:7000/swagger`

## Best Practices Demonstrated

### 1. Version-Based Optimistic Concurrency
```csharp
// Always check version before updating
if (currentData.Version != expectedVersion)
{
    throw new InvalidOperationException("Concurrency conflict");
}
```

### 2. Retry Logic with Exponential Backoff
```csharp
for (int attempt = 0; attempt < maxRetries; attempt++)
{
    try
    {
        // Attempt update
        return await UpdateAsync();
    }
    catch (ConcurrencyException)
    {
        await Task.Delay(TimeSpan.FromMilliseconds(Math.Pow(2, attempt) * 100));
    }
}
```

### 3. Deep Copying for Immutability
```csharp
// Create deep copy to prevent external modifications
var json = JsonConvert.SerializeObject(currentData);
var updatedData = JsonConvert.DeserializeObject<StageData>(json);
```

### 4. Per-Resource Locking
```csharp
// Use separate locks for different resources
var semaphore = _lockMap.GetOrAdd(id, _ => new SemaphoreSlim(1, 1));
```

## Performance Considerations

### Memory Usage
- Deep copying increases memory usage but ensures thread safety
- Consider using memory pools for high-frequency operations
- Monitor garbage collection in high-throughput scenarios

### Throughput
- Optimistic concurrency provides better throughput for low-contention scenarios
- Pessimistic locking serializes access but guarantees consistency
- Batch updates reduce the number of lock acquisitions

### Scalability
- Per-document locking allows better scalability than global locks
- Consider using distributed locks (Redis, etc.) for multi-instance deployments
- Monitor lock contention and adjust strategies accordingly

## Testing Concurrent Updates

The project includes a built-in endpoint to simulate concurrent updates:

```csharp
[HttpPost("{id}/simulate-concurrent-updates")]
```

This endpoint:
- Creates multiple concurrent update tasks
- Implements retry logic with exponential backoff
- Reports success/failure statistics
- Demonstrates real-world concurrency handling

## Alternative Approaches

### Database-Based Solutions
- Use database transactions for ACID guarantees
- Implement row-level locking with SELECT FOR UPDATE
- Consider event sourcing for audit trails

### Message Queue Solutions
- Use message queues (RabbitMQ, Azure Service Bus) for ordered processing
- Implement event-driven architectures
- Consider CQRS pattern for read/write separation

### Distributed Lock Solutions
- Use Redis for distributed locking
- Implement leader election patterns
- Consider consensus algorithms (Raft, PBFT)

## Monitoring and Observability

### Logging
- Structured logging with correlation IDs
- Performance metrics for lock contention
- Error rates and retry statistics

### Metrics
- Update success/failure rates
- Lock acquisition times
- Retry attempt distributions
- Version conflict frequencies

This solution provides a comprehensive approach to handling concurrent JSON updates in .NET Core, with multiple patterns suitable for different scenarios and requirements.
