/* This file defines the models used to represent the structure of data returned by the 
Ticketmaster API in the Ventaura application. These models map the JSON response from 
the API into strongly-typed C# objects, facilitating seamless integration of event data, 
including details like event names, venues, dates, and classifications. */

namespace ventaura_backend.Models
{
    // Represents the top-level structure of the Ticketmaster API response.
    public class TicketmasterResponseModel
    {
        public EmbeddedData _embedded { get; set; } // Contains the embedded event data.
    }

    // Represents the embedded data in the API response, specifically the list of events.
    public class EmbeddedData
    {
        public List<Event> Events { get; set; } // List of events returned by the API.
    }

    // Represents an individual event.
    public class Event
    {
        public string Name { get; set; } // Name of the event.
        public string Type { get; set; } // Type of event (e.g., concert, sports).
        public string URL { get; set; } // URL for event details or ticket purchase.
        public Dates Dates { get; set; } // Event start date and time.
        public VenueEmbedded _embedded { get; set; } // Contains venue information for the event.
        public List<Classification> Classifications { get; set; } // List of event classifications.
    }

    // Represents the start date and time of an event.
    public class Dates
    {
        public Start Start { get; set; }
    }

    public class Start
    {
        public DateTime? LocalDate { get; set; }
        public string LocalTime { get; set; }     // If returned by the API
        public bool TimeTBA { get; set; }         // If returned by the API
        public bool DateTBD { get; set; }         // If returned by the API
        public bool DateTBA { get; set; }         // If returned by the API
        // Add other fields as needed based on API response
    }

    // Represents the embedded venue data for an event.
    public class VenueEmbedded
    {
        public List<Venue> Venues { get; set; } // List of venues where the event takes place.
    }

    // Represents a venue where an event is hosted.
    public class Venue
    {
        public string Name { get; set; } // Name of the venue.
        public Location Location { get; set; } // Geographic location of the venue.
    }

    // Represents the geographic location of a venue.
    public class Location
    {
        public string Latitude { get; set; } // Latitude of the venue location.
        public string Longitude { get; set; } // Longitude of the venue location.
    }

    // Represents the classification of an event, such as genre.
    public class Classification
    {
        public Genre Genre { get; set; } // Genre information for the event.
    }

    // Represents the genre of an event.
    public class Genre
    {
        public string Name { get; set; } // Name of the genre (e.g., Rock, Jazz).
    }
}
