using Microsoft.AspNetCore.Http;
using System.Threading.Tasks;

public class InactivityMiddleware
{
    private readonly RequestDelegate _next;

    public InactivityMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Logic to track user inactivity and logout if needed
        // You can track user activity by updating a timestamp in session or database
        /* Note: Add actual inactivity tracking logic within InvokeAsync. For instance, 
        you might store a timestamp in a user’s session or database record and compare 
        it with the current time to check for inactivity.*/

        await _next(context);
    }
}
