using System;
using System.Net.Http;
using System.Threading.Tasks;

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

        /// <summary>
        /// Demonstrates how to use the Event Ranking API
        /// </summary>
        public async Task RunDemo()
        {
            Console.WriteLine("Event Ranking API Demo");
            Console.WriteLine("======================");
            
            // STEP 1: Setup
            Console.WriteLine("\nSTEP 1: Ensure the FastAPI server is running on localhost:8000");
            Console.WriteLine("If not running, start it with: uvicorn main:app --reload");
            
            // STEP 2: Rank Events
            Console.WriteLine("\nSTEP 2: Ranking events for a specific user");
            Console.WriteLine("This will load the user's events from their CSV file, rank them, and save the results");
            
            // Demo with a specific user ID
            int userId = 42; // Replace with an actual user ID from your generated files
            var result = await RankEventsForUser(userId);
            
            // STEP 3: Show how to integrate
            Console.WriteLine("\nSTEP 3: Integration Guide");
            Console.WriteLine("To integrate this into your own code:");
            Console.WriteLine("1. Copy the RankEventsForUser method");
            Console.WriteLine("2. Call it with your user's ID");
            Console.WriteLine("3. Handle the response as needed");
            
            Console.WriteLine("\nExample Integration Code:");
            Console.WriteLine(@"
    // Example usage in your code:
    using System.Net.Http;
    
    public class YourClass 
    {
        private readonly HttpClient _client = new HttpClient();
        
        public async Task RankUserEvents(int userId)
        {
            var response = await _client.PostAsync(
                $""http://localhost:8000/rank-events/{userId}"",
                null);
                
            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadAsStringAsync();
                // Handle successful response
            }
            else
            {
                // Handle error
            }
        }
    }");
        }

        /// <summary>
        /// Ranks events for a specific user
        /// </summary>
        /// <param name="userId">The ID of the user whose events need ranking</param>
        /// <returns>The ranking results or error message</returns>
        public async Task<string> RankEventsForUser(int userId)
        {
            try
            {
                Console.WriteLine($"\nRanking events for user {userId}...");
                
                var response = await _client.PostAsync(
                    $"/rank-events/{userId}",
                    null);

                var result = await response.Content.ReadAsStringAsync();
                
                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine("Ranking successful!");
                    Console.WriteLine($"Response: {result}");
                    return result;
                }
                else
                {
                    Console.WriteLine($"Error: {response.StatusCode} - {response.ReasonPhrase}");
                    Console.WriteLine($"Details: {result}");
                    return $"Error: {result}";
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exception occurred: {ex.Message}");
                return $"Error: {ex.Message}";
            }
        }
    }

    // Demo program to run the example
    class Program
    {
        static async Task Main(string[] args)
        {
            var demo = new EventRankingDemo();
            await demo.RunDemo();
            
            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}
