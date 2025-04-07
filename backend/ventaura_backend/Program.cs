/* 
This file is the main entry point for the Ventaura application's backend, responsible for initializing 
the web server, configuring services, middleware, and routing. It integrates the database, sets up 
API services for external data fetches, defines CORS policies for frontend-backend communication, 
and configures development tools like Swagger for API documentation. Additionally, it includes 
integration with Stripe for payment handling, serving static files, and handling checkout sessions. 
Once everything is configured, it runs the application.
*/

using Microsoft.EntityFrameworkCore;
using ventaura_backend.Data; // For DatabaseContext 
using ventaura_backend.Services; // For TicketmasterService, AmadeusService, and CombinedAPIService
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Options;
using Stripe;
using Stripe.Checkout;
using System.IO;

// Loads environment variables from .env (used for Stripe keys, etc.)
// Disable for prod, enable for dev
//DotNetEnv.Env.Load();

var builder = WebApplication.CreateBuilder(new WebApplicationOptions
{
    Args = args,
    WebRootPath = "wwwroot" // Optional, for later static files
});
builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(80); 
});

// Configure Stripe options by loading environment variables.
builder.Services.Configure<StripeOptions>(options =>
{
    options.PublishableKey = Environment.GetEnvironmentVariable("STRIPE_PUBLISHABLE_KEY");
    options.SecretKey = Environment.GetEnvironmentVariable("STRIPE_SECRET_KEY");
    options.WebhookSecret = Environment.GetEnvironmentVariable("STRIPE_WEBHOOK_SECRET");
    options.Price = Environment.GetEnvironmentVariable("PRICE");
    options.Domain = Environment.GetEnvironmentVariable("DOMAIN");
});

// Add controllers to the service container, enabling the use of MVC/Web API endpoints.
builder.Services.AddControllers();

// Register the DatabaseContext with a connection string, including retry logic for transient failures.
builder.Services.AddDbContext<DatabaseContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection"), options =>
        options.EnableRetryOnFailure(
            maxRetryCount: 5,
            maxRetryDelay: TimeSpan.FromSeconds(10),
            errorCodesToAdd: null)));

// Register application services for dependency injection:
// - TicketmasterService and AmadeusService handle external event data retrieval.
// - CombinedAPIService merges various event sources into a unified view.
builder.Services.AddScoped<TicketmasterService>();
builder.Services.AddScoped<YelpFusionService>();
builder.Services.AddScoped<AmadeusService>();
builder.Services.AddScoped<CombinedAPIService>(sp => 
    new CombinedAPIService(
        sp.GetRequiredService<TicketmasterService>(),
        sp.GetRequiredService<YelpFusionService>(),
        sp.GetRequiredService<DatabaseContext>(),
        sp.GetRequiredService<GoogleGeocodingService>()
    )
);

// Add a general CORS policy allowing any origin, method, and header.
// This broad policy is useful for development and may be restricted in production.
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Register HttpClient and named HttpClients to facilitate external API calls.
// This includes GoogleGeocodingService and YelpFusionService for geocoding and Yelp data retrieval.
builder.Services.AddHttpClient();
builder.Services.AddHttpClient<GoogleGeocodingService>();
builder.Services.AddHttpClient<YelpFusionService>();

// Add SessionTimeoutService as a hosted service
builder.Services.AddHostedService<SessionTimeoutService>();

// Enable Swagger for API documentation and interactive testing of endpoints.
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Register a named HttpClient for the RankingAPI with a specified base address.
builder.Services.AddHttpClient("RankingAPI", client =>
{
    client.BaseAddress = new Uri("https://ventaura-ranking-rayfould.fly.dev");
});

// Register the RankingService for event ranking logic.
builder.Services.AddScoped<RankingService>();


var app = builder.Build();

// Use the general "AllowAll" CORS policy defined earlier.
app.UseCors("AllowAll");

// Configure Stripe with the secret key from environment variables.
StripeConfiguration.ApiKey = Environment.GetEnvironmentVariable("STRIPE_SECRET_KEY");

// Retrieve the price from environment variables for use in Stripe sessions.
var price = Environment.GetEnvironmentVariable("PRICE");

// In development, show detailed error pages.
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

// Also in development, use Swagger and its UI for testing API endpoints.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// The following code handles Stripe integration and static file serving.
// It serves static files from a directory specified by the STATIC_DIR environment variable.
// app.UseStaticFiles(new StaticFileOptions()
// {
//     FileProvider = new PhysicalFileProvider(
//         Path.Combine(Directory.GetCurrentDirectory(),
//         Environment.GetEnvironmentVariable("STATIC_DIR"))
//     ),
//     RequestPath = new PathString("")
// });

// Define a GET endpoint to redirect the root ("/") to "index.html".
app.MapGet("/", () => Results.Redirect("index.html"));

// Retrieve details of a Stripe checkout session by ID.
app.MapGet("checkout-session", async (string sessionId) =>
{
    var service = new SessionService();
    var session = await service.GetAsync(sessionId);
    return Results.Ok(session);
});

// Create a new Stripe checkout session using parameters set in StripeOptions.
app.MapPost("/api/create-checkout-session", async (IOptions<StripeOptions> options, HttpContext context) =>
{
    var sessionOptions = new SessionCreateOptions
    {
        SuccessUrl = $"{options.Value.Domain}/success.html?session_id={{CHECKOUT_SESSION_ID}}",
        CancelUrl = $"{options.Value.Domain}/canceled.html",
        Mode = "payment",
        LineItems = new List<SessionLineItemOptions>
        {
            new SessionLineItemOptions
            {
                Quantity = 1,
                Price = options.Value.Price,
            },
        },
    };

    var service = new SessionService();
    var session = await service.CreateAsync(sessionOptions);
    context.Response.Headers.Add("Location", session.Url);
    return Results.StatusCode(303); // Redirect to the Stripe hosted checkout page.
});

// Use the React-specific CORS policy if needed.
app.UseCors("AllowReactApp");

// Enable endpoint routing and authorization middleware.
app.UseRouting();
app.UseAuthorization();

// Map the controllers defined in the application to routes.
app.MapControllers();

// Start the application and listen for incoming requests.
app.Run();