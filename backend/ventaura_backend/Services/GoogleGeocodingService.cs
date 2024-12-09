using ventaura_backend.Models;
using System.Text.Json;
using System.Text.Json.Serialization;

// not necessary for the FOR YOU view
namespace ventaura_backend.Services
{
    // Service to fetch coordinates using Google Geocoding API
    public class GoogleGeocodingService
    {
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;

        public GoogleGeocodingService(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _configuration = configuration;
        }

        // Method to get formatted address from coordinates (latitude, longitude)
        public async Task<string> GetAddressFromCoordinates(double latitude, double longitude)
        {
            try
            {
                var apiKey = _configuration["Google:ApiKey"];
                var requestUrl = $"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={apiKey}";

                var response = await _httpClient.GetAsync(requestUrl);
                if (!response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Geocoding request failed with status {response.StatusCode}");
                    return "Unknown Address";
                }

                var jsonResponse = await response.Content.ReadAsStringAsync();
                Console.WriteLine($"Google Geocoding API Response: {jsonResponse}");

                var data = JsonSerializer.Deserialize<GeocodeResponse>(jsonResponse);
                
                if (data == null || data.Results == null || !data.Results.Any())
                {
                    // Console.WriteLine($"No results found for coordinates: {latitude}, {longitude}");
                    return "Unknown Address";
                }

                // Get the first result's formatted address
                var formattedAddress = data.Results.FirstOrDefault()?.FormattedAddress;

                if (!string.IsNullOrEmpty(formattedAddress))
                {
                    // Console.WriteLine($"Formatted Address: {formattedAddress}");
                    return formattedAddress;
                }
                else
                {
                    // Console.WriteLine($"No address found for coordinates: {latitude}, {longitude}");
                    return "Unknown Address";
                }
            }
            catch (Exception ex)
            {
                // Console.WriteLine($"Error occurred while fetching address from coordinates: {ex.Message}");
                return "Unknown Address";
            }
        }

        // Method to get coordinates based on a location string
        public async Task<(double latitude, double longitude)?> GetCoordinatesAsync(string location)
        {
            var apiKey = _configuration["Google:ApiKey"];
            var requestUrl = $"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={apiKey}";
            var response = await _httpClient.GetAsync(requestUrl);

            if (response.IsSuccessStatusCode)
            {
                var data = await response.Content.ReadFromJsonAsync<GeocodeResponse>();
                var coordinates = data.Results.FirstOrDefault()?.Geometry.Location;
                return coordinates != null ? (coordinates.Lat, coordinates.Lng) : null;
            }

            return null;
        }
    }
}
