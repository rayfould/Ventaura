using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using System.Collections.Generic;
using EventRanking;

namespace EventRanking
{
    public class EventRankingClient
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;

        public EventRankingClient(string baseUrl = "http://localhost:8000")
        {c
            _httpClient = new HttpClient();
            _baseUrl = baseUrl;
        }

        public async Task<List<int>> RankEventsAsync(User user, List<Event> events)
        {
            try
            {
                var request = new { user, events };
                var response = await _httpClient.PostAsJsonAsync(
                    $"{_baseUrl}/rank-events",
                    request
                );

                if (!response.IsSuccessStatusCode)
                {
                    var error = await response.Content.ReadAsStringAsync();
                    throw new Exception($"API request failed: {error}");
                }

                return await response.Content.ReadFromJsonAsync<List<int>>();
            }
            catch (Exception ex)
            {
                throw new Exception($"Failed to rank events: {ex.Message}", ex);
            }
        }
    }
}
