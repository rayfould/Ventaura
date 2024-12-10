using Microsoft.AspNetCore.Mvc;
using ventaura_backend.Services;
using ventaura_backend.Data;
using ventaura_backend.Models;
using ventaura_backend.Utils; // Import DistanceCalculator
using Microsoft.EntityFrameworkCore;

[ApiController]
[Route("api/global-events")]
public class GlobalEventsController : ControllerBase
{
    private readonly GoogleGeocodingService _googleGeocodingService;
    private readonly CombinedAPIService _combinedApiService;
    private readonly DatabaseContext _dbContext;

    public GlobalEventsController(GoogleGeocodingService googleGeocodingService, CombinedAPIService combinedApiService, DatabaseContext dbContext)
    {
        _googleGeocodingService = googleGeocodingService;
        _combinedApiService = combinedApiService;
        _dbContext = dbContext;
    }

    [HttpGet("search")]
    public async Task<IActionResult> SearchEvents(
        [FromQuery] string city, 
        [FromQuery] int userId, 
        [FromQuery] string eventType = null,
        [FromQuery] double? maxDistance = 100, // Default to 100 km
        [FromQuery] double? maxPrice = null,
        [FromQuery] DateTime? startDateTime = null
    )
    {
        try
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
                { "Hockey", "Hockey"},
                { "Baseball", "Baseball"},
                { "lectures-books", "Lectures"},
                { "fashion", "Fashion"},
                { "Motorsports/Racing", "Motorsports"},
                { "Dance", "Dance"},
                { "Comedy", "Comedy"},
                { "Pop", "Music"},
                { "Country", "Music"},
                { "Hip-Hop/Rap", "Music"},
                { "Rock", "Music"},
                { "other", "Other" }
            };

            var user = await _dbContext.Users.FindAsync(userId);
            if (user == null || user.Latitude == null || user.Longitude == null)
            {
                return BadRequest("User not found or location is missing.");
            }

            var coordinates = await _googleGeocodingService.GetCoordinatesAsync(city);
            if (coordinates == null) 
            {
                return NotFound(new { Message = "Could not find coordinates for the specified city." });
            }

            var searchLatitude = coordinates.Value.latitude;
            var searchLongitude = coordinates.Value.longitude;

            // **3. Fetch Events**
            var apiEvents = await _combinedApiService.FetchEventsAsync(searchLatitude, searchLongitude, userId);
            var hostEvents = await _dbContext.HostEvents.ToListAsync();

            var processedApiEvents = new List<CombinedEvent>();

            foreach (var e in apiEvents)
            {
                var location = e.Location ?? "Unknown Location";
                double eventLatitude = 0, eventLongitude = 0;

                if (TryParseLocation(location, out eventLatitude, out eventLongitude))
                {
                    location = await _googleGeocodingService.GetAddressFromCoordinates(eventLatitude, eventLongitude);
                }
                else
                {
                    var geoCoordinates = await _googleGeocodingService.GetCoordinatesAsync(location);
                    if (geoCoordinates.HasValue)
                    {
                        eventLatitude = geoCoordinates.Value.latitude;
                        eventLongitude = geoCoordinates.Value.longitude;
                    }
                }

                var distance = DistanceCalculator.CalculateDistance(searchLatitude, searchLongitude, eventLatitude, eventLongitude);

                // If distance is over 100km, don't include it
                if (distance > (maxDistance ?? 100))
                {
                    continue; // Skip events beyond maxDistance
                }

                processedApiEvents.Add(new CombinedEvent
                {
                    Title = e.Title ?? "Unknown Title",
                    Description = e.Description ?? "No description",
                    Location = location,
                    Start = e.Start,
                    Source = e.Source ?? "API",
                    Type = typeMapping.ContainsKey(e.Type?.ToLower()) ? typeMapping[e.Type.ToLower()] : e.Type,
                    CurrencyCode = e.CurrencyCode ?? "N/A",
                    Amount = e.Amount.HasValue ? (decimal)e.Amount.Value : 0,
                    URL = e.URL ?? "N/A",
                    Distance = distance
                });
            }

            var processedHostEvents = new List<CombinedEvent>();

            foreach (var he in hostEvents)
            {
                double hostLatitude = 0, hostLongitude = 0;

                if (!TryParseLocation(he.Location, out hostLatitude, out hostLongitude))
                {
                    var geoCoordinates = await _googleGeocodingService.GetCoordinatesAsync(he.Location);
                    if (geoCoordinates.HasValue)
                    {
                        hostLatitude = geoCoordinates.Value.latitude;
                        hostLongitude = geoCoordinates.Value.longitude;
                    }
                }

                var distance = DistanceCalculator.CalculateDistance(searchLatitude, searchLongitude, hostLatitude, hostLongitude);

                // If distance is over 100km, don't include it
                if (distance > (maxDistance ?? 100))
                {
                    continue; // Skip events beyond maxDistance
                }
                
                processedHostEvents.Add(new CombinedEvent
                {
                    Title = he.Title ?? "Unknown Title",
                    Description = he.Description ?? "No description",
                    Location = he.Location ?? "Unknown Location",
                    Start = he.Start,
                    Source = "Host",
                    Type = typeMapping.ContainsKey(he.Type?.ToLower()) ? typeMapping[he.Type.ToLower()] : he.Type,
                    CurrencyCode = he.CurrencyCode ?? "N/A",
                    Amount = he.Amount ?? 0,
                    URL = he.URL ?? "N/A",
                    Distance = distance
                });
            }

            var combinedEvents = processedApiEvents.Concat(processedHostEvents).ToList();

            if (!string.IsNullOrEmpty(eventType))
            {
                combinedEvents = combinedEvents
                    .Where(e => e.Type.Equals(eventType, StringComparison.OrdinalIgnoreCase))
                    .ToList();
            }

            if (maxPrice.HasValue)
            {
                combinedEvents = combinedEvents
                    .Where(e => e.Amount.HasValue && e.Amount.Value <= (decimal)maxPrice.Value)
                    .ToList();
            }

            if (startDateTime.HasValue)
            {
                combinedEvents = combinedEvents
                    .Where(e => e.Start.HasValue && e.Start.Value >= startDateTime.Value)
                    .ToList();
            }

            return Ok(new { Message = "Events fetched successfully.", Events = combinedEvents });
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while fetching events: {ex.Message}");
        }
    }

    private bool TryParseLocation(string location, out double latitude, out double longitude)
    {
        latitude = 0;
        longitude = 0;
        if (string.IsNullOrEmpty(location) || !location.Contains(",")) return false;

        var parts = location.Split(',');
        return double.TryParse(parts[0].Trim(), out latitude) && double.TryParse(parts[1].Trim(), out longitude);
    }
}