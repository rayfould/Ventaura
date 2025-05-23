/* Retrieves and stores user-specific content in memory, automatically cleared on logout. 
This file implements the CombinedEventsController for the Ventaura application, enabling 
user-specific content management through session-based database tables. It handles fetching 
events from integrated APIs (Amadeus and Ticketmaster), dynamically creating and 
populating temporary tables for user sessions, and ensuring cleanup upon logout. This approach 
optimizes resource usage, ensures privacy, and provides a seamless experience for users accessing 
personalized event recommendations. */

using Microsoft.AspNetCore.Mvc;
using ventaura_backend.Data;
using Microsoft.EntityFrameworkCore;
using ventaura_backend.Utils;
using ventaura_backend.Models;
using ventaura_backend.Services;
using System.IO;
using System.Text;

namespace ventaura_backend.Controllers
{
        
    // Marks this class as an API controller and sets the route prefix for all endpoints.
    [ApiController]
    [Route("api/combined-events")]
    public class CombinedEventsController : ControllerBase
    {
        // Service for fetching events from combined APIs and the database context for accessing the database.
        private readonly CombinedAPIService _combinedApiService;
        private readonly DatabaseContext _dbContext;
        private readonly GoogleGeocodingService _googleGeocodingService;

        // Constructor to inject dependencies for the API service and database context.
        public CombinedEventsController(CombinedAPIService combinedApiService, DatabaseContext dbContext, GoogleGeocodingService googleGeocodingService)
        {
            _combinedApiService = combinedApiService;
            _dbContext = dbContext;
            _googleGeocodingService = googleGeocodingService;
        }

        // Endpoint to fetch and store user-specific event data in a temporary table.
        [HttpGet("fetch")]
        public async Task<IActionResult> FetchCombinedEvents([FromQuery] int userId)
        {
            try
            {
                // **1. Get User**
                var user = await _dbContext.Users.FindAsync(userId);
                if (user == null || user.Latitude == null || user.Longitude == null)
                {
                    Console.WriteLine($"User with ID {userId} not found or location data is missing.");
                    return BadRequest("User not found or location is missing.");
                }

                Console.WriteLine($"Location successfully extracted for userId: {userId}.");

                // **2. Fetch and Process Events**
                var combinedEvents = await _combinedApiService.FetchAndProcessEventsAsync(user.Latitude.Value, user.Longitude.Value, userId);

                if (!combinedEvents.Any())
                {
                    Console.WriteLine("No events to process.");
                    return Ok(new { Message = "No events available to process.", TotalEvents = 0 });
                }

                // **3. Write CSV to Memory Stream**
                var memoryStream = new MemoryStream();
                using (var writer = new StreamWriter(memoryStream, new UTF8Encoding(false), leaveOpen: true))
                {
                    await writer.WriteAsync("contentId,title,description,location,start,source,type,currencyCode,amount,url,distance\n");

                    int contentIdCounter = 1;
                    int eventsWritten = 0;
                    foreach (var e in combinedEvents)
                    {
                        Console.WriteLine($"Writing Event to CSV - Title: {e.Title}, Source: {e.Source}, Start: {e.Start}");
                        await writer.WriteLineAsync(
                            $"{contentIdCounter}," +
                            $"{CleanField(e.Title)}," +
                            $"{CleanField(e.Description)}," +
                            $"{CleanField(e.Location)}," +
                            $"{CleanField(e.Start.HasValue ? e.Start.Value.ToString("yyyy-MM-dd HH:mm:ss") : "")}," +
                            $"{CleanField(e.Source)}," +
                            $"{CleanField(e.Type)}," +
                            $"{CleanField(e.CurrencyCode)}," +
                            $"{CleanField(e.Amount?.ToString())}," +
                            $"{CleanField(e.URL)}," +
                            $"{e.Distance}"
                        );
                        contentIdCounter++;
                        eventsWritten++;
                    }
                    Console.WriteLine($"Total Events Written to CSV: {eventsWritten}");
                }

                // **4. Save Unranked CSV to Supabase**
                memoryStream.Position = 0;
                using (var reader = new StreamReader(memoryStream))
                {
                    var csvContent = await reader.ReadToEndAsync();

                    // Delete any existing row for this user to avoid duplicates
                    var existingData = await _dbContext.UserSessionData
                        .Where(usd => usd.UserId == userId)
                        .FirstOrDefaultAsync();
                    if (existingData != null)
                    {
                        _dbContext.UserSessionData.Remove(existingData);
                    }

                    // Insert the new unranked CSV
                    var userSessionData = new UserSessionData
                    {
                        UserId = userId,
                        RankedCSV = csvContent,
                        IsRanked = false
                    };
                    await _dbContext.UserSessionData.AddAsync(userSessionData);
                    await _dbContext.SaveChangesAsync();

                    Console.WriteLine($"Saved unranked CSV to UserSessionData for user {userId}.");
                }

                return Ok(new { Message = "Events processed successfully and saved to database." });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in FetchCombinedEvents: {ex.Message}");
                return StatusCode(500, "An error occurred while fetching events.");
            }
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

        // New endpoint to test fetching from UserSessionData
        [HttpGet("test-user-session-data")]
        public async Task<IActionResult> TestUserSessionData([FromQuery] int userId)
        {
            try
            {
                var userSessionData = await _dbContext.UserSessionData
                    .Where(usd => usd.UserId == userId)
                    .FirstOrDefaultAsync();

                if (userSessionData == null)
                {
                    return NotFound(new { Message = $"No UserSessionData found for user {userId}." });
                }

                return Ok(new
                {
                    Message = "UserSessionData found.",
                    Data = new
                    {
                        userSessionData.Id,
                        userSessionData.UserId,
                        userSessionData.RankedCSV,
                        userSessionData.UpdatedAt
                    }
                });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in TestUserSessionData: {ex.Message}");
                return StatusCode(500, new { Message = "An error occurred while fetching UserSessionData.", Details = ex.Message });
            }
        }


        // Endpoint that fetches the ranked csv from the database   
        [HttpGet("get-ranked-csv")]
        public async Task<IActionResult> GetRankedCsv([FromQuery] int userId)
        {
            try
            {
                // Update LastActivity for the user
                var user = await _dbContext.Users.FindAsync(userId);
                if (user != null)
                {
                    user.LastActivity = DateTime.UtcNow;
                    await _dbContext.SaveChangesAsync();
                }
                // Fetch the ranked CSV from UserSessionData
                var userSessionData = await _dbContext.UserSessionData
                    .FirstOrDefaultAsync(u => u.UserId == userId && u.IsRanked == true);

                if (userSessionData == null || string.IsNullOrEmpty(userSessionData.RankedCSV))
                {
                    return NotFound(new { Message = "No ranked events found for the user." });
                }

                Console.WriteLine($"Fetched ranked CSV for user {userId}.");
                

                // Return the CSV content as a string in the response body
                return Ok(new { csv = userSessionData.RankedCSV });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error fetching ranked CSV for user {userId}: {ex.Message}");
                return StatusCode(500, new { Message = "An error occurred while fetching the ranked CSV." });
            }
        }

        private async Task<List<CombinedEvent>> ProcessEvents(List<UserContent> apiEvents, List<HostEvent> hostEvents, User user)
        {
            var typeMapping = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                { "festivals-fairs", "Festivals" }, { "sports-active-life", "Outdoors" },
                { "visual-arts", "Exhibitions" }, { "charities", "Community" },
                { "performing-arts", "Theater" }, { "kids-family", "Family" },
                { "film", "Film" }, { "food-and-drink", "Food and Drink" },
                { "music", "Music" }, { "Holiday", "Holiday" },
                { "Networking", "Networking" }, { "Gaming", "Gaming" },
                { "Pets", "Pets" }, { "Virtual", "Virtual" },
                { "Science", "Science" }, { "Basketball", "Basketball" },
                { "Pottery", "Pottery" }, { "Tennis", "Tennis" },
                { "Soccer", "Soccer" }, { "Football", "Football" },
                { "Fishing", "Fishing" }, { "Hiking", "Hiking" },
                { "Wellness", "Wellness" }, { "nightlife", "Nightlife" },
                { "Workshops", "Workshops" }, { "Conferences", "Conferences" },
                { "Hockey", "Hockey" }, { "Baseball", "Baseball" },
                { "lectures-books", "Lectures" }, { "fashion", "Fashion" },
                { "Motorsports/Racing", "Motorsports" }, { "Dance", "Dance" },
                { "Comedy", "Comedy" }, { "Pop", "Music" },
                { "Country", "Music" }, { "Hip-Hop/Rap", "Music" },
                { "Rock", "Music" }, { "other", "Other" }
            };

            // Process API events
            var apiEventObjects = new List<CombinedEvent>();
            foreach (var e in apiEvents)
            {
                string location = e.Location ?? "Unknown Location";
                double latitude = 0, longitude = 0;
                if (TryParseLocation(location, out latitude, out longitude))
                {
                    location = _googleGeocodingService.GetAddressFromCoordinates(latitude, longitude).Result;
                }
                else
                {
                    var coordinates = _googleGeocodingService.GetCoordinatesAsync(location).Result;
                    if (coordinates.HasValue)
                    {
                        latitude = coordinates.Value.latitude;
                        longitude = coordinates.Value.longitude;
                    }
                }
                var distance = DistanceCalculator.CalculateDistance(user.Latitude.Value, user.Longitude.Value, latitude, longitude);

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

            // Process host events
            var processedHostEvents = new List<CombinedEvent>();
            foreach (var he in hostEvents)
            {
                double latitude, longitude;
                if (!TryParseLocation(he.Location, out latitude, out longitude))
                {
                    var coordinates = _googleGeocodingService.GetCoordinatesAsync(he.Location).Result;
                    if (coordinates.HasValue)
                    {
                        latitude = coordinates.Value.latitude;
                        longitude = coordinates.Value.longitude;
                    }
                    else
                    {
                        latitude = user.Latitude.Value;
                        longitude = user.Longitude.Value;
                    }
                }
                var distance = DistanceCalculator.CalculateDistance(user.Latitude.Value, user.Longitude.Value, latitude, longitude);

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

            return apiEventObjects.Concat(processedHostEvents).ToList();
        }

        // Endpoint to log out a user and delete their associated CSV file.
        [HttpPost("logout")]
        public async Task<IActionResult> Logout([FromQuery] int userId)
        {
            try
            {
                // Check if the user exists in the database.
                var user = await _dbContext.Users.FindAsync(userId);
                if (user == null)
                {
                    Console.WriteLine($"User with ID {userId} does not exist.");
                    return BadRequest(new { Message = "User not found or not logged in." });
                }

                // Delete the user's row from UserSessionData
                var userSessionData = await _dbContext.UserSessionData
                    .FirstOrDefaultAsync(usd => usd.UserId == userId);
                if (userSessionData != null)
                {
                    _dbContext.UserSessionData.Remove(userSessionData);
                    await _dbContext.SaveChangesAsync();
                    Console.WriteLine($"Deleted UserSessionData for user {userId}.");
                }
                else
                {
                    Console.WriteLine($"No UserSessionData found for user {userId}.");
                }

                // File path for the user's CSV file.
                var csvFilePath = Path.Combine("CsvFiles", $"{userId}.csv");

                // Attempt to delete the CSV file.
                if (System.IO.File.Exists(csvFilePath))
                {
                    try
                    {
                        System.IO.File.Delete(csvFilePath);
                        Console.WriteLine($"Deleted CSV file: {csvFilePath}");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error deleting CSV file {csvFilePath}: {ex.Message}");
                        return StatusCode(500, new { Message = "Error deleting CSV file.", Details = ex.Message });
                    }
                }
                else
                {
                    Console.WriteLine($"CSV file {csvFilePath} does not exist.");
                }

                // Update the user's login status in the database.
                user.IsLoggedIn = false;
                await _dbContext.SaveChangesAsync();
                Console.WriteLine($"User {user.Email} logged out successfully.");

                return Ok(new { Message = "User logged out successfully and session data cleared." });
            }
            catch (Exception ex)
            {
                // Log and return general errors.
                Console.WriteLine($"Error while logging out user {userId}: {ex.Message}");
                return StatusCode(500, new { Message = "An error occurred while logging out.", Details = ex.Message });
            }
        }

        // Endpoint to add a host event to database
        [HttpPost("create-host-event")]
        public async Task<IActionResult> CreateHostEvent([FromBody] HostEvent hostEvent)
        {
            try
            {
                // Validate the incoming event data
                if (!ModelState.IsValid)
                {
                    Console.WriteLine("Invalid host event data received.");
                    return BadRequest("Invalid event data.");
                }

                // Set default values for Source and CreatedAt
                hostEvent.Source = "Host";
                hostEvent.CreatedAt = DateTime.UtcNow;

                // Add the new host event to the database
                await _dbContext.HostEvents.AddAsync(hostEvent);
                await _dbContext.SaveChangesAsync();

                Console.WriteLine($"Host event '{hostEvent.Title}' created successfully.");

                return Ok(new
                {
                    Message = "Host event created successfully.",
                    EventId = hostEvent.EventId
                });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error creating host event: {ex.Message}");
                return StatusCode(500, $"Error creating host event: {ex.Message}");
            }
        }
    }
}