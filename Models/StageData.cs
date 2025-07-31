using Newtonsoft.Json;

namespace ConcurrentJsonUpdates.Models;

public class StageData
{
    [JsonProperty("id")]
    public string Id { get; set; } = string.Empty;

    [JsonProperty("version")]
    public int Version { get; set; } = 1;

    [JsonProperty("stages")]
    public Dictionary<string, StageInfo> Stages { get; set; } = new();

    [JsonProperty("lastUpdated")]
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;

    [JsonProperty("updatedBy")]
    public string UpdatedBy { get; set; } = string.Empty;
}

public class StageInfo
{
    [JsonProperty("name")]
    public string Name { get; set; } = string.Empty;

    [JsonProperty("status")]
    public StageStatus Status { get; set; } = StageStatus.Pending;

    [JsonProperty("progress")]
    public int Progress { get; set; } = 0;

    [JsonProperty("data")]
    public Dictionary<string, object> Data { get; set; } = new();

    [JsonProperty("startTime")]
    public DateTime? StartTime { get; set; }

    [JsonProperty("endTime")]
    public DateTime? EndTime { get; set; }

    [JsonProperty("lastModified")]
    public DateTime LastModified { get; set; } = DateTime.UtcNow;
}

public enum StageStatus
{
    Pending = 0,
    InProgress = 1,
    Completed = 2,
    Failed = 3,
    Cancelled = 4
}

public class StageUpdateRequest
{
    public string StageKey { get; set; } = string.Empty;
    public StageInfo StageInfo { get; set; } = new();
    public int ExpectedVersion { get; set; }
    public string UpdatedBy { get; set; } = string.Empty;
}