/* This file defines the AmadeusService, a service responsible for interacting with the Amadeus 
API in the Ventaura application. It fetches activity and event data based on user location, 
processes the API response, and converts the data into a format suitable for integration into the application.
The service also handles authentication by retrieving an access token from Amadeus. */

using System.Net.Http.Headers;
using System.Text;
using ventaura_backend.Models;
using Newtonsoft.Json.Linq;

namespace ventaura_backend.Services
{
    // Service to interact with the Amadeus API for retrieving activity data.
    public class AmadeusService
    {
        private readonly HttpClient _httpClient; // HTTP client for making API requests.
        private readonly IConfiguration _configuration; // Configuration for accessing API keys and secrets.

        // Constructor to initialize the HTTP client and configuration.
        public AmadeusService(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _configuration = configuration;
        }

        // Method to fetch activities from the Amadeus API based on location.
        public async Task<List<UserContent>> FetchAmadeusEventsAsync(double latitude, double longitude, int userId)
        {
            // Retrieve the access token required for API authentication.
            var accessToken = await GetAccessTokenAsync();
            if (string.IsNullOrEmpty(accessToken))
            {
                Console.WriteLine("Access token retrieval failed.");
                return new List<UserContent>();
            }

            // Construct the Amadeus API request URL with latitude and longitude.
            var amadeusUrl = $"https://test.api.amadeus.com/v1/shopping/activities?latitude={latitude}&longitude={longitude}&radius=20";
            var amadeusRequest = new HttpRequestMessage(HttpMethod.Get, amadeusUrl);
            amadeusRequest.Headers.Authorization = new AuthenticationHeaderValue("Bearer", accessToken);

            Console.WriteLine("Constructed API URL: " + amadeusUrl);
            Console.WriteLine("Access Token: " + accessToken);

            // Send the request to the Amadeus API.
            var response = await _httpClient.SendAsync(amadeusRequest);

            Console.WriteLine("Response Status Code: " + response.StatusCode);

            // Read the raw response content.
            var rawResponse = await response.Content.ReadAsStringAsync();

            if (response.IsSuccessStatusCode)
            {
                // Parse the JSON response to extract activities.
                var amadeusJson = JObject.Parse(rawResponse);

                // Map the JSON data to a list of UserContent objects.
                var events = amadeusJson["data"].Select(activity => new UserContent
                {
                    UserId = userId,
                    Title = activity["name"]?.ToString() ?? "Unnamed Tour", // Activity name or default text.
                    Description = activity["description"]?.ToString() ?? "No description available.", // Description or default text.
                    Location = $"{activity["geoCode"]?["latitude"]}, {activity["geoCode"]?["longitude"]}",
                    Start = DateTime.UtcNow, // Placeholder for start date (not provided by Amadeus).
                    Source = "Amadeus", // Source identifier for the data.
                    Type = "Other", // Activity type.
                    CurrencyCode = activity["price"]?["currencyCode"]?.ToString() ?? "N/A", // Currency code or default.
                    Amount = double.TryParse(activity["price"]?["amount"]?.ToString(), out var amount) ? amount : (double?)null,
                    URL = activity["self"]?["href"]?.ToString() ?? "Booking link not available." // Booking link or default text.
                }).ToList() ?? new List<UserContent>();

                Console.WriteLine($"Amadeus events fetched: {events.Count}");
                return events;
            }
            else
            {
                // Log errors if the request fails.
                Console.WriteLine($"Failed to fetch from Amadeus API: {response.StatusCode}");
                return new List<UserContent>();
            }
        }

        // Method to retrieve an access token for authenticating with the Amadeus API.
        private async Task<string> GetAccessTokenAsync()
        {
            // Retrieve API credentials from configuration.
            var clientId = _configuration["Amadeus:ApiKey"];
            var clientSecret = _configuration["Amadeus:ApiSecret"];

            // Prepare the request body for the token endpoint.
            var requestBody = new StringContent(
                $"grant_type=client_credentials&client_id={clientId}&client_secret={clientSecret}",
                Encoding.UTF8,
                "application/x-www-form-urlencoded"
            );

            // Send the token request to Amadeus.
            var tokenResponse = await _httpClient.PostAsync("https://test.api.amadeus.com/v1/security/oauth2/token", requestBody);
            if (tokenResponse.IsSuccessStatusCode)
            {
                // Parse the response and extract the access token.
                var jsonResponse = await tokenResponse.Content.ReadAsStringAsync();

                Console.WriteLine("Token Response JSON: " + jsonResponse);

                var tokenObject = JObject.Parse(jsonResponse);

                if (tokenObject.ContainsKey("access_token"))
                {
                    var token = tokenObject["access_token"]?.ToString();
                    Console.WriteLine("Access Token Retrieved Successfully.");
                    return token;
                }
                else
                {
                    Console.WriteLine("Failed to retrieve access token. 'access_token' not found in response.");
                    return null;
                }
            }
            else
            {
                // Log errors if the token request fails.
                Console.WriteLine("Failed to retrieve access token. Status Code: " + tokenResponse.StatusCode);
                var errorContent = await tokenResponse.Content.ReadAsStringAsync();
                Console.WriteLine("Error Content: " + errorContent);
                return null;
            }
        }
    }
}
