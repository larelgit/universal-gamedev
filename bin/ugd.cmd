@echo off
rem universal-gamedev CLI launcher for Windows shells (cmd, PowerShell). Git Bash uses bin/ugd.
rem Uses uv when available (it creates the project's .venv on first run); otherwise python on PATH,
rem which then needs `pip install pyyaml pillow`.
setlocal
set "ROOT=%~dp0.."
if defined UGD_NO_UV goto python
where uv >nul 2>nul || goto python
uv run --quiet --project "%ROOT%" python -m ugd %*
exit /b %ERRORLEVEL%
:python
set "PYTHONPATH=%ROOT%;%PYTHONPATH%"
python -m ugd %*
exit /b %ERRORLEVEL%
