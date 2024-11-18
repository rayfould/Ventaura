using Microsoft.AspNetCore.Mvc;
using ventaura_backend.Services;

[ApiController]
[Route("api/global-events")]
public class GlobalEventsController : ControllerBase
{
    private readonly GoogleGeocodingService _googleGeocodingService;
    private readonly CombinedAPIService _combinedApiService;

    public GlobalEventsController(GoogleGeocodingService googleGeocodingService, CombinedAPIService combinedApiService)
    {
        _googleGeocodingService = googleGeocodingService;
        _combinedApiService = combinedApiService;
    }

    [HttpGet("search")]
    public async Task<IActionResult> SearchEvents([FromQuery] string city)
    {
        if (string.IsNullOrWhiteSpace(city))
        {
            return BadRequest(new { Message = "City name is required." });
        }

        try
        {
            // Get coordinates for the city using Google Geocoding API
            var coordinates = await _googleGeocodingService.GetCoordinatesAsync(city);
            if (coordinates == null)
            {
                return NotFound(new { Message = "Could not find coordinates for the specified city." });
            }

            // Explicitly handle the nullable tuple
            var latitude = coordinates.Value.latitude;
            var longitude = coordinates.Value.longitude;

            // Fetch events using CombinedAPIService
            var events = await _combinedApiService.FetchEventsAsync(latitude, longitude, userId: 0); // Pass a dummy userId

            return Ok(new { Message = "Events fetched successfully.", events });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error fetching events for city {city}: {ex.Message}");
            return StatusCode(500, new { Message = "An error occurred while fetching events." });
        }
    }
}
