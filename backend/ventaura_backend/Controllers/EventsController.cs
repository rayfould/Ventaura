using Microsoft.AspNetCore.Mvc;
using ventaura_backend.Services;

namespace ventaura_backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class EventsController : ControllerBase  // Note: ControllerBase, not Controller
    {
        private readonly RankingService _rankingService;

        public EventsController(RankingService rankingService)
        {
            _rankingService = rankingService;
        }

        [HttpPost("rank/{userId}")]
        public async Task<IActionResult> RankEvents(int userId)
        {
            var success = await _rankingService.RankEventsForUser(userId);
            if (!success)
                return BadRequest("Failed to rank events");
                
            return Ok("Events ranked successfully");
        }
    }
}
