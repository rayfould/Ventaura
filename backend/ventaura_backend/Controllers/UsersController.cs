/* This file defines the UsersController for managing user-related operations in the 
Ventaura application. It provides endpoints for user account creation, authentication, 
and retrieval, ensuring secure password storage and dynamic location updates during login. 
The controller facilitates user onboarding and access to personalized event recommendations 
while maintaining robust error handling and validation. */

using Microsoft.AspNetCore.Mvc;
using ventaura_backend.Data;
using ventaura_backend.Models;
using Microsoft.EntityFrameworkCore;
using BCrypt.Net;
using Npgsql;

namespace ventaura_backend.Controllers
{
    // Marks this class as an API controller and sets the route prefix for all user-related endpoints.
    [ApiController]
    [Route("api/users")]
    public class UsersController : ControllerBase
    {
        private readonly DatabaseContext _dbContext;

        // Constructor to inject the database context for accessing user data.
        public UsersController(DatabaseContext dbContext)
        {
            _dbContext = dbContext;
        }

        // Endpoint to create a new user account.
        [HttpPost("create-account")]
        public async Task<IActionResult> CreateAccount([FromBody] User newUser)
        {
            try
            {
                Console.WriteLine("Start CreateAccount process...");

                // Validate input model
                if (!ModelState.IsValid)
                {
                    Console.WriteLine("Validation failed: Missing required fields.");
                    return BadRequest(ModelState);
                }

                // Check if email already exists
                Console.WriteLine($"Checking if email {newUser.Email} already exists...");
                var existingUser = await _dbContext.Users.AsNoTracking()
                    .FirstOrDefaultAsync(u => u.Email == newUser.Email);

                if (existingUser != null)
                {
                    Console.WriteLine($"Email {newUser.Email} already exists.");
                    return Conflict("An account with this email already exists.");
                }

                // Prepare new user object
                var user = new User
                {
                    Email = newUser.Email,
                    FirstName = newUser.FirstName,
                    LastName = newUser.LastName,
                    PasswordHash = BCrypt.Net.BCrypt.HashPassword(newUser.PasswordHash), // Ensure secure hashing
                    Latitude = newUser.Latitude,
                    Longitude = newUser.Longitude,
                    Preferences = newUser.Preferences,
                    Dislikes = newUser.Dislikes,
                    PriceRange = newUser.PriceRange,
                    MaxDistance = newUser.MaxDistance,
                    IsLoggedIn = false
                };

                Console.WriteLine("Adding user to database...");

                // Retry mechanism for transient failures
                var executionStrategy = _dbContext.Database.CreateExecutionStrategy();
                await executionStrategy.ExecuteAsync(async () =>
                {
                    await _dbContext.Users.AddAsync(user);
                    await _dbContext.SaveChangesAsync();
                });

                Console.WriteLine("User successfully created in database.");

                return Ok(new { Message = "Account created successfully.", UserId = user.UserId });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                return StatusCode(500, "An unexpected error occurred.");
            }
        }

        // Endpoint to retrieve a user's details by ID.
        [HttpGet("{id}")]
        public async Task<IActionResult> GetUser(int id)
        {
             // Fetch the user from the database by their ID.
            var user = await _dbContext.Users.FindAsync(id);
            if (user == null)
            {
                return NotFound("User not found.");
            }

            return Ok(user);
        }

        // Endpoint to handle user login.
        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] UserLoginRequest loginRequest)
        {
            try
            {
                // Check if a user with the provided email exists in the database.
                var user = await _dbContext.Users.FirstOrDefaultAsync(u => u.Email == loginRequest.Email);

                // Validate the user's password using bcrypt.
                if (user == null || !BCrypt.Net.BCrypt.Verify(loginRequest.Password, user.PasswordHash))
                {
                    Console.WriteLine($"Invalid login attempt for email {loginRequest.Email}.");
                    return BadRequest(new { Message = "Invalid email or password." });
                }

                // Update the user's live location coordinates upon successful login.
                user.Latitude = loginRequest.Latitude;
                user.Longitude = loginRequest.Longitude;

                // Mark the user as logged in.
                user.IsLoggedIn = true;
                await _dbContext.SaveChangesAsync();

                Console.WriteLine($"User {user.Email} logged in successfully and location updated.");

                // Redirect the user to fetch combined events after login.
                // return Redirect($"/api/combined-events/fetch?userId={user.UserId}");
                // Return a success response with userId
                return Ok(new { Message = "Login successful!", userId = user.UserId });
            }
            catch (Exception ex)
            {
                // Log and return server error for unexpected issues.
                Console.WriteLine($"Error logging in user: {ex.Message}");
                return StatusCode(500, "An error occurred while logging in.");
            }
        }
    }

    // Data Transfer Object (DTO) to handle login request details.
    public class UserLoginRequest
    {
        public string Email { get; set; }
        public string Password { get; set; }
        public double Latitude { get; set; }
        public double Longitude { get; set; }
    }

}