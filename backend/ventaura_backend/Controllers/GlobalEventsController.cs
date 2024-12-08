// This file defines a controller responsible for handling the global events search functionality.
// Given a city name and a user ID, it uses a geocoding service to obtain coordinates for the city,
// then fetches events from various APIs via a combined service. It enriches these events by assigning
// unique IDs, associating them with the given user, and calculating their distance from the user's 
// stored location. The result is then returned to the client as a JSON response.

using Microsoft.AspNetCore.Mvc;
using ventaura_backend.Services;
using ventaura_backend.Data;
using ventaura_backend.Utils; // Import DistanceCalculator

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
    public async Task<IActionResult> SearchEvents([FromQuery] string city, 
        [FromQuery] int userId, 
        [FromQuery] string eventType = null, 
        [FromQuery] double? maxDistance = null, 
        [FromQuery] decimal? maxPrice = null
    )
    {
        // Validate that a city name is provided.
        if (string.IsNullOrWhiteSpace(city))
        {
            return BadRequest(new { Message = "City name is required." });
        }

        // Verify that the user exists in the database.
        var user = await _dbContext.Users.FindAsync(userId);
        if (user == null)
        {
            return Unauthorized(new { Message = "User is not authorized or does not exist." });
        }

        try
        {
            // Use the Google Geocoding Service to get coordinates for the specified city.
            var coordinates = await _googleGeocodingService.GetCoordinatesAsync(city);
            if (coordinates == null)
            {
                return NotFound(new { Message = "Could not find coordinates for the specified city." });
            }

            var latitude = coordinates.Value.latitude;
            var longitude = coordinates.Value.longitude;

            // Fetch events near the given coordinates using the combined API service.
            var events = await _combinedApiService.FetchEventsAsync(latitude, longitude, userId);

            // Assign user-related info and unique IDs to the fetched events.
            // Also attempt to calculate each event's distance from the user's location.
            for (int i = 0; i < events.Count; i++)
            {
                events[i].UserId = userId;
                events[i].Id = i + 1; // Assign a unique ContentId based on the loop index.

                // Parse the event's location and calculate the distance if possible.
                var eventCoordinates = events[i].Location?.Split(',');
                if (eventCoordinates != null && eventCoordinates.Length == 2 &&
                    double.TryParse(eventCoordinates[0], out var eventLatitude) &&
                    double.TryParse(eventCoordinates[1], out var eventLongitude))
                {
                    // Calculate distance using the user's lat/long from the database and the event's coordinates.
                    events[i].Distance = (float)DistanceCalculator.CalculateDistance(
                        user.Latitude ?? 0, user.Longitude ?? 0, eventLatitude, eventLongitude);
                }
                else
                {
                    // If the location isn't parseable, assign a default distance value.
                    events[i].Distance = 0;
                }
            }

            // **Filter by Event Type**
            if (!string.IsNullOrEmpty(eventType))
            {
                events = events.Where(e => e.Type != null && e.Type.Equals(eventType, StringComparison.OrdinalIgnoreCase)).ToList();
            }

            // **Filter by Max Distance**
            if (maxDistance.HasValue)
            {
                events = events.Where(e => e.Distance >= 0 && e.Distance <= maxDistance).ToList();
            }

            // **Filter by Max Price**
            if (maxPrice.HasValue)
            {
                events = events.Where(e => e.Amount != null && e.Amount <= maxPrice).ToList();
            }

            Console.WriteLine($"✅ Events for {city} successfully fetched and filtered for user {userId}.");

            // Return the processed events with a success message.
            return Ok(new { Message = "Events fetched successfully.", events });
        }
        catch (Exception ex)
        {
            // Log unexpected errors and return a 500 response.
            Console.WriteLine($"Error fetching events for city {city}: {ex.Message}");
            return StatusCode(500, new { Message = "An error occurred while fetching events." });
        }
    }
}