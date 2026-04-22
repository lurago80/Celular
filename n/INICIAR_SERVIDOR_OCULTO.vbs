' Script VBScript que executa o Python de forma oculta
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Obter o diretório atual do script
ScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Caminho completo do arquivo Python
PythonPath = ScriptDir & "\iniciar_servidor_oculto.py"

' Verificar se arquivo existe
If Not fso.FileExists(PythonPath) Then
    MsgBox "Arquivo não encontrado: " & PythonPath, vbCritical, "Erro"
    WScript.Quit
End If

' Usar pythonw.exe (versão sem janela) do sistema
' O script Python já vai usar o Python do ambiente virtual interno
PythonExe = "pythonw.exe"

' Testar se pythonw.exe existe no PATH
On Error Resume Next
Set oShell = CreateObject("WScript.Shell")
oShell.Run "where pythonw.exe", 0, True
If Err.Number <> 0 Then
    ' Se não encontrar, usar python.exe (mas ainda oculto)
    PythonExe = "python.exe"
End If
On Error GoTo 0

' Executar Python de forma oculta (0 = vbHide oculta a janela)
' O script Python vai usar o Python do .venv internamente
WshShell.Run PythonExe & " """ & PythonPath & """", 0, False

' Aguardar mais tempo - o script Python agora gerencia quando abrir o navegador
' Não precisa abrir navegador aqui, o Python já faz isso após verificar que o servidor está pronto
' WScript.Sleep 5000
' WshShell.Run "http://localhost:8000"

' O script Python agora espera o servidor realmente iniciar antes de abrir o navegador

' Script VBScript termina, mas o processo Python continua rodando em background

