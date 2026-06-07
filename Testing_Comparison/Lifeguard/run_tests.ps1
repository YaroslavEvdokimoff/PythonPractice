for ($i = 3; $i -le 10; $i++) {
    Write-Host "Запуск теста $i..."
    Get-Content ".\test${i}_input.txt" | python ".\Exercise1.py" > "test${i}_actual_output.txt"
}
Write-Host "неплохо, неплохо!" -ForegroundColor Green