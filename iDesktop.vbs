Option Explicit

Dim shell, files, root, launcher
Set files = CreateObject("Scripting.FileSystemObject")
root = files.GetParentFolderName(WScript.ScriptFullName)
launcher = files.BuildPath(root, "iDesktop.bat")

If Not files.FileExists(launcher) Then
    MsgBox "The iDesktop launcher was not found:" & vbCrLf & launcher, vbCritical, "iDesktop"
    WScript.Quit 1
End If

Set shell = CreateObject("WScript.Shell")
shell.Run """" & launcher & """", 0, False
