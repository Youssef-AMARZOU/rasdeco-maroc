$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=RASD Maroc Security Cert" -CertStoreLocation "Cert:\CurrentUser\My"
$cerPath = Join-Path $env:TEMP "RASD-Cert.cer"
Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null
Import-Certificate -FilePath $cerPath -CertStoreLocation "Cert:\CurrentUser\Root" | Out-Null
Import-Certificate -FilePath $cerPath -CertStoreLocation "Cert:\CurrentUser\TrustedPublisher" | Out-Null

$target = Resolve-Path "dashboard/dist-electron/win-unpacked/RASD-Maroc.exe"
Set-AuthenticodeSignature -FilePath $target -Certificate $cert
Write-Host "SIGNING COMPLETE FOR $target"
