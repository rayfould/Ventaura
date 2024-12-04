

namespace ventaura_backend.Models
{
    public class HostEvent
    {
        public int EventId { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string Location { get; set; }
        public DateTime? Start { get; set; }
        public string Source { get; set; }
        public string Type { get; set; }
        public string CurrencyCode { get; set; }
        public decimal? Amount { get; set; }
        public string URL { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public int HostUserId { get; set; }
    }
}