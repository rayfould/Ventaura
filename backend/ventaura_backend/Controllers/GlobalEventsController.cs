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
    // Services and database context needed for fetching and processing events.
    private readonly GoogleGeocodingService _googleGeocodingService;
    private readonly CombinedAPIService _combinedApiService;
    private readonly DatabaseContext _dbContext;

    // Constructor that sets up the geocoding service, combined events service, and database context.
    public GlobalEventsController(GoogleGeocodingService googleGeocodingService, CombinedAPIService combinedApiService, DatabaseContext dbContext)
    {
        _googleGeocodingService = googleGeocodingService;
        _combinedApiService = combinedApiService;
        _dbContext = dbContext;
    }

    // GET endpoint that searches for events based on a given city and user ID.
    // It first geocodes the city to find its coordinates, then fetches events using those coordinates.
    // Each event is enriched with user-specific details and distance calculations.
    [HttpGet("search")]
    public async Task<IActionResult> SearchEvents(
        [FromQuery] string city, 
        [FromQuery] int userId, 
        [FromQuery] string eventType = null, 
        [FromQuery] double? maxDistance = null, 
        [FromQuery] double? maxPrice = null,
        [FromQuery] DateTime? startDateTime = null
    )
    {
        try
        {
            // **1. Validate User**
            var user = await _dbContext.Users.FindAsync(userId);
            if (user == null || user.Latitude == null || user.Longitude == null)
            {
                Console.WriteLine($"User with ID {userId} not found or location data is missing.");
                return BadRequest("User not found or location is missing.");
            }

            Console.WriteLine($"Location successfully extracted for userId: {userId}.");

            // **2. Geocode City**
            var coordinates = await _googleGeocodingService.GetCoordinatesAsync(city);
            if (coordinates == null) 
            {
                return NotFound(new { Message = "Could not find coordinates for the specified city." });
            }
            var latitude = coordinates.Value.latitude;
            var longitude = coordinates.Value.longitude;

            // **3. Fetch API Events**
            Console.WriteLine($"Fetching events from API for userId {userId}...");
            var apiEvents = await _combinedApiService.FetchEventsAsync(latitude, longitude, userId);

            // **4. Fetch Host Events**
            Console.WriteLine($"Fetching host events for city {city}...");
            var hostEvents = await _dbContext.HostEvents.ToListAsync();

            // **5. Process API Events**
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

                var distance = DistanceCalculator.CalculateDistance(user.Latitude.Value, user.Longitude.Value, eventLatitude, eventLongitude);

                processedApiEvents.Add(new CombinedEvent
                {
                    Title = e.Title ?? "Unknown Title",
                    Description = e.Description ?? "No description",
                    Location = location,
                    Start = e.Start,
                    Source = e.Source ?? "API",
                    Type = e.Type ?? "Other",
                    CurrencyCode = e.CurrencyCode ?? "N/A",
                    Amount = e.Amount.HasValue ? (decimal)e.Amount.Value : 0,
                    URL = e.URL ?? "N/A",
                    Distance = distance
                });
            }

            // **6. Process Host Events**
            var processedHostEvents = new List<CombinedEvent>();

            var hostEventTasks = hostEvents.Select(async he =>
            {
                var hostCity = await ExtractCityFromLocation(he.Location);
                if (!string.Equals(hostCity, city, StringComparison.OrdinalIgnoreCase))
                {
                    // Skip host events that do not match the input city
                    return null;
                }

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

                var distance = DistanceCalculator.CalculateDistance(user.Latitude.Value, user.Longitude.Value, hostLatitude, hostLongitude);

                return new CombinedEvent
                {
                    Title = he.Title ?? "Unknown Title",
                    Description = he.Description ?? "No description",
                    Location = he.Location ?? "Unknown Location",
                    Start = he.Start,
                    Source = "Host",
                    Type = he.Type ?? "Other",
                    CurrencyCode = he.CurrencyCode ?? "N/A",
                    Amount = he.Amount ?? 0,
                    URL = he.URL ?? "N/A",
                    Distance = distance
                };
            });

            processedHostEvents = (await Task.WhenAll(hostEventTasks)).Where(e => e != null).ToList();


            // **7. Combine Events**
            var combinedEvents = processedApiEvents.Concat(processedHostEvents).ToList();

            // **8. Apply Filters**
            if (!string.IsNullOrEmpty(eventType))
            {
                combinedEvents = combinedEvents
                    .Where(e => e.Type.Equals(eventType, StringComparison.OrdinalIgnoreCase))
                    .ToList();
            }

            if (maxDistance.HasValue)
            {
                combinedEvents = combinedEvents
                    .Where(e => e.Distance >= 0 && e.Distance <= maxDistance.Value)
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

            // **9. Return Combined Events**
            Console.WriteLine($"✅ Total combined events: {combinedEvents.Count}");
            return Ok(new { Message = "Events fetched successfully.", Events = combinedEvents });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in SearchEvents: {ex.Message}");
            return StatusCode(500, "An error occurred while fetching events.");
        }
    }

    private async Task<string> ExtractCityFromLocation(string location)
    {
        if (string.IsNullOrEmpty(location))
            return string.Empty;

        try
        {
            var coordinates = await _googleGeocodingService.GetCoordinatesAsync(location);
            if (!coordinates.HasValue)
                return string.Empty;

            var address = await _googleGeocodingService.GetAddressFromCoordinates(coordinates.Value.latitude, coordinates.Value.longitude);
            var addressParts = address.Split(',');
            if (addressParts.Length >= 2)
            {
                return addressParts[addressParts.Length - 3].Trim(); // Assuming city is the second-to-last part
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error extracting city: {ex.Message}");
        }

        return string.Empty;
    }

    // Function to clean the CSV formatting so it works as expected in the ranking algorithm
    private string CleanField(string field)
    {
        if (string.IsNullOrEmpty(field)) return "";
        field = field.Replace("\r", " ").Replace("\n", " ").Trim();
        if (field.Contains(",") || field.Contains("\""))
            return $"\"{field.Replace("\"", "\"\"")}\"";
        return field;
    }

    // Parse location to calculate distance
    private bool TryParseLocation(string location, out double latitude, out double longitude)
    {
        latitude = 0;
        longitude = 0;
        if (string.IsNullOrEmpty(location) || !location.Contains(",")) return false;

        var parts = location.Split(',');
        return double.TryParse(parts[0].Trim(), out latitude) && double.TryParse(parts[1].Trim(), out longitude);
    }
}
