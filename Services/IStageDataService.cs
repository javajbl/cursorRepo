using ConcurrentJsonUpdates.Models;

namespace ConcurrentJsonUpdates.Services;

public interface IStageDataService
{
    Task<StageData?> GetStageDataAsync(string id);
    Task<StageData> CreateStageDataAsync(string id, string createdBy);
    Task<StageData> UpdateStageAsync(string id, string stageKey, StageInfo stageInfo, int expectedVersion, string updatedBy);
    Task<StageData> UpdateMultipleStagesAsync(string id, Dictionary<string, StageInfo> stages, int expectedVersion, string updatedBy);
    Task<bool> DeleteStageDataAsync(string id);
    Task<IEnumerable<StageData>> GetAllStageDataAsync();
}