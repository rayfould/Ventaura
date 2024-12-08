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

namespace ventaura_backend.Controllers
{
    // Indicates that this class is an API controller and routes are prefixed with "api/users".
    [ApiController]
    [Route("api/users")]
    public class UsersController : ControllerBase
    {
        // Database context for accessing and manipulating user records.
        private readonly DatabaseContext _dbContext;

        // Constructor injecting the database context dependency for data operations.
        public UsersController(DatabaseContext dbContext)
        {
            _dbContext = dbContext;
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
                            PasswordHash = BCrypt.Net.BCrypt.HashPassword(newUser.PasswordHash), // Secure hashing
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

                // Retrieve the user by email to verify credentials.
                var user = await _dbContext.Users.FirstOrDefaultAsync(u => u.Email == loginRequest.Email);

                // Check if user exists and verify password using bcrypt.
                if (user == null || !BCrypt.Net.BCrypt.Verify(loginRequest.Password, user.PasswordHash))
                {
                    Console.WriteLine($"Invalid login attempt for email {loginRequest.Email}.");
                    return BadRequest(new { Message = "Invalid email or password." });
                }

                if (user == null)
                {
                    // This check is theoretically redundant, but left in case of unexpected null states.
                    Console.WriteLine($"User unexpectedly null during re-fetch: {loginRequest.Email}");
                    return StatusCode(500, "An error occurred during login.");
                }

                // If location is provided in the login request, update it for the user.
                if (loginRequest.Latitude.HasValue && loginRequest.Longitude.HasValue)
                {
                    Console.WriteLine($"Updating location for user {user.Email}: ({loginRequest.Latitude}, {loginRequest.Longitude})");
                    user.Latitude = loginRequest.Latitude.Value;
                    user.Longitude = loginRequest.Longitude.Value;
                }

                // Mark the user as logged in.
                user.IsLoggedIn = true;

                // Save changes to the database.
                await _dbContext.SaveChangesAsync();

                Console.WriteLine($"User {user.Email} logged in successfully and location updated.");

                // Return success response with the user's ID. 
                return Ok(new { Message = "Login successful!", userId = user.UserId });
            }
            catch (Exception ex)
            {
                // Handle unexpected login errors.
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

                // Save the updated user information to the database.
                _dbContext.Users.Update(user);
                await _dbContext.SaveChangesAsync();

                Console.WriteLine("User preferences updated successfully.");

                // Return a success message.
                return Ok(new { Message = "User preferences updated successfully." });
            }
            catch (Exception ex)
            {
                // Handle unexpected errors during preference updates.
                Console.WriteLine($"Error in UpdateUserPreferences: {ex.Message}");
                return StatusCode(500, "An error occurred while updating user preferences.");
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
}