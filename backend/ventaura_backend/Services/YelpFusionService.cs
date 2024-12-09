/* This file defines the YelpFusionService, a service responsible for interacting with the 
Yelp API in the Ventaura application. It fetches event data based on user location, 
processes the API response, and converts the data into a format suitable for use in the application. 
The service allows the app to provide users with personalized event recommendations. */

using System.Net.Http.Headers;
using Newtonsoft.Json.Linq;
using ventaura_backend.Models;

namespace ventaura_backend.Services
{
    // Service to interact with the Ticketmaster API for retrieving event data.
    public class YelpFusionService
    {
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;

        // Constructor to initialize the HTTP client and configuration.

        public YelpFusionService(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _configuration = configuration;
        }

        public async Task<List<UserContent>> FetchYelpEventsAsync(double latitude, double longitude, int userId)
        {
            // Retrieve the API key from the configuration.
            var apiKey = _configuration["Yelp:ApiKey"];

            // Construct the API URL with user location and search radius.
            var url = $"https://api.yelp.com/v3/events?limit=50&sort_by=asc&sort_on=time_start&latitude={latitude}&longitude={longitude}&radius=40000";

            _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", apiKey);
            
            // Receive the response
            var response = await _httpClient.GetAsync(url);

            if (response.IsSuccessStatusCode)
            {
                // Deserialize the JSON respone
                var jsonResponse = await response.Content.ReadAsStringAsync();
                var yelpData = JObject.Parse(jsonResponse);

                // Build the events objects based on model
                var events = yelpData["events"]?.Select(eventItem => new UserContent
                {

                    UserId = userId,
                    Title = eventItem["name"]?.ToString() ?? "Unnamed Event",
                    Description = eventItem["description"]?.ToString() ?? "No description available.",
                    Location = eventItem["location"]?["display_address"] != null
                        ? string.Join(", ", eventItem["location"]["display_address"])
                        : "Location not available.",
                    Start = DateTime.TryParse(eventItem["time_start"]?.ToString(), out var timeStart)
                        ? timeStart
                        : DateTime.UtcNow,
                    Source = "Yelp",
                    Type = eventItem["category"]?.ToString() ?? "Other",
                    Amount = eventItem["cost"] != null 
                        ? (decimal?)Convert.ToDecimal(eventItem["cost"]) 
                        : null,
                    CurrencyCode = "USD", // Yelp API doesn't specify currency.
                    URL = eventItem["event_site_url"]?.ToString() ?? "No URL available"

                }).ToList() ?? new List<UserContent>();

                Console.WriteLine($"Fetched {events.Count} events from Yelp.");
                return events;
            }

            Console.WriteLine($"Failed to fetch events from Yelp. Status Code: {response.StatusCode}");
            return new List<UserContent>();
        }
    }
}
