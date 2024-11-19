// EventModels.cs
using System.Text.Json.Serialization;

namespace EventRanking
{
    public class User
    {
        [JsonPropertyName("user_id")]
        public int UserId { get; set; }

        [JsonPropertyName("preferred_events")]
        public List<string> PreferredEvents { get; set; }

        [JsonPropertyName("undesirable_events")]
        public List<string> UndesirableEvents { get; set; }

        [JsonPropertyName("latitude")]
        public double Latitude { get; set; }

        [JsonPropertyName("longitude")]
        public double Longitude { get; set; }

        [JsonPropertyName("max_distance")]
        public double MaxDistance { get; set; }

        [JsonPropertyName("price_range")]
        public string PriceRange { get; set; }

        [JsonPropertyName("preferred_crowd_size")]
        public string PreferredCrowdSize { get; set; }

        [JsonPropertyName("age")]
        public int Age { get; set; }
    }

    public class Event
    {

        // Original fields needed for the algorithm (derived from new structure)
        [JsonPropertyName("event_id")]
        public int EventId => ContentId;  // Map from ContentId

        [JsonPropertyName("event_type")]
        public string EventType => Type;   // Map from Type


        [JsonPropertyName("date_time")]
        public string DateTime => Start;    // Map from Start

        [JsonPropertyName("price")]
        public double Price => double.TryParse(Amount, out double result) ? result : 0.0;  // Map from Amount

        // New structure fields
        [JsonPropertyName("contentId")]
        public int ContentId { get; set; }

        [JsonPropertyName("title")]
        public string Title { get; set; }

        [JsonPropertyName("description")]
        public string Description { get; set; }

        [JsonPropertyName("location")]
        public string Location { get; set; }

        [JsonPropertyName("start")]
        public string Start { get; set; }

        [JsonPropertyName("source")]
        public string Source { get; set; }

        [JsonPropertyName("type")]
        public string Type { get; set; }

        [JsonPropertyName("currencyCode")]
        public string CurrencyCode { get; set; }

        [JsonPropertyName("amount")]
        public string Amount { get; set; }

        [JsonPropertyName("url")]
        public string Url { get; set; }

        [JsonPropertyName("distance")]
        public double Distance { get; set; }

    }

    public class RankedEvent : Event
    {
        [JsonPropertyName("rank")]
        public int Rank { get; set; }

        [JsonPropertyName("q_value")]
        public double QValue { get; set; }
    }
}
