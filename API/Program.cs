using Microsoft.Data.Sqlite;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// --- Configuración ---
// Apuntamos al archivo .db que genera el bot de Python
string dbRelativePath = Path.Combine("..", "Data", "bot_logs.db");
string dbPath = Path.GetFullPath(dbRelativePath);
string connectionString = $"Data Source={dbPath}";

// --- Endpoint de Exposición ---
app.MapGet("/api/logs", async (int page = 1, int size = 10 ) =>
{
    // Verificamos que la base de datos exista
    if (!File.Exists(dbPath))
    {
        return Results.NotFound(new { message = "Database not found. Please interact with the Telegram bot first." });
    }

    if (page < 1) page = 1;
    if (size < 1 || size > 50) size = 10;

    int offset = (page - 1) * size;
    var logs = new List<BotLog>();

    try
    {
        using (var connection = new SqliteConnection(connectionString))
        {
            await connection.OpenAsync();
            var command = connection.CreateCommand();
            
            command.CommandText = @"
                SELECT Id, TelegramUserId, Username, MessageText, Timestamp 
                FROM InteractionLogs 
                ORDER BY Id DESC 
                LIMIT 50";

            using (var reader = await command.ExecuteReaderAsync())
            {
                while (await reader.ReadAsync())
                {
                    // Manejo seguro de nulos: El username puede ser nulo en Telegram, 
                    // así que verificamos con IsDBNull antes de leer el string.
                    string username = reader.IsDBNull(2) ? "Anonymous" : reader.GetString(2);

                    logs.Add(new BotLog(
                        reader.GetInt32(0),
                        reader.GetInt64(1),
                        username,
                        reader.GetString(3),
                        reader.GetString(4)
                    ));
                }
            }
        }
        
        return Results.Ok(new
        {
            Page = page,
            Size = size,
            Data = logs
        });
    }
    catch (Exception ex)
    {
        return Results.Problem(detail: ex.Message, title: "Database Connection Error");
    }
});

app.Run();

// --- Data Transfer Object (DTO) ---
public record BotLog(int Id, long TelegramUserId, string Username, string MessageText, string Timestamp);