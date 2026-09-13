$uri = "http://127.0.0.1:5000/blur"

$email = "test@example.com"
$imagePath = "test.png"

# Читаем файл как байты
$imageBytes = [System.IO.File]::ReadAllBytes($imagePath)

# Создаём multipart/form-data
$boundary = "----WebKitFormBoundary" + [System.Guid]::NewGuid().ToString("N")
$lines = @(
    "--$boundary",
    'Content-Disposition: form-data; name="email"',
    "",
    $email,
    "--$boundary",
    "Content-Disposition: form-data; name=`"images`"; filename=`"$imagePath`"",
    "Content-Type: image/png",
    "",
    ""
)

$header = [System.Text.Encoding]::UTF8.GetBytes(($lines -join "`r`n") + "`r`n")
$footer = [System.Text.Encoding]::UTF8.GetBytes("`r`n--$boundary--`r`n")

$memoryStream = New-Object System.IO.MemoryStream
$memoryStream.Write($header, 0, $header.Length)
$memoryStream.Write($imageBytes, 0, $imageBytes.Length)
$memoryStream.Write($footer, 0, $footer.Length)
$memoryStream.Position = 0

$contentType = "multipart/form-data; boundary=$boundary"

$response = Invoke-WebRequest -Uri $uri `
    -Method POST `
    -ContentType $contentType `
    -Body $memoryStream `
    -UseBasicParsing

$response.Content