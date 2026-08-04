# PowerShell Script : Signature de l'application sous le nom de Youssef AMARZOU (Licence Open Source MIT)

$certSubject = "CN=Youssef AMARZOU (MIT Open Source License)"
$exePath = Resolve-Path "dashboard/dist-electron/win-unpacked/RASD-Maroc.exe"

# 1. Créer le certificat Code Signing sous le nom de Youssef AMARZOU
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject $certSubject -CertStoreLocation "Cert:\CurrentUser\My"

# 2. Exporter et importer le certificat dans les Autorités de Confiance Windows
$cerPath = Join-Path $env:TEMP "Youssef-AMARZOU-MIT-Cert.cer"
Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null
Import-Certificate -FilePath $cerPath -CertStoreLocation "Cert:\CurrentUser\Root" | Out-Null
Import-Certificate -FilePath $cerPath -CertStoreLocation "Cert:\CurrentUser\TrustedPublisher" | Out-Null

# 3. Signer numériquement l'exécutable
Set-AuthenticodeSignature -FilePath $exePath -Certificate $cert

Write-Host "============================================================"
Write-Host "APPLICATION SIGNEE AVEC SUCCES SOUS LE NOM :"
Write-Host "Auteur   : Youssef AMARZOU"
Write-Host "Licence  : MIT Open Source License"
Write-Host "Binaire  : $exePath"
Write-Host "============================================================"
