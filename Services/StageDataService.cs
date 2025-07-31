using System.Collections.Concurrent;
using ConcurrentJsonUpdates.Models;
using Newtonsoft.Json;

namespace ConcurrentJsonUpdates.Services;

public class StageDataService : IStageDataService
{
    private readonly ConcurrentDictionary<string, StageData> _stageDataStore = new();
    private readonly ConcurrentDictionary<string, SemaphoreSlim> _lockMap = new();
    private readonly ILogger<StageDataService> _logger;

    public StageDataService(ILogger<StageDataService> logger)
    {
        _logger = logger;
    }

    public async Task<StageData?> GetStageDataAsync(string id)
    {
        _stageDataStore.TryGetValue(id, out var stageData);
        
        // Return a deep copy to prevent external modifications
        if (stageData != null)
        {
            var json = JsonConvert.SerializeObject(stageData);
            return JsonConvert.DeserializeObject<StageData>(json);
        }
        
        return null;
    }

    public async Task<StageData> CreateStageDataAsync(string id, string createdBy)
    {
        var newStageData = new StageData
        {
            Id = id,
            Version = 1,
            UpdatedBy = createdBy,
            LastUpdated = DateTime.UtcNow
        };

        if (!_stageDataStore.TryAdd(id, newStageData))
        {
            throw new InvalidOperationException($"Stage data with ID '{id}' already exists.");
        }

        _logger.LogInformation("Created new stage data with ID: {Id}", id);
        return await GetStageDataAsync(id) ?? newStageData;
    }

    public async Task<StageData> UpdateStageAsync(string id, string stageKey, StageInfo stageInfo, int expectedVersion, string updatedBy)
    {
        var semaphore = _lockMap.GetOrAdd(id, _ => new SemaphoreSlim(1, 1));
        
        await semaphore.WaitAsync();
        try
        {
            if (!_stageDataStore.TryGetValue(id, out var currentData))
            {
                throw new KeyNotFoundException($"Stage data with ID '{id}' not found.");
            }

            // Optimistic concurrency check
            if (currentData.Version != expectedVersion)
            {
                throw new InvalidOperationException(
                    $"Concurrency conflict: Expected version {expectedVersion}, but current version is {currentData.Version}");
            }

            // Create a deep copy for atomic update
            var json = JsonConvert.SerializeObject(currentData);
            var updatedData = JsonConvert.DeserializeObject<StageData>(json)!;

            // Update the specific stage
            stageInfo.LastModified = DateTime.UtcNow;
            updatedData.Stages[stageKey] = stageInfo;
            updatedData.Version++;
            updatedData.LastUpdated = DateTime.UtcNow;
            updatedData.UpdatedBy = updatedBy;

            // Atomic replacement
            _stageDataStore[id] = updatedData;

            _logger.LogInformation("Updated stage '{StageKey}' for ID: {Id}, Version: {Version}", 
                stageKey, id, updatedData.Version);

            return await GetStageDataAsync(id) ?? updatedData;
        }
        finally
        {
            semaphore.Release();
        }
    }

    public async Task<StageData> UpdateMultipleStagesAsync(string id, Dictionary<string, StageInfo> stages, int expectedVersion, string updatedBy)
    {
        var semaphore = _lockMap.GetOrAdd(id, _ => new SemaphoreSlim(1, 1));
        
        await semaphore.WaitAsync();
        try
        {
            if (!_stageDataStore.TryGetValue(id, out var currentData))
            {
                throw new KeyNotFoundException($"Stage data with ID '{id}' not found.");
            }

            // Optimistic concurrency check
            if (currentData.Version != expectedVersion)
            {
                throw new InvalidOperationException(
                    $"Concurrency conflict: Expected version {expectedVersion}, but current version is {currentData.Version}");
            }

            // Create a deep copy for atomic update
            var json = JsonConvert.SerializeObject(currentData);
            var updatedData = JsonConvert.DeserializeObject<StageData>(json)!;

            // Update multiple stages atomically
            var now = DateTime.UtcNow;
            foreach (var kvp in stages)
            {
                kvp.Value.LastModified = now;
                updatedData.Stages[kvp.Key] = kvp.Value;
            }

            updatedData.Version++;
            updatedData.LastUpdated = now;
            updatedData.UpdatedBy = updatedBy;

            // Atomic replacement
            _stageDataStore[id] = updatedData;

            _logger.LogInformation("Updated {Count} stages for ID: {Id}, Version: {Version}", 
                stages.Count, id, updatedData.Version);

            return await GetStageDataAsync(id) ?? updatedData;
        }
        finally
        {
            semaphore.Release();
        }
    }

    public async Task<bool> DeleteStageDataAsync(string id)
    {
        var removed = _stageDataStore.TryRemove(id, out _);
        
        if (removed)
        {
            // Clean up the semaphore
            _lockMap.TryRemove(id, out var semaphore);
            semaphore?.Dispose();
            
            _logger.LogInformation("Deleted stage data with ID: {Id}", id);
        }
        
        return removed;
    }

    public async Task<IEnumerable<StageData>> GetAllStageDataAsync()
    {
        var allData = new List<StageData>();
        
        foreach (var kvp in _stageDataStore)
        {
            // Return deep copies to prevent external modifications
            var json = JsonConvert.SerializeObject(kvp.Value);
            var copy = JsonConvert.DeserializeObject<StageData>(json);
            if (copy != null)
            {
                allData.Add(copy);
            }
        }
        
        return allData;
    }
}