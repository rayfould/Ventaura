// Services/RankingService.cs
using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json;
using ventaura_backend.Models;

namespace ventaura_backend.Services
{
    public class RankingService
    {
        private readonly HttpClient _client;

        public RankingService(IHttpClientFactory clientFactory)
        {
            _client = clientFactory.CreateClient("RankingAPI");
        }

        // Method to rank the events after fetch endpoint to data is made
        public async Task<RankingResponse> RankEventsForUser(int userId)
        {
            try
            {
                var response = await _client.PostAsync($"rank-events/{userId}", null);
                response.EnsureSuccessStatusCode();
                var content = await response.Content.ReadAsStringAsync();
                var rankingResponse = JsonConvert.DeserializeObject<RankingResponse>(content);
                return rankingResponse;
            }
            catch (Exception ex)
            {
                // Log the exception (consider using a logging framework)
                Console.Error.WriteLine($"RankingService Error: {ex.Message}");
                return new RankingResponse
                {
                    Success = false,
                    Message = "An error occurred while ranking events."
                };
            }
        }
    }
}
