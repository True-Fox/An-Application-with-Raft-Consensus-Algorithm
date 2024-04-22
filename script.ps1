# Define commands
$commands = @(
    "python3 raft-backend/main.py -a 127.0.0.3:5010 -i 1 -e '2/127.0.0.3:5020,3/127.0.0.3:5030'",
    "python3 raft-backend/main.py -a 127.0.0.3:5020 -i 2 -e '1/127.0.0.3:5010,3/127.0.0.3:5030'",
    "python3 raft-backend/main.py -a 127.0.0.3:5030 -i 3 -e '1/127.0.0.3:5010,2/127.0.0.3:5020'"
)

# Open terminals with commands
foreach ($command in $commands) {
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c start powershell -NoExit -Command `"$command`"" -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

Start-Process -FilePath "cmd.exe" -ArgumentList "/c start powershell -NoExit -Command `"python3 app.py`"" -WindowStyle Hidden