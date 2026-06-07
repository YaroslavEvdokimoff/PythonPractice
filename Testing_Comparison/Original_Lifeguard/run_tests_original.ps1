for ($i = 3; $i -le 10; $i++) {
    $num = "{0:D2}" -f $i
    Write-Host "Запуск теста $num..." -ForegroundColor Cyan
    Get-Content ".\test${num}_input.txt" | python ".\life_guard.py" > "test${num}_actual_output.txt"
}
Write-Host "Все тесты от 03 до 10 выполнены!" -ForegroundColor Green