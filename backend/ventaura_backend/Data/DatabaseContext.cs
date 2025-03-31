/* This file defines the DatabaseContext, which acts as the bridge between the Ventaura 
application and the underlying database. It configures the database schema using Entity 
Framework Core, ensuring proper table setup, enforcing constraints, and managing data 
interactions such as querying and saving records. The file is essential for maintaining 
the structure and integrity of the database. */

using Microsoft.EntityFrameworkCore;
using ventaura_backend.Models;

namespace ventaura_backend.Data
{
    public class DatabaseContext : DbContext
    {
        // Constructor for injecting database options into the context.
        public DatabaseContext(DbContextOptions<DatabaseContext> options) : base(options) { }

        // DbSet properties representing tables in the database.
        public DbSet<User> Users { get; set; }
        public DbSet<UserContent> UserContent { get; set; }
        public DbSet<HostEvent> HostEvents { get; set; }
        public DbSet<UserSessionData> UserSessionData {get; set; }

        // Configures the model and schema for the database during creation.
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {

            // Configure the primary key for HostEvent
            modelBuilder.Entity<HostEvent>()
                .HasKey(he => he.EventId);

            // Configure the default value for the CreatedAt column
            modelBuilder.Entity<HostEvent>()
                .Property(he => he.CreatedAt)
                .HasDefaultValueSql("NOW()");

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
            
            
            // Configure the UserSessionData table
            modelBuilder.Entity<UserSessionData>()
                .HasKey(usd => usd.Id); // Primary key

            // Map PascalCase properties to lowercase column names
            modelBuilder.Entity<UserSessionData>()
                .Property(usd => usd.Id)
                .HasColumnName("id");

            modelBuilder.Entity<UserSessionData>()
                .Property(usd => usd.UserId)
                .HasColumnName("userid");

            modelBuilder.Entity<UserSessionData>()
                .Property(usd => usd.RankedCSV)
                .HasColumnName("rankedcsv");

            modelBuilder.Entity<UserSessionData>()
                .Property(usd => usd.CreatedAt)
                .HasColumnName("createdat")
                .HasDefaultValueSql("NOW()"); // Default value for CreatedAt

            modelBuilder.Entity<UserSessionData>()
                .Property(usd => usd.IsRanked)
                .HasColumnName("IsRanked");

            modelBuilder.Entity<UserSessionData>()
                .HasOne(usd => usd.User)
                .WithMany()
                .HasForeignKey(usd => usd.UserId); // Foreign key to Users table

            
            base.OnModelCreating(modelBuilder); // Call the base implementation
            
        }
    }
}