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
                // Retrieve the user and validate their location data
                var user = await _dbContext.Users.FindAsync(userId);
                if (user == null || user.Latitude == null || user.Longitude == null)
                {
                    Console.WriteLine($"User with ID {userId} not found or location data is missing.");
                    return BadRequest("User not found or location is missing.");
                }

                Console.WriteLine($"Location successfully extracted for userId: {userId}.");

                // Fetch events from the combined API service
                Console.WriteLine($"Fetching events for userId {userId}...");
                var events = await _combinedApiService.FetchEventsAsync(user.Latitude.Value, user.Longitude.Value, userId);

                // Process events for CSV creation
                if (events.Any())
                {
                    Console.WriteLine($"Preparing data for {events.Count} events to generate CSV.");

                    var csvFilePath = Path.Combine("CsvFiles", $"{userId}.csv");

                    // Ensure the directory exists
                    var directory = Path.GetDirectoryName(csvFilePath);
                    if (!Directory.Exists(directory))
                    {
                        Directory.CreateDirectory(directory);
                    }

                    // Write CSV file
                    using (var writer = new StreamWriter(csvFilePath, false, Encoding.UTF8))
                    {
                        // Write header
                        // Write lowercase header with contentId
                        await writer.WriteLineAsync("contentId,title,description,location,start,source,type,currencyCode,amount,url,distance");
                        
                        int contentIdCounter = 1; // Start unique ID counter
                        foreach (var e in events)
                        {
                            // Handle invalid or missing event locations
                            double eventLatitude, eventLongitude;
                            if (string.IsNullOrEmpty(e.Location) ||
                                !e.Location.Contains(",") ||
                                !double.TryParse(e.Location.Split(',')[0], out eventLatitude) ||
                                !double.TryParse(e.Location.Split(',')[1], out eventLongitude))
                            {
                                eventLatitude = user.Latitude.Value;
                                eventLongitude = user.Longitude.Value;
                            }

                            var distance = DistanceCalculator.CalculateDistance(
                                user.Latitude.Value,
                                user.Longitude.Value,
                                eventLatitude,
                                eventLongitude
                            );
                            e.Distance = (float)distance;

                            // Helper function to clean text fields
                            string CleanField(string field)
                            {
                                if (string.IsNullOrEmpty(field)) return "";
                                
                                // Remove newlines and extra spaces
                                field = field.Replace("\r", " ")
                                            .Replace("\n", " ")
                                            .Replace("  ", " ")
                                            .Trim();
                                
                                // Quote if field contains commas or quotes
                                if (field.Contains(",") || field.Contains("\""))
                                    return $"\"{field.Replace("\"", "\"\"")}\"";
                                
                                return field;
                            }

                            // Write the line with cleaned fields
                            await writer.WriteLineAsync(
                                $"{contentIdCounter}," +
                                $"{CleanField(e.Title)}," +
                                $"{CleanField(e.Description)}," +
                                $"{CleanField(e.Location)}," +
                                $"{CleanField(e.Start?.ToString("yyyy-MM-dd HH:mm:ss"))}," +
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

                    Console.WriteLine($"CSV file created at {csvFilePath}.");

                    return Ok(new
                    {
                        Message = "Events processed successfully and CSV created.",
                        CsvPath = csvFilePath,
                        TotalEvents = events.Count,
                        ValidEvents = events.Count(e => !string.IsNullOrEmpty(e.Location)),
                        InvalidEvents = events.Count(e => string.IsNullOrEmpty(e.Location))
                    });
                }
                else
                {
                    Console.WriteLine("No events to process.");
                    return Ok(new { Message = "No events available to process.", TotalEvents = 0 });
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in FetchCombinedEvents: {ex.Message}");
                return StatusCode(500, "An error occurred while fetching events.");
            }
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

                var csvContent = System.IO.File.ReadAllText(csvFilePath);

                Console.WriteLine($"Serving CSV file {csvFilePath} for userId {userId}.");
                return Content(csvContent, "text/csv");
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