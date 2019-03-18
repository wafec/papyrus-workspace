set destination=%1
set setup_name=%2

set loopcount=9
set exp_destination=""

:loop
if %loopcount%==-1 goto exitloop

set exp_destination=%destination%\exp_%loopcount%
mkdir %exp_destination%
java -cp statemutest.jar statemutest.application.TestCaseGeneration -s %setup_name% -d %exp_destination%

set /a loopcount=loopcount-1
goto loop
:exitloop
pause