/* This file defines the User model, representing the structure of the Users table in the 
Ventaura application's database. It stores user information, including personal details, 
preferences, and authentication data, to facilitate personalized recommendations and secure account management. */

namespace ventaura_backend.Models
{
    // Represents a user in the Ventaura application.
    public class User
    {
        public int UserId { get; set; }  // Primary key for identifying each user.
        public string Email { get; set; }  // User's email address for account identification and login.
        public string FirstName { get; set; }  // User's first name.
        public string LastName { get; set; }  // User's last name.
        public double Latitude { get; set; }  // Latitude of the user's location for personalized content.
        public double Longitude { get; set; }  // Longitude of the user's location for personalized content.
        public string Preferences { get; set; } // User's preferences for event recommendations (e.g., "Music, Sports").
        public string PriceRange { get; set; } // User's selected price range for events (e.g., "$0-$50").
        public string CrowdSize { get; set; } // User's preferred crowd size for events (e.g., "Small", "Medium").
        public DateTime CreatedAt { get; set; } = DateTime.Now;  // Timestamp of when the user account was created.
        public string PasswordHash { get; set; } // Securely hashed password for authentication.
        public bool IsLoggedIn { get; set; } = false; // Indicates if the user is currently logged in.
    }
}
