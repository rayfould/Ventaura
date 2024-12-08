// This file defines classes that model the JSON response structure returned 
// by the Google Geocoding API (or a similar geocoding service). It allows for 
// easy deserialization of the API response into .NET objects, making it simpler 
// to extract geographic coordinates from a given address or query.

// The top-level GeocodeResponse includes a list of Results and a Status field.
// Each Result contains Geometry information, which in turn includes a Location 
// with latitude and longitude values.

public class GeocodeResponse
{
    // A list of results returned by the geocoding service.
    // Each result represents a possible geographic match for the queried address.
    public List<Result> Results { get; set; }

    // The status of the geocoding request (e.g., "OK", "ZERO_RESULTS").
    public string Status { get; set; }

    // Represents a single geocoding result.
    public class Result
    {
        // The geometry of the result, which contains location coordinates.
        public Geometry Geometry { get; set; }
    }

    // Contains geometric information about the result, including location coordinates.
    public class Geometry
    {
        // The actual latitude and longitude of the matched location.
        public Location Location { get; set; }
    }

    // Holds the latitude (Lat) and longitude (Lng) coordinates of the found location.
    public class Location
    {
        // The latitude of the matched location.
        public double Lat { get; set; }

        // The longitude of the matched location.
        public double Lng { get; set; }
    }
}