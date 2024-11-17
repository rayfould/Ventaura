/* This file defines the models used to represent the structure of data returned by 
the Amadeus API in the Ventaura application. These models map the JSON response from 
the API into strongly-typed C# objects, enabling easy handling and integration of 
activities and event data into the application. */

namespace ventaura_backend.Models
{
    // Represents the top-level structure of the Amadeus API response.
    public class AmadeusResponseModel
    {
        public List<Activity> Data { get; set; } // List of activities returned by the API.
    }

    // Represents an individual activity or event.
    public class Activity
    {
        public string Name { get; set; } // Name of the activity or event.
        public string ShortDescription { get; set; } // Brief description of the activity or event.
        public GeoCode GeoCode { get; set; } // Geographic coordinates of the activity's location.
        public Price Price { get; set; } // Pricing information for the activity.
        public string BookingLink { get; set; } // URL for booking or accessing more details.
        public List<string> Pictures { get; set; } // List of URLs for activity images.
    }

    // Represents the geographic coordinates of an activity or event.
    public class GeoCode
    {
        public string Latitude { get; set; } // Latitude of the location.
        public string Longitude { get; set; } // Longitude of the location.
    }

    // Represents the pricing details of an activity or event.
    public class Price
    {
        public string CurrencyCode { get; set; } // Currency code (e.g., USD, EUR).
        public string Amount { get; set; } // Price amount in the specified currency.
    }
}
