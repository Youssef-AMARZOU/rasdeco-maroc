Attribute VB_Name = "SearchTables"
'=====================================================
' SearchTables - Macro de recherche pour tables Excel
' Utilisation: Ctrl+Shift+F ou via le ruban Developpeur
'=====================================================

Sub SearchAllTables()
    ' Recherche dans toutes les feuilles du classeur
    Dim searchTerm As String
    Dim ws As Worksheet
    Dim rng As Range
    Dim found As Range
    Dim firstAddress As String
    Dim results As String
    Dim count As Integer
    
    searchTerm = InputBox("Entrez le texte ou la valeur a rechercher dans toutes les tables:", "Recherche dans les tables")
    
    If searchTerm = "" Then Exit Sub
    
    count = 0
    results = "Resultats de la recherche pour: " & searchTerm & vbCrLf & vbCrLf
    
    For Each ws In ThisWorkbook.Worksheets
        Set rng = ws.UsedRange
        Set found = rng.Find(What:=searchTerm, LookIn:=xlValues, LookAt:=xlPart)
        
        If Not found Is Nothing Then
            firstAddress = found.Address
            Do
                count = count + 1
                results = results & "Feuille: " & ws.Name & " | Cellule: " & found.Address & _
                          " | Valeur: " & found.Value & vbCrLf
                Set found = rng.FindNext(found)
            Loop While Not found Is Nothing And found.Address <> firstAddress
        End If
    Next ws
    
    If count > 0 Then
        results = results & vbCrLf & "Total: " & count & " occurrence(s) trouvee(s)."
        MsgBox results, vbInformation, "Recherche terminee"
    Else
        MsgBox "Aucun resultat trouve pour: " & searchTerm, vbExclamation, "Recherche"
    End If
End Sub

Sub SearchCurrentSheet()
    ' Recherche uniquement dans la feuille active
    Dim searchTerm As String
    Dim rng As Range
    Dim found As Range
    Dim firstAddress As String
    Dim results As String
    Dim count As Integer
    
    searchTerm = InputBox("Entrez la valeur a rechercher dans la feuille active:", "Recherche dans la feuille")
    
    If searchTerm = "" Then Exit Sub
    
    count = 0
    results = "Resultats dans la feuille [" & ActiveSheet.Name & "] pour: " & searchTerm & vbCrLf & vbCrLf
    
    Set rng = ActiveSheet.UsedRange
    Set found = rng.Find(What:=searchTerm, LookIn:=xlValues, LookAt:=xlPart)
    
    If Not found Is Nothing Then
        firstAddress = found.Address
        Do
            count = count + 1
            results = results & "Cellule: " & found.Address & " | Valeur: " & found.Value & vbCrLf
            Set found = rng.FindNext(found)
        Loop While Not found Is Nothing And found.Address <> firstAddress
    End If
    
    If count > 0 Then
        results = results & vbCrLf & "Total: " & count & " occurrence(s) dans la feuille active."
        MsgBox results, vbInformation, "Recherche terminee"
    Else
        MsgBox "Aucun resultat trouve pour: " & searchTerm, vbExclamation, "Recherche"
    End If
End Sub

Sub HighlightSearchTerm()
    ' Recherche et surligne en jaune toutes les occurrences
    Dim searchTerm As String
    Dim rng As Range
    Dim found As Range
    Dim firstAddress As String
    
    searchTerm = InputBox("Entrez la valeur a surligner dans la feuille active:", "Surligner")
    
    If searchTerm = "" Then Exit Sub
    
    ' Effacer les couleurs precedentes
    Cells.Interior.ColorIndex = xlNone
    
    Set rng = ActiveSheet.UsedRange
    Set found = rng.Find(What:=searchTerm, LookIn:=xlValues, LookAt:=xlPart)
    
    If Not found Is Nothing Then
        firstAddress = found.Address
        Do
            found.Interior.Color = RGB(255, 255, 0)  ' Jaune
            Set found = rng.FindNext(found)
        Loop While Not found Is Nothing And found.Address <> firstAddress
        
        MsgBox "Recherche terminee. Toutes les occurrences sont surlignees en jaune.", vbInformation, "Surlignage"
    Else
        MsgBox "Aucun resultat trouve.", vbExclamation, "Recherche"
    End If
End Sub

Sub ClearHighlights()
    ' Efface tous les surlignages
    Cells.Interior.ColorIndex = xlNone
    MsgBox "Surlignages effaces.", vbInformation
End Sub
