// Models/RankingResponse.cs
namespace ventaura_backend.Models
{
    public class RankingResponse
    {
        public bool Success { get; set; }
        public string Message { get; set; }
        public int EventsProcessed { get; set; }
        public int EventsRemoved { get; set; }
    }
}
