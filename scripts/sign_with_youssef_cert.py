import os
import subprocess

ps_script = """
$cert = Get-ChildItem Cert:\\CurrentUser\\My -CodeSigningCert | Where-Object { $_.Subject -like "*Youssef AMARZOU*" } | Select-Object -First 1
if (-not $cert) {
    $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=Youssef AMARZOU (MIT Open Source License)" -CertStoreLocation "Cert:\\CurrentUser\\My"
    $cerPath = Join-Path $env:TEMP "Youssef-AMARZOU.cer"
    Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null
    Import-Certificate -FilePath $cerPath -CertStoreLocation "Cert:\\CurrentUser\\Root" | Out-Null
    Import-Certificate -FilePath $cerPath -CertStoreLocation "Cert:\\CurrentUser\\TrustedPublisher" | Out-Null
}

$exe = (Get-Item "dashboard/dist-electron/win-unpacked/RASD-Maroc.exe").FullName
$res = Set-AuthenticodeSignature -FilePath $exe -Certificate $cert
Write-Host "SIGN_RESULT:" $res.Status
Write-Host "SIGNER:" $res.SignerCertificate.Subject
"""

script_path = "scripts/do_sign_youssef.ps1"
with open(script_path, "w", encoding="utf-8") as f:
    f.write(ps_script)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], capture_output=True, text=True)
print(res.stdout)
print(res.stderr)
