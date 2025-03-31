namespace ventaura_backend.Models
{
    public class UserSessionData
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public string RankedCSV { get; set; }
        public DateTime UpdatedAt { get; set; }
        public bool IsRanked {get; set; }

        // Foreign key relationship
        public User User { get; set; }
    }
}