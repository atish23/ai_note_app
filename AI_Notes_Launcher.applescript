-- AI Notes Launcher AppleScript
-- This script launches the AI Notes/Task Manager app

on run
	-- Get the path to the script directory
	set scriptPath to (path to me as text)
	set scriptDir to do shell script "dirname " & quoted form of POSIX path of scriptPath
	
	-- Change to the script directory
	do shell script "cd " & quoted form of scriptDir
	
	-- Check if virtual environment exists
	set venvCheck to do shell script "if [ -d 'venv_mcp' ]; then echo 'OK'; else echo 'MISSING'; fi"
	
	if venvCheck is "MISSING" then
		display dialog "❌ Virtual environment not found. Please run setup first:" & return & return & "Open Terminal and run:" & return & "   ./run_macos.sh setup" buttons {"OK"} default button "OK" with icon stop
		return
	end if
	
	-- Launch the native macOS app
	try
		do shell script "./run_macos.sh macos"
	on error errMsg
		display dialog "❌ Error launching AI Notes app:" & return & return & errMsg buttons {"OK"} default button "OK" with icon stop
	end try
end run
