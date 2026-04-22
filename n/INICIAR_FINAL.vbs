' Script final para iniciar servidor completamente oculto (alternativa)
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Obter o diretório atual do script
ScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Caminho completo do arquivo Python
PythonPath = ScriptDir & "\iniciar_servidor_oculto.py"

' Verificar se arquivo existe
If Not fso.FileExists(PythonPath) Then
    MsgBox "Arquivo não encontrado: " & PythonPath & vbCrLf & _
           "Procurei em:" & vbCrLf & _
           "- Pasta do script" & vbCrLf & _
           "- C:\INOVE\CELULAR (Cliente)" & vbCrLf & _
           "- C:\PROJETOS\CELULAR (Desenvolvimento)", _
           vbCritical, "Erro"
    WScript.Quit
End If

' Usar pythonw.exe (versão sem janela) do sistema
PythonExe = "pythonw.exe"

' Testar se pythonw.exe existe no PATH
On Error Resume Next
Set oShell = CreateObject("WScript.Shell")
oShell.Run "where pythonw.exe", 0, True
If Err.Number <> 0 Then
    PythonExe = "python.exe"
End If
On Error GoTo 0

' Executar Python de forma completamente oculta (0 = vbHide)
WshShell.Run PythonExe & " """ & PythonPath & """", 0, False

' Script termina, mas o processo Python continua rodando em background

