using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text.Json;

namespace RankingAPIDemo
{
    public class EventRankingDemo
    {
        private readonly HttpClient _client;
        private const string API_BASE_URL = "http://localhost:8000";

        public EventRankingDemo()
        {
            _client = new HttpClient();
            _client.BaseAddress = new Uri(API_BASE_URL);
        }

        public async Task<bool> RankEventsForUser(int userId)
{
    try
    {
        Console.WriteLine($"\n=== Starting API call for user {userId} ===");
        
        Console.WriteLine("Making POST request...");
        var url = $"rank-events/{userId}";
        Console.WriteLine($"Calling URL: {_client.BaseAddress}{url}");
        
        var response = await _client.PostAsync(url, null);  // Use the url variable here
        
        Console.WriteLine($"Response status: {response.StatusCode}");
        var result = await response.Content.ReadAsStringAsync();
        Console.WriteLine($"Raw response: {result}");
        
        try
        {
            response.EnsureSuccessStatusCode();  // Call it on response, not result
        }
        catch (HttpRequestException ex)
        {
            Console.WriteLine($"HTTP Request failed: {ex.Message}");
            Console.WriteLine($"Status code: {response.StatusCode}");
            Console.WriteLine($"Content: {result}");
            return false;
        }

        if (response.IsSuccessStatusCode)
        {
            var apiResponse = JsonSerializer.Deserialize<ApiResponse>(result);
            Console.WriteLine($"Deserialized response: {apiResponse?.Message}");

            string csvPath = Path.Combine("E:", "Documents", "GitHub", "Ventaura", 
                "backend", "Ranking", "API", "content", $"{userId}.csv");
            Console.WriteLine($"Checking for CSV at: {csvPath}");
            
            if (File.Exists(csvPath))
            {
                Console.WriteLine($"CSV file found at: {csvPath}");
            }
            else
            {
                Console.WriteLine($"WARNING: CSV file not found at: {csvPath}");
            }

            return true;
        }
        else
        {
            Console.WriteLine($"Error response: {response.StatusCode} - {response.ReasonPhrase}");
            Console.WriteLine($"Error details: {result}");
            return false;
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Exception type: {ex.GetType().Name}");
        Console.WriteLine($"Exception message: {ex.Message}");
        Console.WriteLine($"Stack trace:\n{ex.StackTrace}");
        return false;
    }


    }

    public class ApiResponse
    {
        public string Status { get; set; }
        public string Message { get; set; }
        public int UserId { get; set; }
    }

    // Demo program
    class Program
    {
        static async Task Main(string[] args)
        {
            var demo = new EventRankingDemo();

            // Test with a specific user ID
            bool success = await demo.RankEventsForUser(96);

            Console.WriteLine($"\nRanking process {(success ? "succeeded" : "failed")}");
            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}

}