/* This file defines the DatabaseContext, which acts as the bridge between the Ventaura 
application and the underlying database. It configures the database schema using Entity 
Framework Core, ensuring proper table setup, enforcing constraints, and managing data 
interactions such as querying and saving records. The file is essential for maintaining 
the structure and integrity of the database. */

using Microsoft.EntityFrameworkCore;
using ventaura_backend.Models;

namespace ventaura_backend.Data
{
    // Defines the database context for Entity Framework Core.
    public class DatabaseContext : DbContext
    {
        // Explicit connection string for Supabase database.
        private const string ConnectionString = "Host=aws-0-us-east-1.pooler.supabase.com;Port=6543;Database=postgres;Username=postgres.lzrnyahwsvygmcdqofkm;Password=cs392ventaura;SslMode=Require;TrustServerCertificate=true;";

        // Constructor for injecting database options into the context.
        public DatabaseContext(DbContextOptions<DatabaseContext> options) : base(options) { }

        // Parameterless constructor to ensure proper creation of the DbContext.
        public DatabaseContext() { }

        // DbSet properties representing tables in the database.
        public DbSet<User> Users { get; set; }
        public DbSet<UserContent> UserContent { get; set; }

        // Configures the model and schema for the database during creation.
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            // Configures the Users table to have a unique index on the Email column.
            modelBuilder.Entity<User>()
                .HasIndex(u => u.Email)
                .IsUnique(); // Ensures no duplicate email addresses are stored.

            // Configures the UserContent table with constraints or default values.
            modelBuilder.Entity<UserContent>()
                .Property(uc => uc.Title)
                .IsRequired(); // Title is required.

            modelBuilder.Entity<UserContent>()
                .Property(uc => uc.CreatedAt)
                .HasDefaultValueSql("NOW()"); // Default value for CreatedAt.
        }

        // Configures the database to use the explicit connection string.
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            optionsBuilder.UseNpgsql(ConnectionString, options =>
                options.EnableRetryOnFailure(
                    maxRetryCount: 5, 
                    maxRetryDelay: TimeSpan.FromSeconds(10), 
                    errorCodesToAdd: null));
        }
    }
}
