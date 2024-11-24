using Microsoft.AspNetCore.Mvc;
using ventaura_backend.Services;
using ventaura_backend.Data;
using ventaura_backend.Utils; // Import DistanceCalculator

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
    public async Task<IActionResult> SearchEvents([FromQuery] string city, [FromQuery] int userId)
    {
        if (string.IsNullOrWhiteSpace(city))
        {
            return BadRequest(new { Message = "City name is required." });
        }

        var user = await _dbContext.Users.FindAsync(userId);
        if (user == null)
        {
            return Unauthorized(new { Message = "User is not authorized or does not exist." });
        }

        try
        {
            // Get coordinates for the city using Google Geocoding API
            var coordinates = await _googleGeocodingService.GetCoordinatesAsync(city);
            if (coordinates == null)
            {
                return NotFound(new { Message = "Could not find coordinates for the specified city." });
            }

            var latitude = coordinates.Value.latitude; 
            var longitude = coordinates.Value.longitude;

            // Fetch events using CombinedAPIService
            var events = await _combinedApiService.FetchEventsAsync(latitude, longitude, userId);

            // Populate the `UserId` and unique `ContentId` fields
            for (int i = 0; i < events.Count; i++)
            {
                events[i].UserId = userId;
                events[i].Id = i + 1; // Assign unique ContentId

                // Parse event location into latitude and longitude
                var eventCoordinates = events[i].Location?.Split(',');
                if (eventCoordinates != null && eventCoordinates.Length == 2 &&
                    double.TryParse(eventCoordinates[0], out var eventLatitude) &&
                    double.TryParse(eventCoordinates[1], out var eventLongitude))
                {
                    // Calculate the distance from user's location to the event
                    events[i].Distance = (float)DistanceCalculator.CalculateDistance(
                        user.Latitude ?? 0, user.Longitude ?? 0, eventLatitude, eventLongitude);

                }
                else 
                {
                    events[i].Distance = -1; // Assign a default or error value for distance if parsing fails
                }
            }

            Console.WriteLine($"Events for {city} successfully fetched and returned for user {userId}.");
            return Ok(new { Message = "Events fetched successfully.", events });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error fetching events for city {city}: {ex.Message}");
            return StatusCode(500, new { Message = "An error occurred while fetching events." });
        }
    }
}
