// This file defines classes that model the JSON response structure returned 
// by the Google Geocoding API (or a similar geocoding service). It allows for 
// easy deserialization of the API response into .NET objects, making it simpler 
// to extract geographic coordinates from a given address or query.

// The top-level GeocodeResponse includes a list of Results and a Status field.
// Each Result contains Geometry information, which in turn includes a Location 
// with latitude and longitude values.

using System.Text.Json.Serialization;
public class GeocodeResponse
{
    // A list of results returned by the geocoding service.
    // Each result represents a possible geographic match for the queried address.
    [JsonPropertyName("results")]
    public List<Result> Results { get; set; }

    // The status of the geocoding request (e.g., "OK", "ZERO_RESULTS").
    [JsonPropertyName("status")]
    public string Status { get; set; }

    // Represents a single geocoding result.
    public class Result
    {
        [JsonPropertyName("formatted_address")]
        public string FormattedAddress { get; set; }

        [JsonPropertyName("geometry")]
        public Geometry Geometry { get; set; }

        [JsonPropertyName("place_id")]
        public string PlaceId { get; set; }

        [JsonPropertyName("types")]
        public List<string> Types { get; set; }

        [JsonPropertyName("address_components")]
        public List<AddressComponent> AddressComponents { get; set; }
    }

    // Contains geometric information about the result, including location coordinates.
    public class Geometry
    {
        [JsonPropertyName("location")]
        public Location Location { get; set; }

        [JsonPropertyName("location_type")]
        public string LocationType { get; set; }

        [JsonPropertyName("viewport")]
        public Viewport Viewport { get; set; }
    }

    // Holds the latitude (Lat) and longitude (Lng) coordinates of the found location.
    public class Location
    {
        [JsonPropertyName("lat")]
        public double Lat { get; set; }

        [JsonPropertyName("lng")]
        public double Lng { get; set; }
    }

    public class Viewport
    {
        [JsonPropertyName("northeast")]
        public Location Northeast { get; set; }

        [JsonPropertyName("southwest")]
        public Location Southwest { get; set; }
    }

    public class AddressComponent
    {
        [JsonPropertyName("long_name")]
        public string LongName { get; set; }

        [JsonPropertyName("short_name")]
        public string ShortName { get; set; }

        [JsonPropertyName("types")]
        public List<string> Types { get; set; }
    }
}