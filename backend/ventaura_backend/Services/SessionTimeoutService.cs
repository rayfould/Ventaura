using Microsoft.EntityFrameworkCore;
using ventaura_backend.Data;

namespace ventaura_backend.Services
{
    public class SessionTimeoutService : BackgroundService
    {
        private readonly IServiceProvider _serviceProvider;
        private readonly TimeSpan _timeout = TimeSpan.FromMinutes(60);
        private readonly TimeSpan _checkInterval = TimeSpan.FromMinutes(30);

        public SessionTimeoutService(IServiceProvider serviceProvider)
        {
            _serviceProvider = serviceProvider;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            while (!stoppingToken.IsCancellationRequested)
            {
                await CheckForInactiveUsers(stoppingToken);
                await Task.Delay(_checkInterval, stoppingToken);
            }
        }

        private async Task CheckForInactiveUsers(CancellationToken stoppingToken)
        {
            try
            {
                using (var scope = _serviceProvider.CreateScope())
                {
                    var dbContext = scope.ServiceProvider.GetRequiredService<DatabaseContext>();
                    var now = DateTime.UtcNow;

                    // Find users who are logged in and inactive for more than 30 minutes
                    var inactiveUsers = await dbContext.Users
                        .Where(u => u.IsLoggedIn && (now - u.LastActivity) > _timeout)
                        .ToListAsync(stoppingToken);

                    foreach (var user in inactiveUsers)
                    {
                        Console.WriteLine($"Logging out inactive user {user.UserId} (last activity: {user.LastActivity})");

                        // Delete UserSessionData
                        var userSessionData = await dbContext.UserSessionData
                            .FirstOrDefaultAsync(usd => usd.UserId == user.UserId, stoppingToken);
                        if (userSessionData != null)
                        {
                            dbContext.UserSessionData.Remove(userSessionData);
                        }

                        // Delete CSV file if it exists
                        var csvFilePath = Path.Combine("CsvFiles", $"{user.UserId}.csv");
                        if (System.IO.File.Exists(csvFilePath))
                        {
                            try
                            {
                                System.IO.File.Delete(csvFilePath);
                                Console.WriteLine($"Deleted CSV file: {csvFilePath}");
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Error deleting CSV file {csvFilePath}: {ex.Message}");
                            }
                        }

                        // Update user login status
                        user.IsLoggedIn = false;
                        user.LastActivity = DateTime.UtcNow; // Reset LastActivity to prevent repeated logout attempts
                    }

                    if (inactiveUsers.Any())
                    {
                        await dbContext.SaveChangesAsync(stoppingToken);
                        Console.WriteLine($"Logged out {inactiveUsers.Count} inactive users.");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in SessionTimeoutService: {ex.Message}");
            }
        }
    }
}