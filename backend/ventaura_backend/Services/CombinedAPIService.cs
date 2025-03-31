/* This file defines the CombinedAPIService, a service that aggregates data from multiple APIs 
(Amadeus and Ticketmaster) in the Ventaura application. It acts as a unified interface to fetch 
and combine event and activity data based on a user's location, enabling seamless integration 
of multiple data sources for personalized recommendations. */

using ventaura_backend.Models;
using ventaura_backend.Services;
using Microsoft.EntityFrameworkCore;
using ventaura_backend.Data;
using ventaura_backend.Utils;

public class CombinedAPIService
{
    // Services for interacting with Amadeus, Yelp and Ticketmaster APIs.
    private readonly TicketmasterService _ticketmasterService;
    private readonly YelpFusionService _yelpFusionService;
    private readonly DatabaseContext _dbContext;
    private readonly GoogleGeocodingService _googleGeocodingService;

    // Constructor to inject the Amadeus and Ticketmaster services.
    public CombinedAPIService(
        TicketmasterService ticketmasterService,
        YelpFusionService yelpFusionService,
        DatabaseContext dbContext,
        GoogleGeocodingService googleGeocodingService)
    {
        _ticketmasterService = ticketmasterService;
        _yelpFusionService = yelpFusionService;
        _dbContext = dbContext;
        _googleGeocodingService = googleGeocodingService;
    }

    // Method to fetch and combine events from Amadeus and Ticketmaster APIs.
    public async Task<List<UserContent>> FetchEventsAsync(double latitude, double longitude, int userId)
    {
        // Fetch events from the Ticketmaster API.
        var ticketmasterEvents = await _ticketmasterService.FetchTicketmasterEventsAsync(latitude, longitude, userId);

        Console.WriteLine($"Fetched {ticketmasterEvents.Count} events from Ticketmaster.");

        var events = ticketmasterEvents.ToList();

        return events;
    }

    // New method to fetch and process events, returning a list of CombinedEvent
    public async Task<List<CombinedEvent>> FetchAndProcessEventsAsync(double latitude, double longitude, int userId)
    {
        // **1. Type Mapping Implementation**
        var typeMapping = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            { "festivals-fairs", "Festivals" },
            { "sports-active-life", "Outdoors" },
            { "visual-arts", "Exhibitions" },
            { "charities", "Community" },
            { "performing-arts", "Theater" },
            { "kids-family", "Family" },
            { "film", "Film" },
            { "food-and-drink", "Food and Drink" },
            { "music", "Music" },
            { "Holiday", "Holiday" },
            { "Networking", "Networking" },
            { "Gaming", "Gaming" },
            { "Pets", "Pets" },
            { "Virtual", "Virtual" },
            { "Science", "Science" },
            { "Basketball", "Basketball" },
            { "Pottery", "Pottery" },
            { "Tennis", "Tennis" },
            { "Soccer", "Soccer" },
            { "Football", "Football" },
            { "Fishing", "Fishing" },
            { "Hiking", "Hiking" },
            { "Wellness", "Wellness" },
            { "nightlife", "Nightlife" },
            { "Workshops", "Workshops" },
            { "Conferences", "Conferences" },
            { "Hockey", "Hockey" },
            { "Baseball", "Baseball" },
            { "lectures-books", "Lectures" },
            { "fashion", "Fashion" },
            { "Motorsports/Racing", "Motorsports" },
            { "Dance", "Dance" },
            { "Comedy", "Comedy" },
            { "Pop", "Music" },
            { "Country", "Music" },
            { "Hip-Hop/Rap", "Music" },
            { "Rock", "Music" },
            { "other", "Other" }
        };

        // **2. Fetch API Events**
        Console.WriteLine($"Fetching events from API for userId {userId}...");
        var apiEvents = await FetchEventsAsync(latitude, longitude, userId);

        Console.WriteLine($"Total API Events Fetched: {apiEvents.Count}");
        var yelpEventsCount = apiEvents.Count(e => e.Source.Equals("Yelp", StringComparison.OrdinalIgnoreCase));
        Console.WriteLine($"Total Yelp Events Fetched: {yelpEventsCount}");

        // **3. Fetch Host Events**
        Console.WriteLine($"Fetching host events for userId {userId}...");
        var hostEvents = await _dbContext.HostEvents.ToListAsync();

        // **4. Process API Events**
        var apiEventObjects = new List<CombinedEvent>();
        foreach (var e in apiEvents)
        {
            string location = e.Location ?? "Unknown Location";
            double eventLatitude = 0, eventLongitude = 0;

            // Use Latitude and Longitude from UserContent if available (e.g., for Ticketmaster events)
            if (e.Latitude.HasValue && e.Longitude.HasValue)
            {
                eventLatitude = e.Latitude.Value;
                eventLongitude = e.Longitude.Value;
            }
            else if (TryParseLocation(location, out eventLatitude, out eventLongitude))
            {
                // If the location is in "latitude,longitude" format, geocode to get a readable address
                location = await _googleGeocodingService.GetAddressFromCoordinates(eventLatitude, eventLongitude);
            }
            else
            {
                // If no coordinates are available, geocode the address to get coordinates for distance
                var coordinates = await _googleGeocodingService.GetCoordinatesAsync(location);
                if (coordinates.HasValue)
                {
                    eventLatitude = coordinates.Value.latitude;
                    eventLongitude = coordinates.Value.longitude;
                }
            }

            var distance = DistanceCalculator.CalculateDistance(latitude, longitude, eventLatitude, eventLongitude);

            apiEventObjects.Add(new CombinedEvent
            {
                Title = e.Title ?? "Unknown Title",
                Description = e.Description ?? "No description",
                Location = location,
                Start = e.Start,
                Source = e.Source ?? "API",
                Type = typeMapping.ContainsKey(e.Type.ToLower()) ? typeMapping[e.Type.ToLower()] : e.Type,
                CurrencyCode = e.CurrencyCode ?? "N/A",
                Amount = (decimal?)e.Amount ?? 0,
                URL = e.URL ?? "N/A",
                Distance = distance
            });
        }

        // **5. Process Host Events**
        var processedHostEvents = new List<CombinedEvent>();
        foreach (var he in hostEvents)
        {
            double eventLatitude, eventLongitude;
            if (!TryParseLocation(he.Location, out eventLatitude, out eventLongitude))
            {
                var coordinates = await _googleGeocodingService.GetCoordinatesAsync(he.Location);
                if (coordinates.HasValue)
                {
                    eventLatitude = coordinates.Value.latitude;
                    eventLongitude = coordinates.Value.longitude;
                }
                else
                {
                    eventLatitude = latitude;
                    eventLongitude = longitude;
                }
            }

            var distance = DistanceCalculator.CalculateDistance(latitude, longitude, eventLatitude, eventLongitude);

            processedHostEvents.Add(new CombinedEvent
            {
                Title = he.Title ?? "Unknown Title",
                Description = he.Description ?? "No description",
                Location = he.Location ?? "Unknown Location",
                Start = he.Start,
                Source = "Host",
                Type = typeMapping.ContainsKey(he.Type.ToLower()) ? typeMapping[he.Type.ToLower()] : he.Type,
                CurrencyCode = he.CurrencyCode ?? "N/A",
                Amount = he.Amount ?? 0,
                URL = he.URL ?? "N/A",
                Distance = distance
            });
        }

        // **6. Combine Events**
        var combinedEvents = apiEventObjects.Concat(processedHostEvents).ToList();

        Console.WriteLine($"Total Combined Events: {combinedEvents.Count}");
        var yelpCombinedCount = combinedEvents.Count(e => e.Source.Equals("Yelp", StringComparison.OrdinalIgnoreCase));
        Console.WriteLine($"Total Yelp Events in Combined: {yelpCombinedCount}");

        if (!combinedEvents.Any())
        {
            Console.WriteLine("No events to process.");
            return new List<CombinedEvent>();
        }

        // **7. Recalculate Distances for Events with Parsed Locations**
        foreach (var e in combinedEvents)
        {
            double eventLatitude, eventLongitude;
            if (TryParseLocation(e.Location, out eventLatitude, out eventLongitude))
            {
                e.Distance = DistanceCalculator.CalculateDistance(latitude, longitude, eventLatitude, eventLongitude);
            }
        }

        return combinedEvents;
    }

    // Helper method to parse location strings into latitude and longitude
    private bool TryParseLocation(string location, out double latitude, out double longitude)
    {
        latitude = 0;
        longitude = 0;
        if (string.IsNullOrEmpty(location) || !location.Contains(",")) return false;

        var parts = location.Split(',');
        return double.TryParse(parts[0].Trim(), out latitude) && double.TryParse(parts[1].Trim(), out longitude);
    }
}