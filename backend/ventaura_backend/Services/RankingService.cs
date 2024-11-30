namespace ventaura_backend.Services
{
    public class RankingService
    {
        private readonly HttpClient _client;

        public RankingService(IHttpClientFactory clientFactory)
        {
            _client = clientFactory.CreateClient("RankingAPI");
        }

        public async Task<bool> RankEventsForUser(int userId)
        {
            try
            {
                var response = await _client.PostAsync($"rank-events/{userId}", null);
                response.EnsureSuccessStatusCode();
                return true;
            }
            catch (Exception ex)
            {
                // Log error
                return false;
            }
        }
    }
}
