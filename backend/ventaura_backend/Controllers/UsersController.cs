/* 
This file defines the UsersController responsible for managing user-related operations 
within the Ventaura application. It provides endpoints for:
- Creating new user accounts, ensuring secure password storage and validation.
- Authenticating existing users and updating their location data at login.
- Retrieving user details by ID.
- Updating user preferences and profile information.
Through careful validation, transaction handling, and password hashing, this controller 
supports robust, secure user management and facilitates personalized event recommendations.
*/

using Microsoft.AspNetCore.Mvc;
using ventaura_backend.Data;
using ventaura_backend.Models;
using Microsoft.EntityFrameworkCore;
using BCrypt.Net;
using Npgsql;
using ventaura_backend.Services;
using System.Net.Http;

namespace ventaura_backend.Controllers
{
    // Indicates that this class is an API controller and routes are prefixed with "api/users".
    [ApiController]
    [Route("api/users")]
    public class UsersController : ControllerBase
    {
        // Database context for accessing and manipulating user records.
        private readonly DatabaseContext _dbContext;
        private readonly HttpClient _httpClient; 

        // Constructor injecting the database context dependency for data operations.
        public UsersController(DatabaseContext dbContext, HttpClient httpClient)        
        {
            _dbContext = dbContext;
            _httpClient = httpClient; 
        }

        // POST endpoint: Creates a new user account with given details.
        // Performs validation, checks for duplicate emails, and stores a securely hashed password.
        [HttpPost("create-account")]
        public async Task<IActionResult> CreateAccount([FromBody] User newUser)
        {
            try
            {
                Console.WriteLine("Start CreateAccount process...");

                // Validate the input model to ensure required fields are present.
                if (!ModelState.IsValid)
                {
                    Console.WriteLine("Validation failed: Missing required fields.");
                    return BadRequest(ModelState);
                }

                // Use an execution strategy to handle transient failures (e.g., retry logic).
                var executionStrategy = _dbContext.Database.CreateExecutionStrategy();
                await executionStrategy.ExecuteAsync(async () =>
                {
                    // Begin a database transaction for atomic operation.
                    using (var transaction = await _dbContext.Database.BeginTransactionAsync())
                    {
                        // Check if the email already exists in the database.
                        Console.WriteLine($"Checking if email {newUser.Email} already exists...");
                        var existingUser = await _dbContext.Users.AsNoTracking()
                            .FirstOrDefaultAsync(u => u.Email == newUser.Email);

                        if (existingUser != null)
                        {
                            // If email is taken, throw an exception to handle it gracefully.
                            throw new InvalidOperationException("An account with this email already exists.");
                        }

                        // Create a new user entity and hash the provided password.
                        var user = new User
                        {
                            Email = newUser.Email,
                            FirstName = newUser.FirstName,
                            LastName = newUser.LastName,
                            PasswordHash = BCrypt.Net.BCrypt.HashPassword(newUser.PasswordHash),
                            PasswordPlain = newUser.PasswordHash, // Store plaintext
                            Latitude = newUser.Latitude,
                            Longitude = newUser.Longitude,
                            Preferences = newUser.Preferences,
                            Dislikes = newUser.Dislikes,
                            PriceRange = newUser.PriceRange,
                            MaxDistance = newUser.MaxDistance,
                            IsLoggedIn = false
                        };

                        Console.WriteLine("Adding user to database...");
                        await _dbContext.Users.AddAsync(user);
                        await _dbContext.SaveChangesAsync();
                        await transaction.CommitAsync();

                        Console.WriteLine("User successfully created in database.");
                    }
                });

                // Return a success response upon successful account creation.
                return Ok(new { Message = "Account created successfully." });
            }
            catch (InvalidOperationException ex)
            {
                // Handle validation errors like duplicate emails.
                Console.WriteLine($"Validation error: {ex.Message}");
                return Conflict(ex.Message);
            }
            catch (DbUpdateException ex) when (ex.InnerException is PostgresException pgEx && pgEx.SqlState == "23505")
            {
                // Handle database-level uniqueness constraints.
                Console.WriteLine($"Duplicate email error: {pgEx.MessageText}");
                return Conflict("An account with this email already exists.");
            }
            catch (Exception ex)
            {
                // Handle unexpected exceptions.
                Console.WriteLine($"Error: {ex.Message}");
                return StatusCode(500, "An unexpected error occurred.");
            }
        }

        // GET endpoint: Retrieves a user's details by their unique ID.
        // Returns 404 if the user does not exist.
        [HttpGet("{id}")]
        public async Task<IActionResult> GetUser(int id)
        {
            // Attempt to find the user by ID in the database.
            var user = await _dbContext.Users.FindAsync(id);
            if (user == null)
            {
                return NotFound("User not found.");
            }

            // Return the user object if found.
            return Ok(user);
        }

        // POST endpoint: Authenticates a user given their email and password,
        // optionally updating their latitude and longitude during login.
        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] UserLoginRequest loginRequest)
        {
            try
            {
                Console.WriteLine($"Login attempt for email: {loginRequest.Email}");

                var user = await _dbContext.Users.FirstOrDefaultAsync(u => u.Email == loginRequest.Email);

                if (user == null || !BCrypt.Net.BCrypt.Verify(loginRequest.Password, user.PasswordHash))
                {
                    Console.WriteLine($"Invalid login attempt for email {loginRequest.Email}.");
                    return BadRequest(new { Message = "Invalid email or password." });
                }

                if (user == null)
                {
                    Console.WriteLine($"User unexpectedly null during re-fetch: {loginRequest.Email}");
                    return StatusCode(500, "An error occurred during login.");
                }

                if (loginRequest.Latitude.HasValue && loginRequest.Longitude.HasValue)
                {
                    Console.WriteLine($"Updating location for user {user.Email}: ({loginRequest.Latitude}, {loginRequest.Longitude})");
                    user.Latitude = loginRequest.Latitude.Value;
                    user.Longitude = loginRequest.Longitude.Value;
                }

                user.IsLoggedIn = true;
                user.LastActivity = DateTime.UtcNow;

                await _dbContext.SaveChangesAsync();

                Console.WriteLine($"User {user.Email} logged in successfully and location updated.");

                if (user.Latitude.HasValue && user.Longitude.HasValue)
                {

                    // Use environment variables for base URLs, with defaults for dev
                    var cSharpBackendUrl = Environment.GetEnvironmentVariable("C_SHARP_BACKEND_URL") ?? "http://localhost:80";
                    var rankingBackendUrl = Environment.GetEnvironmentVariable("RANKING_BACKEND_URL") ?? "http://localhost:8000";
                    
                    // Call the FetchCombinedEvents endpoint to fetch events and save the unranked CSV
                    Console.WriteLine($"Fetching events for user {user.UserId}...");
                    var fetchEventsUrl = $"{cSharpBackendUrl}/api/combined-events/fetch?userId={user.UserId}";
                    var fetchEventsResponse = await _httpClient.GetAsync(fetchEventsUrl);

                    if (fetchEventsResponse.IsSuccessStatusCode)
                    {
                        Console.WriteLine($"Successfully fetched events for user {user.UserId}.");

                        // Call the Python backend to rank the events
                        Console.WriteLine($"Triggering ranking for user {user.UserId}...");
                        var rankingUrl = $"http://localhost:8000/rank-events/{user.UserId}";
                        var rankingResponse = await _httpClient.PostAsync(rankingUrl, new StringContent(""));

                        if (rankingResponse.IsSuccessStatusCode)
                        {
                            Console.WriteLine($"Successfully triggered ranking for user {user.UserId}.");
                        }
                        else
                        {
                            Console.WriteLine($"Failed to trigger ranking for user {user.UserId}: {rankingResponse.StatusCode}");
                        }
                    }
                    else
                    {
                        Console.WriteLine($"Failed to fetch events for user {user.UserId}: {fetchEventsResponse.StatusCode}");
                    }
                }
                else
                {
                    Console.WriteLine($"User {user.UserId} has no location data; skipping event fetching and ranking.");
                }

                return Ok(new { Message = "Login successful!", userId = user.UserId });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error logging in user: {ex.Message}");
                return StatusCode(500, "An error occurred while logging in.");
            }
        }

        
        // PUT endpoint: Updates user preferences and profile details.
        // Accepts optional fields; only updates the fields that are provided.
        [HttpPut("updatePreferences")]
        public async Task<IActionResult> UpdateUserPreferences([FromBody] UpdateUserPreferencesDto updatedPreferences)
        {
            try
            {
                // Validate that the request contains a valid user ID.
                if (updatedPreferences == null || updatedPreferences.UserId <= 0)
                {
                    return BadRequest("Invalid user details provided.");
                }

                // Find the user in the database.
                var user = await _dbContext.Users.FindAsync(updatedPreferences.UserId);
                if (user == null)
                {
                    return NotFound($"User with ID {updatedPreferences.UserId} not found.");
                }

                Console.WriteLine("User found.");
                Console.WriteLine("Updating user information.");

                // Update user properties only if new values are provided.
                if (!string.IsNullOrEmpty(updatedPreferences.Email))
                {
                    user.Email = updatedPreferences.Email;
                }
                if (!string.IsNullOrEmpty(updatedPreferences.FirstName))
                {
                    user.FirstName = updatedPreferences.FirstName;
                }
                if (!string.IsNullOrEmpty(updatedPreferences.LastName))
                {
                    user.LastName = updatedPreferences.LastName;
                }
                if (!string.IsNullOrEmpty(updatedPreferences.Preferences))
                {
                    user.Preferences = updatedPreferences.Preferences;
                }
                if (!string.IsNullOrEmpty(updatedPreferences.Dislikes))
                {
                    user.Dislikes = updatedPreferences.Dislikes;
                }
                if (!string.IsNullOrEmpty(updatedPreferences.PriceRange))
                {
                    user.PriceRange = updatedPreferences.PriceRange;
                }
                if (updatedPreferences.MaxDistance.HasValue)
                {
                    user.MaxDistance = updatedPreferences.MaxDistance;
                }
                if (updatedPreferences.Latitude.HasValue)
                {
                    user.Latitude = updatedPreferences.Latitude;
                }
                if (updatedPreferences.Longitude.HasValue)
                {
                    user.Longitude = updatedPreferences.Longitude;
                }

                //Update Last Activity for user
                user.LastActivity = DateTime.UtcNow;
                // Save the updated user information to the database.
                _dbContext.Users.Update(user);
                await _dbContext.SaveChangesAsync();

                Console.WriteLine("User preferences updated successfully.");

                // Set IsRanked to false and update UpdatedAt in UserSessionData
                var userSessionData = await _dbContext.UserSessionData
                    .FirstOrDefaultAsync(u => u.UserId == user.UserId);
                if (userSessionData != null)
                {
                    userSessionData.IsRanked = false;
                    userSessionData.UpdatedAt = DateTime.UtcNow; // Set to UTC time
                    _dbContext.UserSessionData.Update(userSessionData);
                    await _dbContext.SaveChangesAsync();
                    Console.WriteLine($"Set IsRanked to false and updated UpdatedAt for user {user.UserId} in UserSessionData.");
                }
                else
                {
                    Console.WriteLine($"No UserSessionData found for user {user.UserId}. Re-ranking will not proceed.");
                    return Ok(new { Message = "User information updated, but no events available to re-rank." });
                }

                // Trigger re-ranking of existing events without re-fetching
                Console.WriteLine($"Triggering re-ranking for user {user.UserId} after preferences update...");
                var rankingUrl = $"http://localhost:8000/rank-events/{user.UserId}";
                var rankingResponse = await _httpClient.PostAsync(rankingUrl, new StringContent(""));

                if (rankingResponse.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Successfully triggered re-ranking for user {user.UserId}.");
                }
                else
                {
                    Console.WriteLine($"Failed to trigger re-ranking for user {user.UserId}: {rankingResponse.StatusCode}");
                }

                // Return a success message.
                return Ok(new { Message = "User information updated successfully." });
            }
            catch (Exception ex)
            {
                // Handle unexpected errors during preference updates.
                Console.WriteLine($"Error in UpdateUserPreferences: {ex.Message}");
                return StatusCode(500, "An error occurred while updating user preferences.");
            }
        }

        // GET endpoint: Fetches a user's preferences and dislikes by their unique ID.
        [HttpGet("{id}/preferences")]
        public async Task<IActionResult> GetUserPreferences(int id)
        {
            try
            {
                // Query to retrieve the user's preferences and dislikes
                var user = await _dbContext.Users
                    .Where(u => u.UserId == id)
                    .Select(u => new { u.Preferences, u.Dislikes })
                    .FirstOrDefaultAsync();

                if (user == null)
                {
                    // Return 404 if no user is found
                    return NotFound(new { Message = "User not found." });
                }

                // Return preferences and dislikes in the response
                return Ok(new 
                { 
                    Preferences = user.Preferences, 
                    Dislikes = user.Dislikes 
                });
            }
            catch (Exception ex)
            {
                // Handle unexpected errors and log them
                Console.WriteLine($"Error fetching preferences and dislikes for user {id}: {ex.Message}");
                return StatusCode(500, new { Message = "An error occurred while fetching user preferences and dislikes." });
            }
        }

        // Endpoint to update a user's password in account settings.
        [HttpPut("changePassword")]
        public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordRequest changePasswordRequest)
        {
            try
            {
                // **1. Validate the request data**
                if (changePasswordRequest == null ||
                    changePasswordRequest.UserId <= 0 ||
                    string.IsNullOrWhiteSpace(changePasswordRequest.CurrentPassword) ||
                    string.IsNullOrWhiteSpace(changePasswordRequest.NewPassword))
                {
                    return BadRequest(new { Message = "Invalid request. Please provide userId, currentPassword, and newPassword." });
                }

                if (changePasswordRequest.NewPassword.Length < 8)
                {
                    return BadRequest(new { Message = "New password must be at least 8 characters long." });
                }

                // **2. Fetch the user from the database**
                var user = await _dbContext.Users.FindAsync(changePasswordRequest.UserId);
                if (user == null)
                {
                    return NotFound(new { Message = "User not found." });
                }

                // **3. Verify the current password using BCrypt**
                if (!BCrypt.Net.BCrypt.Verify(changePasswordRequest.CurrentPassword, user.PasswordHash))
                {
                    return Unauthorized(new { Message = "Current password is incorrect." });
                }

                // **4. Prevent the user from reusing the same password**
                if (BCrypt.Net.BCrypt.Verify(changePasswordRequest.NewPassword, user.PasswordHash))
                {
                    return BadRequest(new { Message = "New password cannot be the same as the current password." });
                }

                // **5. Hash the new password using BCrypt**
                var hashedNewPassword = BCrypt.Net.BCrypt.HashPassword(changePasswordRequest.NewPassword);

                // **6. Update the user's password in the database**
                user.PasswordHash = hashedNewPassword;
                await _dbContext.SaveChangesAsync();

                Console.WriteLine($"User with ID {user.UserId} successfully changed their password.");

                return Ok(new { Message = "Password updated successfully." });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error occurred while changing password: {ex.Message}");
                return StatusCode(500, new { Message = "An error occurred while changing the password.", Details = ex.Message });
            }
        }
    }

    // DTO for handling login requests, including optional location updates.
    public class UserLoginRequest
    {
        public string Email { get; set; }
        public string Password { get; set; }
        public double? Latitude { get; set; }
        public double? Longitude { get; set; }
    }

    // DTO for updating user preferences and other fields in a controlled manner.
    public class UpdateUserPreferencesDto
    {
        public int UserId { get; set; }           // Required field (User identifier)
        public string? Email { get; set; }         // Optional update fields
        public string? FirstName { get; set; }     
        public string? LastName { get; set; }      
        public string? Preferences { get; set; }   
        public string? Dislikes { get; set; }
        public string? PriceRange { get; set; }
        public double? MaxDistance { get; set; }
        public double? Latitude { get; set; }
        public double? Longitude { get; set; }
    }
    
    // DTO for updating the user's password. 
    public class ChangePasswordRequest
    {
        public int UserId { get; set; }
        public string CurrentPassword { get; set; }
        public string NewPassword { get; set; }
    }
}