@echo off

:: Step 1: ��ָ���ļ�
start notepad "C:\GPT-SoVITS-beta0706\RUNALL_CONFIG.py"

:: �ȴ��û�����ȷ��
:confirm1
set /p input=�ļ��Ѵ򿪣������� "ok" ����: 
if /i "%input%"=="ok" goto run_all_1
echo ����������������롣
goto confirm1

:run_all_1
echo ����ִ�е�һ��...
cd C:\GPT-SoVITS-beta0706\
runtime\python.exe RUNALL-1.py
echo ��һ������ɡ�

:: Step 2: ��ָ���ļ���
:open_folder
start explorer "C:\GPT-SoVITS-beta0706\output\slicer_opt"

:: �ٴεȴ��û�����ȷ��
:confirm2
set /p input=�ļ����Ѵ򿪣������� "ok" ����: 
if /i "%input%"=="ok" goto run_all_2
echo ����������������롣
goto confirm2

:: Step 3: ��������
:run_all_2
echo ����ִ�еڶ���...
runtime/python.exe RUNALL-2.py
echo �ڶ�������ɡ�
pause
