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
                var events = apiData?._embedded?.Events?.Select(eventItem =>
                {
                    // Set a default fallback start date if no date is provided.
                    DateTime startDate = DateTime.UtcNow;

                    if (eventItem.Dates?.Start?.LocalDate.HasValue == true)
                    {
                        startDate = eventItem.Dates.Start.LocalDate.Value;

                        // Check if time is available and not TBA
                        bool timeTBA = eventItem.Dates.Start.TimeTBA;
                        string localTime = eventItem.Dates.Start.LocalTime;

                        if (!timeTBA && !string.IsNullOrEmpty(localTime))
                        {
                            // Attempt to parse the local time, usually "HH:mm:ss"
                            if (TimeSpan.TryParse(localTime, out var timeSpan))
                            {
                                // Combine the date and the parsed time
                                startDate = startDate.Date + timeSpan;
                            }
                        }
                    }

                    return new UserContent
                    {
                        UserId = userId,
                        Title = eventItem.Name,
                        Description = eventItem.Type ?? "No description available",
                        Location = eventItem._embedded?.Venues?.FirstOrDefault()?.Location != null
                            ? $"{eventItem._embedded.Venues.First().Location.Latitude}, {eventItem._embedded.Venues.First().Location.Longitude}"
                            : "Location not available",
                        Start = startDate,
                        Source = "Ticketmaster",
                        Type = eventItem.Classifications?.FirstOrDefault()?.Genre?.Name,
                        URL = eventItem.URL
                    };
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
