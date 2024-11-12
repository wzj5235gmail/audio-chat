@echo off

:: Step 1: 打开指定文件
start notepad "C:\GPT-SoVITS-beta0706\RUNALL_CONFIG.py"

:: 等待用户输入确认
:confirm1
set /p input=文件已打开，请输入 "ok" 继续: 
if /i "%input%"=="ok" goto run_all_1
echo 输入错误，请重新输入。
goto confirm1

:run_all_1
echo 正在执行第一步...
cd C:\GPT-SoVITS-beta0706\
runtime\python.exe RUNALL-1.py
echo 第一步已完成。

:: Step 2: 打开指定文件夹
:open_folder
start explorer "C:\GPT-SoVITS-beta0706\output\slicer_opt"

:: 再次等待用户输入确认
:confirm2
set /p input=文件夹已打开，请输入 "ok" 继续: 
if /i "%input%"=="ok" goto run_all_2
echo 输入错误，请重新输入。
goto confirm2

:: Step 3: 运行命令
:run_all_2
echo 正在执行第二步...
runtime/python.exe RUNALL-2.py
echo 第二步已完成。
pause
