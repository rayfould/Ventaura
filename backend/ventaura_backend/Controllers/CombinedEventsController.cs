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

        // Constructor to inject dependencies for the API service and database context.
        public CombinedEventsController(CombinedAPIService combinedApiService, DatabaseContext dbContext)
        {
            _combinedApiService = combinedApiService;
            _dbContext = dbContext;
        }

        // Endpoint to fetch and store user-specific event data in a temporary table.
        [HttpGet("fetch")]
        public async Task<IActionResult> FetchCombinedEvents([FromQuery] int userId)
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
                    { "other", "Other" }
                };

                // **2. Get User**
                var user = await _dbContext.Users.FindAsync(userId);
                if (user == null || user.Latitude == null || user.Longitude == null)
                {
                    Console.WriteLine($"User with ID {userId} not found or location data is missing.");
                    return BadRequest("User not found or location is missing.");
                }

                Console.WriteLine($"Location successfully extracted for userId: {userId}.");

                 // **3. Fetch API Events**
                Console.WriteLine($"Fetching events from API for userId {userId}...");
                var apiEvents = await _combinedApiService.FetchEventsAsync(user.Latitude.Value, user.Longitude.Value, userId);

                // **4. Fetch Host Events**
                Console.WriteLine($"Fetching host events for userId {userId}...");
                var hostEvents = await _dbContext.HostEvents.ToListAsync();

                // **5. Process API Events**
                var apiEventObjects = apiEvents.Select(e => new CombinedEvent
                {
                    Title = e.Title ?? "Unknown Title",
                    Description = e.Description ?? "No description",
                    Location = e.Location ?? "Unknown Location",
                    Start = e.Start,
                    Source = e.Source ?? "API",
                    Type = typeMapping.ContainsKey(e.Type.ToLower()) ? typeMapping[e.Type.ToLower()] : e.Type,
                    CurrencyCode = e.CurrencyCode ?? "N/A",
                    Amount = (decimal?)e.Amount ?? 0,
                    URL = e.URL ?? "N/A",
                    Distance = e.Distance ?? 0
                }).ToList();

                 // **6. Process Host Events**
                var processedHostEvents = hostEvents.Select(he => 
                {
                    double latitude, longitude;
                    if (!TryParseLocation(he.Location, out latitude, out longitude))
                    {
                        latitude = user.Latitude.Value;
                        longitude = user.Longitude.Value;
                    }

                    var distance = DistanceCalculator.CalculateDistance(user.Latitude.Value, user.Longitude.Value, latitude, longitude);

                    return new CombinedEvent
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
                    };
                }).ToList();

                // **7. Combine Events**
                var combinedEvents = apiEventObjects.Concat(processedHostEvents).ToList();

                if (!combinedEvents.Any())
                {
                    Console.WriteLine("No events to process.");
                    return Ok(new { Message = "No events available to process.", TotalEvents = 0 });
                }

                // **8. Write CSV File**
                var csvFilePath = Path.Combine("CsvFiles", $"{userId}.csv");
                Directory.CreateDirectory(Path.GetDirectoryName(csvFilePath));

                using (var writer = new StreamWriter(csvFilePath, false, Encoding.UTF8))
                {
                    await writer.WriteLineAsync("contentId,title,description,location,start,source,type,currencyCode,amount,url,distance");

                    int contentIdCounter = 1;
                    foreach (var e in combinedEvents)
                    {
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
                    }
                }

                return Ok(new { Message = "Events processed successfully and CSV created.", CsvPath = csvFilePath });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in FetchCombinedEvents: {ex.Message}");
                return StatusCode(500, "An error occurred while fetching events.");
            }
        }

        private string CleanField(string field)
        {
            if (string.IsNullOrEmpty(field)) return "";
            field = field.Replace("\r", " ").Replace("\n", " ").Trim();
            if (field.Contains(",") || field.Contains("\""))
                return $"\"{field.Replace("\"", "\"\"")}\"";
            return field;
        }

        private bool TryParseLocation(string location, out double latitude, out double longitude)
        {
            latitude = 0;
            longitude = 0;
            if (string.IsNullOrEmpty(location) || !location.Contains(",")) return false;
            var parts = location.Split(',');
            return double.TryParse(parts[0].Trim(), out latitude) && double.TryParse(parts[1].Trim(), out longitude);
        }

        // Endpoint for the frontend to access th csv file - TO BE MODIFIEF
        [HttpGet("get-csv")]
        public IActionResult GetCsv([FromQuery] int userId)
        {
            try
            {
                var csvFilePath = Path.Combine("CsvFiles", $"{userId}.csv");

                if (!System.IO.File.Exists(csvFilePath))
                {
                    Console.WriteLine($"CSV file {csvFilePath} does not exist.");
                    return NotFound(new { Message = "CSV file not found." });
                }

                // Return the CSV file as a response
                var fileStream = new FileStream(csvFilePath, FileMode.Open, FileAccess.Read);
                var fileName = $"{userId}.csv";

                Console.WriteLine($"Serving CSV file {csvFilePath}.");
                return File(fileStream, "text/csv", fileName);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error while fetching CSV for user {userId}: {ex.Message}");
                return StatusCode(500, "An error occurred while fetching the CSV file.");
            }
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

                return Ok(new { Message = "User logged out successfully and CSV file deleted." });
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