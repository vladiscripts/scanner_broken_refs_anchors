REM Для запуска скрипта из AWB
set WshShell = WScript.CreateObject("WScript.Shell")
set WshArguments=WScript.Arguments
WshShell.CurrentDirectory = "d:\home\scripts.my\wikiapi_framework\"
command = "python add_warning_tpl.py"
if WshArguments.count()=0 then
	'c:\Python35\python.exe c:\Python35\ParserTempates_SlovariYandex.py
	WshShell.Run command,0,true
else
	WshShell.Run command & " " & """" & WshArguments(0) & """", 0,true
end if

REM Option Explicit
 
REM Dim WshArguments, i, list
 
REM list=""
 
REM 'Получаем доступ к коллекции через свойство Arguments
REM set WshArguments=WScript.Arguments
 
REM 'Определяем, есть ли передача параметров
REM if WshArguments.count()=0 then
    REM MsgBox "Передайте сценарию аргументы"
REM else
    REM ' Производим перебор коллекции
    REM for i=0 to WshArguments.Count-1
        REM list = list & WshArguments(0) & vbCrLf
    REM next
    REM MsgBox list
REM End if