using ventaura_backend.Models;

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
