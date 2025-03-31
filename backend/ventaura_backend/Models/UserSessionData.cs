namespace ventaura_backend.Models
{
    public class UserSessionData
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public string RankedCSV { get; set; }
        public DateTime CreatedAt { get; set; }

        // Foreign key relationship
        public User User { get; set; }
    }
}