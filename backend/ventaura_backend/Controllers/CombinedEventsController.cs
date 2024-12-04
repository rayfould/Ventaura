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

                            // Write event data to CSV
                            // Write event data to CSV without quotes
                            await writer.WriteLineAsync($"{contentIdCounter}," +
                                                        $"{e.Title}," +
                                                        $"{e.Description}," +
                                                        $"{e.Location}," +
                                                        $"{e.Start?.ToString("yyyy-MM-dd HH:mm:ss") ?? ""}," +
                                                        $"{e.Source}," +
                                                        $"{e.Type}," +
                                                        $"{e.CurrencyCode}," +
                                                        $"{e.Amount?.ToString() ?? ""}," +
                                                        $"{e.URL}," +
                                                        $"{e.Distance}");


                            contentIdCounter++; // Increment contentId for the next event
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

        // OLD Endpoint to fetch and store user-specific event data in a temporary table.
        /* [HttpGet("fetch")]
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

                // Use a single database connection for the operation
                using (var connection = _dbContext.Database.GetDbConnection())
                {
                    await connection.OpenAsync();
                    Console.WriteLine($"Database connection opened successfully for userId: {userId}");
                    Console.WriteLine($"Connection state before table existence check: {connection.State}");

                    string tableExistsQuery = $@"
                        SELECT EXISTS (
                            SELECT 1
                            FROM pg_catalog.pg_tables
                            WHERE schemaname = 'public'
                            AND tablename = 'usercontent_{userId}'
                        );";

                    bool tableExists = false;

                    // Retry logic to handle connection or query issues
                    for (int attempt = 0; attempt < 3; attempt++)
                    {
                        try
                        {
                            // Check if the user-specific table exists
                            Console.WriteLine($"Checking for existing UserContent_{userId} table...");
                            using (var checkTableCommand = connection.CreateCommand())
                            {
                                checkTableCommand.CommandText = tableExistsQuery;
                                Console.WriteLine($"SQL Command: {checkTableCommand.CommandText}");

                                var result = await checkTableCommand.ExecuteScalarAsync();
                                Console.WriteLine($"Query executed successfully. Result: {result}");

                                tableExists = result != null && (bool)result;
                                Console.WriteLine($"Table existence check result: {tableExists}");
                                break; // Exit the loop if successful
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Attempt {attempt + 1} failed: {ex.Message}");

                            // Close and reopen the connection if it's invalid
                            if (connection.State != System.Data.ConnectionState.Open)
                            {
                                Console.WriteLine("Reopening database connection...");
                                await connection.OpenAsync();
                                Console.WriteLine($"Connection reopened successfully. State: {connection.State}");
                            }

                            if (attempt == 2) throw; // Re-throw after the 3rd attempt
                        }
                    }

                    // Drop the table if it exists
                    if (tableExists)
                    {
                        Console.WriteLine($"UserContent_{userId} table exists. Dropping...");
                        using var dropTableCommand = connection.CreateCommand();
                        dropTableCommand.CommandText = $@"DROP TABLE usercontent_{userId};";
                        await dropTableCommand.ExecuteNonQueryAsync();
                        Console.WriteLine($"UserContent_{userId} table dropped.");
                    }

                    // Create the user-specific table
                    Console.WriteLine($"Creating UserContent_{userId} table...");
                    using (var createTableCommand = connection.CreateCommand())
                    {
                        createTableCommand.CommandText = $@"
                            CREATE TABLE usercontent_{userId} (
                                ContentId SERIAL PRIMARY KEY,
                                Title VARCHAR(255),
                                Description TEXT,
                                Location VARCHAR(255),
                                Start TIMESTAMPTZ,
                                Source VARCHAR(50),
                                Type VARCHAR(50),
                                CurrencyCode VARCHAR(10),
                                Amount VARCHAR(20),
                                URL TEXT,
                                Distance FLOAT
                            );";
                        Console.WriteLine($"SQL Command: {createTableCommand.CommandText}");
                        await createTableCommand.ExecuteNonQueryAsync();
                        Console.WriteLine($"UserContent_{userId} table created.");
                    }

                    // Fetch events from the combined API service
                    Console.WriteLine($"Fetching events for userId {userId}...");
                    var events = await _combinedApiService.FetchEventsAsync(user.Latitude.Value, user.Longitude.Value, userId);

                    // Batch insert events into the user-specific table
                    if (events.Any())
                    {
                        Console.WriteLine($"Preparing batch insert for {events.Count} events.");

                        var insertValues = events.Select(e =>
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

                            return $@"
                                ('{e.Title?.Replace("'", "''")}', 
                                '{e.Description?.Replace("'", "''")}', 
                                '{e.Location?.Replace("'", "''")}', 
                                '{e.Start?.ToString("yyyy-MM-dd HH:mm:ss") ?? "NULL"}', 
                                '{e.Source?.Replace("'", "''")}', 
                                '{e.Type?.Replace("'", "''")}', 
                                '{e.CurrencyCode?.Replace("'", "''")}', 
                                '{e.Amount?.ToString() ?? "NULL"}', 
                                '{e.URL?.Replace("'", "''")}', 
                                {e.Distance ?? 0})";
                        }).ToList();

                        using var batchInsertCommand = connection.CreateCommand();
                        batchInsertCommand.CommandText = $@"
                            INSERT INTO usercontent_{userId} 
                            (Title, Description, Location, Start, Source, Type, CurrencyCode, Amount, URL, Distance) 
                            VALUES {string.Join(",", insertValues)};";
                        await batchInsertCommand.ExecuteNonQueryAsync();
                        Console.WriteLine("Batch insert completed successfully.");
                    }
                    else
                    {
                        Console.WriteLine("No events to insert.");
                    }

                    return Ok(new
                    {
                        Message = "Events processed successfully.",
                        Table = $"usercontent_{userId}",
                        TotalEvents = events.Count,
                        ValidEvents = events.Count(e => !string.IsNullOrEmpty(e.Location)),
                        InvalidEvents = events.Count(e => string.IsNullOrEmpty(e.Location))
                    });
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in FetchCombinedEvents: {ex.Message}");
                return StatusCode(500, "An error occurred while fetching events.");
            }
        }*/

        // OLD Endpoint to log out a user and clear their session-specific content.
        /* [HttpPost("logout")]
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

                // Use a single DbConnection for direct SQL execution.
                using (var connection = _dbContext.Database.GetDbConnection())
                {
                    for (int attempt = 0; attempt < 3; attempt++)
                    {
                        try
                        {
                            if (connection.State != System.Data.ConnectionState.Open)
                            {
                                Console.WriteLine("Opening database connection...");
                                await connection.OpenAsync();
                                Console.WriteLine($"Connection opened successfully. State: {connection.State}");
                            }

                            // Drop the user-specific table if it exists.
                            using (var dropTableCommand = connection.CreateCommand())
                            {
                                dropTableCommand.CommandText = $@"DROP TABLE IF EXISTS usercontent_{userId};";
                                Console.WriteLine($"Executing: {dropTableCommand.CommandText}");
                                await dropTableCommand.ExecuteNonQueryAsync();
                                Console.WriteLine($"UserContent_{userId} table dropped if it existed.");
                            }

                            break; // Exit the retry loop if successful
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Attempt {attempt + 1} failed: {ex.Message}");

                            if (connection.State != System.Data.ConnectionState.Open)
                            {
                                Console.WriteLine("Reopening database connection...");
                                await connection.CloseAsync();
                                await connection.OpenAsync();
                                Console.WriteLine($"Connection reopened successfully. State: {connection.State}");
                            }

                            if (attempt == 2) throw; // Re-throw after 3rd attempt
                        }
                    }
                }

                // Update the user's login status in the database.
                user.IsLoggedIn = false;
                await _dbContext.SaveChangesAsync();
                Console.WriteLine($"User {user.Email} logged out successfully.");

                return Ok(new { Message = "User logged out successfully." });
            }
            catch (Npgsql.PostgresException ex)
            {
                // Log and return database-specific errors.
                Console.WriteLine($"Postgres error while logging out user {userId}: {ex.Message}");
                return StatusCode(500, new { Message = "Database error.", Details = ex.Message });
            }
            catch (Exception ex)
            {
                // Log and return general errors.
                Console.WriteLine($"Error while logging out user {userId}: {ex.Message}");
                return StatusCode(500, new { Message = "An error occurred while logging out.", Details = ex.Message });
            }
        }*/

    }
}
