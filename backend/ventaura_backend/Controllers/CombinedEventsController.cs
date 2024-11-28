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

                    // Insert events into the user-specific table
                    Console.WriteLine($"Inserting events into UserContent_{userId} table...");
                    foreach (var e in events)
                    {
                        var eventCoordinates = e.Location?.Split(',');
                        if (eventCoordinates == null || eventCoordinates.Length != 2)
                        {
                            // Console.WriteLine($"Invalid location format for event: {e.Title}");
                            continue;
                        }

                        double.TryParse(eventCoordinates[0], out var eventLatitude);
                        double.TryParse(eventCoordinates[1], out var eventLongitude);

                        var distance = DistanceCalculator.CalculateDistance(
                            user.Latitude.Value,
                            user.Longitude.Value,
                            eventLatitude,
                            eventLongitude
                        );
                        e.Distance = (float)distance;

                        // Console.WriteLine($"Distance successfully calculated with a value of {distance}.");

                        using var insertCommand = connection.CreateCommand();
                        insertCommand.CommandText = $@"
                            INSERT INTO usercontent_{userId} 
                            (Title, Description, Location, Start, Source, Type, CurrencyCode, Amount, URL, Distance) 
                            VALUES (@Title, @Description, @Location, @Start, @Source, @Type, @CurrencyCode, @Amount, @URL, @Distance);";

                        insertCommand.Parameters.Add(new Npgsql.NpgsqlParameter("Title", e.Title ?? (object)DBNull.Value));
                        insertCommand.Parameters.Add(new Npgsql.NpgsqlParameter("Description", e.Description ?? (object)DBNull.Value));
                        insertCommand.Parameters.Add(new Npgsql.NpgsqlParameter("Location", e.Location ?? (object)DBNull.Value));
                        insertCommand.Parameters.Add(new Npgsql.NpgsqlParameter("Start", e.Start.HasValue ? e.Start.Value : (object)DBNull.Value));
                        insertCommand.Parameters.Add(new Npgsql.NpgsqlParameter("Source", e.Source ?? (object)DBNull.Value));
                        insertCommand.Parameters.Add(new Npgsql.NpgsqlParameter("Type", e.Type ?? (object)DBNull.Value));
                        insertCommand.Parameters.Add(new Npgsql.NpgsqlParameter("CurrencyCode", e.CurrencyCode ?? (object)DBNull.Value));
                        insertCommand.Parameters.Add(new Npgsql.NpgsqlParameter("Amount", e.Amount.HasValue ? e.Amount.Value : (object)DBNull.Value));
                        insertCommand.Parameters.Add(new Npgsql.NpgsqlParameter("URL", e.URL ?? (object)DBNull.Value));
                        insertCommand.Parameters.Add(new Npgsql.NpgsqlParameter("Distance", e.Distance));

                        await insertCommand.ExecuteNonQueryAsync();
                    }

                    return Ok(new
                    {
                        Message = $"Table usercontent_{userId} created and populated.",
                        EventCount = events.Count
                    });
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in FetchCombinedEvents: {ex.Message}");
                return StatusCode(500, "An error occurred while fetching events.");
            }
        }

        // Endpoint to log out a user and clear their session-specific content.
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

                // Use a single DbConnection for direct SQL execution.
                using var connection = _dbContext.Database.GetDbConnection();
                await connection.OpenAsync();

                // Check if the user's temporary table exists before attempting to drop it.
                Console.WriteLine($"Checking if UserContent_{userId} table exists...");
                using (var checkTableCommand = connection.CreateCommand())
                {
                    checkTableCommand.CommandText = $@"
                        SELECT EXISTS (
                            SELECT FROM pg_tables 
                            WHERE schemaname = 'public' 
                            AND tablename = 'usercontent_{userId}'
                        );";
                    
                    var tableExists = (bool)(await checkTableCommand.ExecuteScalarAsync() ?? false);
                    
                    if (tableExists)
                    {
                        Console.WriteLine($"UserContent_{userId} table exists. Attempting to drop it...");
                        using (var dropTableCommand = connection.CreateCommand())
                        {
                            dropTableCommand.CommandText = $@"DROP TABLE usercontent_{userId};";
                            await dropTableCommand.ExecuteNonQueryAsync();
                            Console.WriteLine($"UserContent_{userId} table successfully dropped.");
                        }
                    }
                    else
                    {
                        Console.WriteLine($"UserContent_{userId} table does not exist. Skipping drop operation.");
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
        }
    }
}
