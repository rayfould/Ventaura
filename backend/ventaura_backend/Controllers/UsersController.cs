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
        public async Task<IActionResult> CreateAccount([FromBody] User user)
        {
            try
            {
                // Validate that all required fields are provided by the user.
                if (string.IsNullOrEmpty(user.Email) ||
                    string.IsNullOrEmpty(user.FirstName) ||
                    string.IsNullOrEmpty(user.LastName) ||
                    user.Latitude == 0 ||
                    user.Longitude == 0 ||
                    string.IsNullOrEmpty(user.Preferences) ||
                    string.IsNullOrEmpty(user.PriceRange) ||
                    string.IsNullOrEmpty(user.CrowdSize) ||
                    string.IsNullOrEmpty(user.PasswordHash))
                {
                    return BadRequest(new { Message = "All fields are required to create an account." });
                }

                // Check if the email is already registered in the database.
                var existingUser = await _dbContext.Users.FirstOrDefaultAsync(u => u.Email == user.Email);
                if (existingUser != null)
                {
                    return Conflict(new { Message = "An account with this email already exists. Please log in or use a different email." });
                }

                // Securely hash the user's password before storing it.
                user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(user.PasswordHash);
                user.CreatedAt = DateTime.UtcNow;

                // Add the new user to the database.
                _dbContext.Users.Add(user);
                await _dbContext.SaveChangesAsync();

                // Log success and return a success response.
                Console.WriteLine($"Account created successfully for Email: {user.Email}");
                return Ok(new { Message = "Account created successfully!", userId = user.UserId });
            }
            catch (Exception ex)
            {
                // Log and return server error for unexpected issues.
                Console.WriteLine($"Error in CreateAccount: {ex.Message}");
                return StatusCode(500, new { Message = "An error occurred while creating the account. Please try again later." });
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
