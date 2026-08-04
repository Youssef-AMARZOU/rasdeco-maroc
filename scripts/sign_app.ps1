# PowerShell Script to create self-signed certificate, import it into Trusted Root, and sign RASD-Maroc.exe

$certSubject = "CN=RASD Maroc Local Code Signing"
$exePath = Resolve-Path "dashboard/dist-electron/win-unpacked/RASD-Maroc.exe"

# 1. Create Code Signing Cert
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject $certSubject -CertStoreLocation "Cert:\CurrentUser\My"

# 2. Export and import into Root & TrustedPublisher
$cerPath = Join-Path $env:TEMP "RASD-Maroc-Cert.cer"
Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null
Import-Certificate -FilePath $cerPath -CertStoreLocation "Cert:\CurrentUser\Root" | Out-Null
Import-Certificate -FilePath $cerPath -CertStoreLocation "Cert:\CurrentUser\TrustedPublisher" | Out-Null

# 3. Sign the executable with the certificate
Set-AuthenticodeSignature -FilePath $exePath -Certificate $cert

Write-Host "[OK] Executable signe avec succes !"
Write-Host "Chemin : $exePath"
Write-Host "Certificat valide et approuve dans le magasin de confiance Windows."
