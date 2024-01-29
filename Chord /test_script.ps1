# PowerShell Script to Run Python Script Repeatedly in a New Terminal Window with Arguments

# Set the path to your Python executable
$pythonExecutable = "python"

# Set the path to your Python script
$pythonNode = "./node_merged.py"
$pythonLoadData = "./data_load.py"

# Set additional arguments to pass to the Python script
$scriptArguments1 = 3001
$scriptArguments2 = 3001

# Set the number of times you want to run the Python script
$numberOfRuns = 40

# Counter for the number of runs
$runCounter = 0

$delayBetweenRuns = 10

Write-Host "Creating Ring"

Start-Process -FilePath "cmd.exe" -ArgumentList "/c start $pythonExecutable $pythonNode $scriptArguments2" -NoNewWindow -Wait

Start-Sleep -Seconds $delayBetweenRuns

# Main loop to run the Python script repeatedly
while ($runCounter -lt $numberOfRuns) {
    
    $scriptArguments1++

    # Increment the run counter
    $runCounter++

    # Display information about the current run
    Write-Host "Creating Node #$runCounter"

    # Execute the Python script in a new terminal window with arguments
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c start $pythonExecutable $pythonNode $scriptArguments1 $scriptArguments2" -NoNewWindow -Wait

    Start-Sleep -Seconds 2
}

$delayBetweenRuns=20

Start-Sleep -Seconds $delayBetweenRuns

Write-Host "Inserting data..."

Start-Process -FilePath "cmd.exe" -ArgumentList "/c start $pythonExecutable $pythonLoadData $scriptArguments2" -NoNewWindow -Wait