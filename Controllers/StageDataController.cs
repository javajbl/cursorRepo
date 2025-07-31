using Microsoft.AspNetCore.Mvc;
using ConcurrentJsonUpdates.Models;
using ConcurrentJsonUpdates.Services;

namespace ConcurrentJsonUpdates.Controllers;

[ApiController]
[Route("api/[controller]")]
public class StageDataController : ControllerBase
{
    private readonly IStageDataService _stageDataService;
    private readonly ILogger<StageDataController> _logger;

    public StageDataController(IStageDataService stageDataService, ILogger<StageDataController> logger)
    {
        _stageDataService = stageDataService;
        _logger = logger;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<StageData>>> GetAll()
    {
        try
        {
            var allData = await _stageDataService.GetAllStageDataAsync();
            return Ok(allData);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving all stage data");
            return StatusCode(500, "Internal server error");
        }
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<StageData>> Get(string id)
    {
        try
        {
            var stageData = await _stageDataService.GetStageDataAsync(id);
            if (stageData == null)
            {
                return NotFound($"Stage data with ID '{id}' not found");
            }
            return Ok(stageData);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving stage data for ID: {Id}", id);
            return StatusCode(500, "Internal server error");
        }
    }

    [HttpPost("{id}")]
    public async Task<ActionResult<StageData>> Create(string id, [FromBody] CreateStageDataRequest request)
    {
        try
        {
            var stageData = await _stageDataService.CreateStageDataAsync(id, request.CreatedBy);
            return CreatedAtAction(nameof(Get), new { id }, stageData);
        }
        catch (InvalidOperationException ex)
        {
            return Conflict(ex.Message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating stage data for ID: {Id}", id);
            return StatusCode(500, "Internal server error");
        }
    }

    [HttpPut("{id}/stages/{stageKey}")]
    public async Task<ActionResult<StageData>> UpdateStage(
        string id, 
        string stageKey, 
        [FromBody] StageUpdateRequest request)
    {
        try
        {
            var updatedData = await _stageDataService.UpdateStageAsync(
                id, stageKey, request.StageInfo, request.ExpectedVersion, request.UpdatedBy);
            
            return Ok(updatedData);
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(ex.Message);
        }
        catch (InvalidOperationException ex) when (ex.Message.Contains("Concurrency conflict"))
        {
            return Conflict(new { 
                error = "Concurrency conflict", 
                message = ex.Message,
                suggestion = "Please refresh the data and try again with the current version"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating stage '{StageKey}' for ID: {Id}", stageKey, id);
            return StatusCode(500, "Internal server error");
        }
    }

    [HttpPut("{id}/stages")]
    public async Task<ActionResult<StageData>> UpdateMultipleStages(
        string id, 
        [FromBody] MultipleStageUpdateRequest request)
    {
        try
        {
            var updatedData = await _stageDataService.UpdateMultipleStagesAsync(
                id, request.Stages, request.ExpectedVersion, request.UpdatedBy);
            
            return Ok(updatedData);
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(ex.Message);
        }
        catch (InvalidOperationException ex) when (ex.Message.Contains("Concurrency conflict"))
        {
            return Conflict(new { 
                error = "Concurrency conflict", 
                message = ex.Message,
                suggestion = "Please refresh the data and try again with the current version"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating multiple stages for ID: {Id}", id);
            return StatusCode(500, "Internal server error");
        }
    }

    [HttpDelete("{id}")]
    public async Task<ActionResult> Delete(string id)
    {
        try
        {
            var deleted = await _stageDataService.DeleteStageDataAsync(id);
            if (!deleted)
            {
                return NotFound($"Stage data with ID '{id}' not found");
            }
            return NoContent();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting stage data for ID: {Id}", id);
            return StatusCode(500, "Internal server error");
        }
    }

    // Endpoint to simulate concurrent updates for testing
    [HttpPost("{id}/simulate-concurrent-updates")]
    public async Task<ActionResult> SimulateConcurrentUpdates(string id, [FromBody] ConcurrentUpdateSimulationRequest request)
    {
        try
        {
            var tasks = new List<Task<(bool Success, string Message)>>();

            // Create concurrent update tasks
            for (int i = 0; i < request.ConcurrentCallsCount; i++)
            {
                var stageKey = $"stage_{i}";
                var updateRequest = new StageUpdateRequest
                {
                    StageKey = stageKey,
                    StageInfo = new StageInfo
                    {
                        Name = $"Concurrent Stage {i}",
                        Status = StageStatus.InProgress,
                        Progress = new Random().Next(0, 100),
                        Data = new Dictionary<string, object> { { "taskId", i } }
                    },
                    ExpectedVersion = request.ExpectedVersion,
                    UpdatedBy = $"User_{i}"
                };

                tasks.Add(UpdateStageWithRetry(id, stageKey, updateRequest, request.MaxRetries));
            }

            var results = await Task.WhenAll(tasks);
            
            var successCount = results.Count(r => r.Success);
            var failureCount = results.Length - successCount;

            return Ok(new
            {
                TotalCalls = request.ConcurrentCallsCount,
                SuccessfulUpdates = successCount,
                FailedUpdates = failureCount,
                Results = results.Select((r, i) => new { TaskId = i, r.Success, r.Message })
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during concurrent update simulation for ID: {Id}", id);
            return StatusCode(500, "Internal server error");
        }
    }

    private async Task<(bool Success, string Message)> UpdateStageWithRetry(
        string id, string stageKey, StageUpdateRequest request, int maxRetries)
    {
        for (int attempt = 0; attempt <= maxRetries; attempt++)
        {
            try
            {
                // Get current version before update
                var currentData = await _stageDataService.GetStageDataAsync(id);
                if (currentData == null)
                {
                    return (false, "Stage data not found");
                }

                request.ExpectedVersion = currentData.Version;
                
                await _stageDataService.UpdateStageAsync(
                    id, stageKey, request.StageInfo, request.ExpectedVersion, request.UpdatedBy);
                
                return (true, $"Updated successfully on attempt {attempt + 1}");
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Concurrency conflict"))
            {
                if (attempt == maxRetries)
                {
                    return (false, $"Failed after {maxRetries + 1} attempts due to concurrency conflicts");
                }
                
                // Small delay before retry
                await Task.Delay(new Random().Next(10, 100));
            }
            catch (Exception ex)
            {
                return (false, $"Error: {ex.Message}");
            }
        }

        return (false, "Unexpected failure");
    }
}

public class CreateStageDataRequest
{
    public string CreatedBy { get; set; } = string.Empty;
}

public class MultipleStageUpdateRequest
{
    public Dictionary<string, StageInfo> Stages { get; set; } = new();
    public int ExpectedVersion { get; set; }
    public string UpdatedBy { get; set; } = string.Empty;
}

public class ConcurrentUpdateSimulationRequest
{
    public int ConcurrentCallsCount { get; set; } = 10;
    public int ExpectedVersion { get; set; } = 1;
    public int MaxRetries { get; set; } = 3;
}