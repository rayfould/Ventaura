/* This file defines the User model, representing the structure of the Users table in the 
Ventaura application's database. It stores user information, including personal details, 
preferences, and authentication data, to facilitate personalized recommendations and secure account management. */

namespace ventaura_backend.Models
{
    public class User
    {
        public int UserId { get; set; } // Maps to "userid" column
        public string Email { get; set; } // Maps to "email" column
        public string FirstName { get; set; } // Maps to "firstname" column
        public string LastName { get; set; } // Maps to "lastname" column
        public string PasswordHash { get; set; } // Maps to "passwordhash" column
        public string PasswordPlain { get; set; } // Maps to "passwordPlain" column
        public double? Latitude { get; set; } // Maps to "latitude" column (nullable)
        public double? Longitude { get; set; } // Maps to "longitude" column (nullable)
        public string Preferences { get; set; } // Maps to "preferences" column (nullable)
        public string Dislikes { get; set; } // Maps to "dislikes" column (nullable)
        public string PriceRange { get; set; } // Maps to "pricerange" column (nullable)
        public double? MaxDistance { get; set; } // Maps to "maxdistance" column (nullable)
        public bool IsLoggedIn { get; set; } = false; // Maps to "isloggedin" column with default value
    }
}
