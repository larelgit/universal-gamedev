@echo off
rem Runs universal-modder's `um` CLI (fal assets, sprites, 3D-to-sprite, window capture and input, video)
rem through uvx at a pinned commit. Install it permanently instead with:
rem   uv tool install git+https://github.com/rehan-remade/universal-modder
setlocal
if not defined UM_REF set "UM_REF=15d6f9d5fbd32de9b1884f29ddec3be9133bd912"
where uvx >nul 2>nul || goto nouv
uvx --from "git+https://github.com/rehan-remade/universal-modder@%UM_REF%" um %*
exit /b %ERRORLEVEL%
:nouv
echo um: needs uv (https://docs.astral.sh/uv/), or install it: uv tool install git+https://github.com/rehan-remade/universal-modder 1>&2
exit /b 1
