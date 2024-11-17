/* This file defines the UserContent model, representing the structure of a temporary table used 
in the Ventaura application. The table is session-specific and dynamically created for each user 
to store personalized event data fetched from integrated APIs. It enables efficient retrieval and 
display of tailored content during user sessions. */

// Temporary table model for storing user-specific event data.
namespace ventaura_backend.Models
{
    public class UserContent
    {
        public int ContentId { get; set; } // Primary key for identifying each content entry.
        public int UserId { get; set; } // Foreign key linking the content to a specific user.
        public string Title { get; set; } // Title of the event or activity.
        public string Description { get; set; } // Detailed description of the event.
        public string Location { get; set; } // Location where the event is held.
        public DateTime? Start { get; set; } // Date and time when the event starts.
        public string Source { get; set; } // Source of the event data (e.g., "Amadeus" or "Ticketmaster").
        public string Type { get; set; } // Type of event (e.g., "Music", "Sports").
        public string CurrencyCode { get; set; } // Currency code for the event's price (e.g., "USD").
        public string Amount { get; set; } // Price amount of the event.
        public string URL { get; set; } // URL for accessing event details or making bookings.
        public float Distance { get; set; } // Distance from user's location to the event destination.
    }
}
