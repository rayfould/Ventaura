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
        // Constructor for injecting database options into the context.
        public DatabaseContext(DbContextOptions<DatabaseContext> options) : base(options) { }

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            // Add connection string with SSL and timeout
            optionsBuilder.UseNpgsql("Host=aws-0-us-east-1.pooler.supabase.com;Port=6543;Database=postgres;Username=postgres.tybxxsijvsytmztqhffh;Password=cs392ventaura;SSL Mode=Require;Trust Server Certificate=true;",
                options => options.CommandTimeout(180)); // Increase timeout to 180 seconds
        }

        // DbSet property representing the Users table in the database.
        public DbSet<User> Users { get; set; }

        // Configures the model and schema for the database during creation.
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            // Configures the Users table to have a unique index on the Email column.
            modelBuilder.Entity<User>()
                .HasIndex(u => u.Email)
                .IsUnique(); // Ensures no duplicate email addresses are stored.
        }
    }
}