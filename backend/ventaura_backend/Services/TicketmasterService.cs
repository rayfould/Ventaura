/* This file defines the TicketmasterService, a service responsible for interacting with the 
Ticketmaster API in the Ventaura application. It fetches event data based on user location, 
processes the API response, and converts the data into a format suitable for use in the application. 
The service allows the app to provide users with personalized event recommendations. */

using ventaura_backend.Models;

namespace ventaura_backend.Services
{
    // Service to interact with the Ticketmaster API for retrieving event data.
    public class TicketmasterService
    {
        private readonly HttpClient _httpClient; // HTTP client for making API requests.
        private readonly IConfiguration _configuration; // Configuration for accessing API keys.

        // Constructor to initialize the HTTP client and configuration.
        public TicketmasterService(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _configuration = configuration;
        }

        // Method to fetch events from the Ticketmaster API based on location.
        public async Task<List<UserContent>> FetchTicketmasterEventsAsync(double latitude, double longitude, int userId)
        {
            // Retrieve the API key from the configuration.
            var apiKey = _configuration["Ticketmaster:ApiKey"];

            // Construct the API URL with user location and search radius.
            var apiUrl = $"https://app.ticketmaster.com/discovery/v2/events.json?apikey={apiKey}&latlong={latitude},{longitude}&radius=20";

            Console.WriteLine("Ticketmaster API URL: " + apiUrl);

            // Send a GET request to the Ticketmaster API.
            var response = await _httpClient.GetAsync(apiUrl);

            if (response.IsSuccessStatusCode)
            {
                // Deserialize the API response into the TicketmasterResponseModel.
                var apiData = await response.Content.ReadFromJsonAsync<TicketmasterResponseModel>();

                // Map the API response to a list of UserContent objects.
                var events = apiData?._embedded?.Events?.Select(eventItem => new UserContent
                {
                    UserId = userId,
                    Title = eventItem.Name, // Event title.
                    Description = eventItem.Type ?? "No description available", // Event type or default text.
                    Location = eventItem._embedded?.Venues?.FirstOrDefault()?.Location != null
                        ? $"{eventItem._embedded.Venues.First().Location.Latitude}, {eventItem._embedded.Venues.First().Location.Longitude}" // Combine latitude and longitude.
                        : "Location not available", // Default text if location is missing.
                    Start = eventItem.Start?.LocalDate ?? DateTime.UtcNow, // Event start date or current time as fallback.
                    Source = "Ticketmaster", // Source identifier for the data.
                    Type = eventItem.Classifications?.FirstOrDefault()?.Genre?.Name, // Event genre.
                    URL = eventItem.URL // Event URL for more details.
                }).ToList() ?? new List<UserContent>();

                Console.WriteLine($"Ticketmaster events fetched: {events.Count}");
                return events;
            }
            else
            {
                // Log errors if the request fails.
                Console.WriteLine($"Failed to fetch from Ticketmaster API: {response.StatusCode}");
                return new List<UserContent>();
            }
        }
    }
}
