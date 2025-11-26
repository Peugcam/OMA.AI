@echo off
echo ========================================
echo Limpeza Manual - OMA Video Generator
echo ========================================
echo.
echo Este script vai remover:
echo - node_modules (14.6 MB)
echo - htmlcov (1.8 MB)
echo - reports (2.9 MB)
echo - __pycache__ (~300 KB)
echo - screenshots PNG (~800 KB)
echo.
echo Total: ~20 MB
echo.
pause

cd /d "%~dp0"

echo.
echo Removendo node_modules...
if exist node_modules (
    rmdir /s /q node_modules
    echo OK - node_modules removido
) else (
    echo OK - node_modules nao existe
)

echo.
echo Removendo htmlcov...
if exist htmlcov (
    rmdir /s /q htmlcov
    echo OK - htmlcov removido
) else (
    echo OK - htmlcov nao existe
)

echo.
echo Removendo reports...
if exist reports (
    rmdir /s /q reports
    echo OK - reports removido
) else (
    echo OK - reports nao existe
)

echo.
echo Removendo __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
echo OK - __pycache__ removido

echo.
echo Removendo .pytest_cache...
if exist .pytest_cache (
    rmdir /s /q .pytest_cache
    echo OK - .pytest_cache removido
) else (
    echo OK - .pytest_cache nao existe
)

echo.
echo Removendo screenshots PNG...
del /q *.png 2>nul
echo OK - screenshots removidos

echo.
echo Removendo .coverage...
del /q .coverage 2>nul
echo OK - .coverage removido

echo.
echo ========================================
echo LIMPEZA CONCLUIDA!
echo ========================================
echo.
echo Verifique o espaco liberado:
dir /s
echo.
pause
