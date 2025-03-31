/* This file defines the UserContent model, representing the structure of the UserContent table in the 
Ventaura application's database. It stores content related to events or activities that are linked to a user. */

namespace ventaura_backend.Models
{
    public class UserContent
    {
        public int Id { get; set; } // Maps to "id" column
        public int? UserId { get; set; } // Maps to "user_id" column (nullable foreign key)
        public string Title { get; set; } // Maps to "title" column
        public string Description { get; set; } // Maps to "description" column (nullable)
        public string Location { get; set; } // Maps to "location" column (nullable)
        public double? Latitude { get; set; } // Maps to "Latitude" column (nullable)
        public double? Longitude { get; set; } // Maps to "Longitude" column (nullable)
        public DateTime? Start { get; set; } // Maps to "start" column (nullable)
        public string Source { get; set; } // Maps to "source" column (nullable)
        public string Type { get; set; } // Maps to "type" column (nullable)
        public string CurrencyCode { get; set; } // Maps to "currency_code" column (nullable)
        public decimal? Amount { get; set; } // Maps to "amount" column (nullable)
        public string URL { get; set; } // Maps to "url" column (nullable)
        public DateTime CreatedAt { get; set; } = DateTime.Now; // Maps to "created_at" column with default value
        public double? Distance { get; set; } // Maps to "distance" column (nullable)
    }
}

