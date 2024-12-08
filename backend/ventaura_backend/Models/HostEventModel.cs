// This model defines a HostEvent entity, which represents events created and managed by a host user within the Ventaura application.
// HostEvents are stored in the database and can be combined with external events to provide a unified event list for users.
// The model includes details such as the event’s title, description, location, pricing information, and a reference to the host who created it.

namespace ventaura_backend.Models
{
    public class HostEvent
    {
        // The unique identifier for the event in the database.
        public int EventId { get; set; }

        // The title or name of the host event.
        public string Title { get; set; }

        // A description providing details about the event’s content or purpose.
        public string Description { get; set; }

        // The event location. This could be a physical address or coordinates.
        public string Location { get; set; }

        // The scheduled start date and time of the event (if applicable).
        public DateTime? Start { get; set; }

        // Indicates the origin of the event data. For host events, typically "Host".
        public string Source { get; set; }

        // The category or type of the event (e.g., "Concert", "Workshop", "Meetup").
        public string Type { get; set; }

        // The currency code (e.g., "USD", "EUR") associated with any ticket price or cost.
        public string CurrencyCode { get; set; }

        // The price amount for attending the event, if applicable.
        public decimal? Amount { get; set; }

        // A URL providing additional information or a way to RSVP/purchase tickets.
        public string URL { get; set; }

        // The date and time when the event was created and stored in the database.
        public DateTime CreatedAt { get; set; }

        // The ID of the host user who created this event.
        public int HostUserId { get; set; }
    }
}