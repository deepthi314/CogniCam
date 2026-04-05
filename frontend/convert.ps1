$files = @("app.js", "index.html", "style.css")
foreach ($file in $files) {
    $content = Get-Content -Path $file -Encoding Unicode
    Set-Content -Path "$file.utf8" -Value $content -Encoding UTF8
}
