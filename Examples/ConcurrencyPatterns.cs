using System.Collections.Concurrent;
using ConcurrentJsonUpdates.Models;
using ConcurrentJsonUpdates.Services;

namespace ConcurrentJsonUpdates.Examples;

/// <summary>
/// Demonstrates various concurrency patterns for handling parallel JSON updates
/// </summary>
public static class ConcurrencyPatterns
{
    /// <summary>
    /// Pattern 1: Optimistic Concurrency Control with Versioning
    /// Best for: Low contention scenarios, read-heavy workloads
    /// </summary>
    public static async Task<bool> OptimisticConcurrencyExample(IStageDataService service, string id)
    {
        const int maxRetries = 3;
        
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                // 1. Read current state
                var currentData = await service.GetStageDataAsync(id);
                if (currentData == null) return false;

                // 2. Prepare update with current version
                var stageInfo = new StageInfo
                {
                    Name = "Updated Stage",
                    Status = StageStatus.InProgress,
                    Progress = 50
                };

                // 3. Attempt update with version check
                await service.UpdateStageAsync(id, "example_stage", stageInfo, currentData.Version, "OptimisticUser");
                return true; // Success
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Concurrency conflict"))
            {
                // Version mismatch - retry with exponential backoff
                await Task.Delay(TimeSpan.FromMilliseconds(Math.Pow(2, attempt) * 100));
            }
        }
        
        return false; // Failed after retries
    }

    /// <summary>
    /// Pattern 2: Pessimistic Locking (handled internally by service)
    /// Best for: High contention scenarios, write-heavy workloads
    /// </summary>
    public static async Task<List<string>> PessimisticLockingExample(IStageDataService service, string id, int concurrentUpdates = 10)
    {
        var results = new ConcurrentBag<string>();
        var tasks = new List<Task>();

        // Create multiple concurrent update tasks
        for (int i = 0; i < concurrentUpdates; i++)
        {
            var taskId = i;
            tasks.Add(Task.Run(async () =>
            {
                try
                {
                    var stageInfo = new StageInfo
                    {
                        Name = $"Concurrent Stage {taskId}",
                        Status = StageStatus.InProgress,
                        Progress = taskId * 10,
                        Data = new Dictionary<string, object> { { "taskId", taskId } }
                    };

                    // Service handles locking internally
                    var data = await service.GetStageDataAsync(id);
                    if (data != null)
                    {
                        await service.UpdateStageAsync(id, $"stage_{taskId}", stageInfo, data.Version, $"User_{taskId}");
                        results.Add($"Task {taskId}: Success");
                    }
                }
                catch (Exception ex)
                {
                    results.Add($"Task {taskId}: Failed - {ex.Message}");
                }
            }));
        }

        await Task.WhenAll(tasks);
        return results.ToList();
    }

    /// <summary>
    /// Pattern 3: Batch Updates for Multiple Stages
    /// Best for: Updating multiple related stages atomically
    /// </summary>
    public static async Task<bool> BatchUpdateExample(IStageDataService service, string id)
    {
        try
        {
            // Get current version
            var currentData = await service.GetStageDataAsync(id);
            if (currentData == null) return false;

            // Prepare batch update
            var stagesToUpdate = new Dictionary<string, StageInfo>
            {
                ["preprocessing"] = new StageInfo
                {
                    Name = "Preprocessing",
                    Status = StageStatus.Completed,
                    Progress = 100,
                    EndTime = DateTime.UtcNow
                },
                ["processing"] = new StageInfo
                {
                    Name = "Processing",
                    Status = StageStatus.InProgress,
                    Progress = 25,
                    StartTime = DateTime.UtcNow
                },
                ["postprocessing"] = new StageInfo
                {
                    Name = "Postprocessing",
                    Status = StageStatus.Pending,
                    Progress = 0
                }
            };

            // Atomic batch update
            await service.UpdateMultipleStagesAsync(id, stagesToUpdate, currentData.Version, "BatchUser");
            return true;
        }
        catch (Exception)
        {
            return false;
        }
    }

    /// <summary>
    /// Pattern 4: Producer-Consumer with Queue
    /// Best for: High-throughput scenarios with ordered processing
    /// </summary>
    public static async Task ProducerConsumerExample(IStageDataService service, string id, int messageCount = 100)
    {
        var updateQueue = new ConcurrentQueue<(string StageKey, StageInfo StageInfo, string UpdatedBy)>();
        var cancellationTokenSource = new CancellationTokenSource();

        // Producer task
        var producer = Task.Run(async () =>
        {
            for (int i = 0; i < messageCount; i++)
            {
                var stageInfo = new StageInfo
                {
                    Name = $"Queued Stage {i}",
                    Status = StageStatus.InProgress,
                    Progress = new Random().Next(0, 100),
                    Data = new Dictionary<string, object> { { "messageId", i } }
                };

                updateQueue.Enqueue(($"queued_stage_{i}", stageInfo, $"Producer_{i}"));
                await Task.Delay(10); // Simulate work
            }
        });

        // Consumer task
        var consumer = Task.Run(async () =>
        {
            while (!cancellationTokenSource.Token.IsCancellationRequested || !updateQueue.IsEmpty)
            {
                if (updateQueue.TryDequeue(out var update))
                {
                    try
                    {
                        var currentData = await service.GetStageDataAsync(id);
                        if (currentData != null)
                        {
                            await service.UpdateStageAsync(id, update.StageKey, update.StageInfo, currentData.Version, update.UpdatedBy);
                        }
                    }
                    catch (InvalidOperationException ex) when (ex.Message.Contains("Concurrency conflict"))
                    {
                        // Re-queue for retry
                        updateQueue.Enqueue(update);
                        await Task.Delay(50);
                    }
                }
                else
                {
                    await Task.Delay(10);
                }
            }
        });

        await producer;
        cancellationTokenSource.Cancel();
        await consumer;
    }

    /// <summary>
    /// Pattern 5: Event-Driven Updates with Saga Pattern
    /// Best for: Complex workflows with compensation logic
    /// </summary>
    public static async Task<bool> SagaPatternExample(IStageDataService service, string id)
    {
        var sagaSteps = new List<(string StageKey, Func<Task<bool>> Execute, Func<Task<bool>> Compensate)>
        {
            ("step1", () => ExecuteStep1(service, id), () => CompensateStep1(service, id)),
            ("step2", () => ExecuteStep2(service, id), () => CompensateStep2(service, id)),
            ("step3", () => ExecuteStep3(service, id), () => CompensateStep3(service, id))
        };

        var completedSteps = new List<int>();

        try
        {
            // Execute saga steps
            for (int i = 0; i < sagaSteps.Count; i++)
            {
                var success = await sagaSteps[i].Execute();
                if (!success)
                {
                    throw new InvalidOperationException($"Step {i + 1} failed");
                }
                completedSteps.Add(i);
            }

            return true;
        }
        catch (Exception)
        {
            // Compensate in reverse order
            for (int i = completedSteps.Count - 1; i >= 0; i--)
            {
                try
                {
                    await sagaSteps[completedSteps[i]].Compensate();
                }
                catch (Exception ex)
                {
                    // Log compensation failure but continue
                    Console.WriteLine($"Compensation failed for step {completedSteps[i] + 1}: {ex.Message}");
                }
            }

            return false;
        }
    }

    #region Saga Helper Methods
    
    private static async Task<bool> ExecuteStep1(IStageDataService service, string id)
    {
        try
        {
            var data = await service.GetStageDataAsync(id);
            if (data == null) return false;

            var stageInfo = new StageInfo
            {
                Name = "Saga Step 1",
                Status = StageStatus.Completed,
                Progress = 100,
                Data = new Dictionary<string, object> { { "sagaStep", 1 } }
            };

            await service.UpdateStageAsync(id, "saga_step1", stageInfo, data.Version, "SagaExecutor");
            return true;
        }
        catch (Exception)
        {
            return false;
        }
    }

    private static async Task<bool> ExecuteStep2(IStageDataService service, string id)
    {
        try
        {
            var data = await service.GetStageDataAsync(id);
            if (data == null) return false;

            var stageInfo = new StageInfo
            {
                Name = "Saga Step 2",
                Status = StageStatus.Completed,
                Progress = 100,
                Data = new Dictionary<string, object> { { "sagaStep", 2 } }
            };

            await service.UpdateStageAsync(id, "saga_step2", stageInfo, data.Version, "SagaExecutor");
            return true;
        }
        catch (Exception)
        {
            return false;
        }
    }

    private static async Task<bool> ExecuteStep3(IStageDataService service, string id)
    {
        // Simulate failure for demonstration
        return false;
    }

    private static async Task<bool> CompensateStep1(IStageDataService service, string id)
    {
        try
        {
            var data = await service.GetStageDataAsync(id);
            if (data == null) return false;

            var stageInfo = new StageInfo
            {
                Name = "Saga Step 1 - Compensated",
                Status = StageStatus.Cancelled,
                Progress = 0,
                Data = new Dictionary<string, object> { { "compensated", true } }
            };

            await service.UpdateStageAsync(id, "saga_step1", stageInfo, data.Version, "SagaCompensator");
            return true;
        }
        catch (Exception)
        {
            return false;
        }
    }

    private static async Task<bool> CompensateStep2(IStageDataService service, string id)
    {
        try
        {
            var data = await service.GetStageDataAsync(id);
            if (data == null) return false;

            var stageInfo = new StageInfo
            {
                Name = "Saga Step 2 - Compensated",
                Status = StageStatus.Cancelled,
                Progress = 0,
                Data = new Dictionary<string, object> { { "compensated", true } }
            };

            await service.UpdateStageAsync(id, "saga_step2", stageInfo, data.Version, "SagaCompensator");
            return true;
        }
        catch (Exception)
        {
            return false;
        }
    }

    private static async Task<bool> CompensateStep3(IStageDataService service, string id)
    {
        // Step 3 never executed, no compensation needed
        return true;
    }

    #endregion
}