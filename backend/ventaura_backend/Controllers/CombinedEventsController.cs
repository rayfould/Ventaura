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
                // Retrieve the user and validate their location data.
                var user = await _dbContext.Users.FindAsync(userId);
                if (user == null || user.Latitude == null || user.Longitude == null)
                {
                    Console.WriteLine($"User with ID {userId} not found or location data is missing.");
                    return BadRequest("User not found or location is missing.");
                }

                Console.WriteLine($"Location successfully extracted for {userId}...");

                // Use a single DbConnection for direct SQL execution.
                // Open a database connection for SQL execution.
                using var connection = _dbContext.Database.GetDbConnection();
                await connection.OpenAsync();

                // Check if the table exists for the user and drop it if it does.
                Console.WriteLine($"Checking if UserContent_{userId} table exists...");

                using (var checkTableCommand = connection.CreateCommand())
                {
                    checkTableCommand.CommandText = $@"
                        DO $$
                        BEGIN
                            IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'usercontent_{userId}') THEN
                                EXECUTE 'DROP TABLE usercontent_{userId}';
                            END IF;
                        END $$;";
                    await checkTableCommand.ExecuteNonQueryAsync();
                }

                // Create the user-specific UserContent table.
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
                    await createTableCommand.ExecuteNonQueryAsync();
                }

                // Fetch events from the combined API service based on user's location.
                Console.WriteLine($"Fetching events for userId {userId}...");
                var events = await _combinedApiService.FetchEventsAsync(user.Latitude ?? 0, user.Longitude ?? 0, userId);

                // Insert fetched events into the user's temporary table.
                Console.WriteLine($"Inserting events into UserContent_{userId} table...");
                foreach (var e in events)
                {

                    // Parse event location into latitude and longitude
                    var eventCoordinates = e.Location?.Split(',');
                    if (eventCoordinates == null || eventCoordinates.Length != 2)
                    {
                        Console.WriteLine($"Invalid location format for event: {e.Title}");
                        continue;
                    }

                    double.TryParse(eventCoordinates[0], out var eventLatitude);
                    double.TryParse(eventCoordinates[1], out var eventLongitude);

                    // Calculate distance
                    var distance = DistanceCalculator.CalculateDistance(
                        user.Latitude ?? 0, 
                        user.Longitude ?? 0, 
                        eventLatitude, 
                        eventLongitude
                    );
                    e.Distance = (float)distance; // Assign calculated distance to the event object

                    Console.WriteLine($"Distance successfully calculated with a value of {distance}.");

                    using var insertCommand = connection.CreateCommand();

                    insertCommand.CommandText = $@"
                        INSERT INTO usercontent_{userId} 
                        (Title, Description, Location, Start, Source, Type, CurrencyCode, Amount, URL, Distance) 
                        VALUES (@Title, @Description, @Location, @Start, @Source, @Type, @CurrencyCode, @Amount, @URL, @Distance);";

                    // Add parameters for safe insertion of event data.
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

                // Retrieve the inserted events with their ContentId values.
                var insertedEvents = new List<object>();
                using (var fetchCommand = connection.CreateCommand())
                {
                    fetchCommand.CommandText = $@"
                        SELECT ContentId, Title, Description, Location, Start, Source, Type, CurrencyCode, Amount, URL, Distance
                        FROM usercontent_{userId};";

                    using var reader = await fetchCommand.ExecuteReaderAsync();
                    while (await reader.ReadAsync())
                    {
                        insertedEvents.Add(new
                        {
                            ContentId = reader.GetInt32(0),
                            Title = reader.IsDBNull(1) ? null : reader.GetString(1),
                            Description = reader.IsDBNull(2) ? null : reader.GetString(2),
                            Location = reader.IsDBNull(3) ? null : reader.GetString(3),
                            Start = reader.IsDBNull(4) ? (DateTime?)null : reader.GetDateTime(4), // Explicitly handle nullable DateTime
                            Source = reader.IsDBNull(5) ? null : reader.GetString(5),
                            Type = reader.IsDBNull(6) ? null : reader.GetString(6),
                            CurrencyCode = reader.IsDBNull(7) ? null : reader.GetString(7),
                            Amount = reader.IsDBNull(8) ? null : reader.GetString(8),
                            URL = reader.IsDBNull(9) ? null : reader.GetString(9),
                            Distance = reader.IsDBNull(10) ? (float?)null : (float)reader.GetFloat(10)

                        });
                    }
                }

                Console.WriteLine($"Table usercontent_{userId} created and populated.");

                return Ok(new {
                    Message = $"Table usercontent_{userId} created and populated.", 
                    EventCount = events.Count,
                    // events
                    insertedEvents
                    //rankedEvents 
                });
            }
            catch (Npgsql.PostgresException ex)
            {
                // Log and return database-specific errors.
                Console.WriteLine($"Postgres error: {ex.Message}");
                return StatusCode(500, $"Database error: {ex.Message}");
            }
            catch (Exception ex)
            {
                // Log and return general errors.
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
