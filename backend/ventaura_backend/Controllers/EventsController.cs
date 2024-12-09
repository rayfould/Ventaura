/* This file defines a controller responsible for handling event ranking functionality for users.
It exposes an endpoint that, given a user ID, triggers the ranking of events based on certain criteria,
and returns the result of that operation. The actual logic for ranking is delegated to the RankingService. */

using Microsoft.AspNetCore.Mvc;
using ventaura_backend.Services;

namespace ventaura_backend.Controllers
{
    // Indicates that this class is an API controller and sets the routing template to "api/[controller]".
    // The actual route will replace [controller] with "events", resulting in "api/events".
    [ApiController]
    [Route("api/[controller]")]
    public class EventsController : ControllerBase
    {
        // A service that handles the logic for ranking events for a given user.
        private readonly RankingService _rankingService;

        // Constructor that receives the RankingService via dependency injection
        // and assigns it to a private field for use within the controller's endpoints.
        public EventsController(RankingService rankingService)
        {
            _rankingService = rankingService;
        }

        // POST endpoint: Ranks events for a specified user.
        // The {userId} parameter is extracted from the route and passed to the service method.
        [HttpPost("rank/{userId}")]
        public async Task<IActionResult> RankEvents(int userId)
        {
            var rankingResponse = await _rankingService.RankEventsForUser(userId);

            if (!rankingResponse.Success)
                return BadRequest(rankingResponse); // Returns the JSON object with success: false

            return Ok(rankingResponse); // Returns the JSON object with success: true
        }
    }
}