# OpenDEP Control
Dielectrophoresis (DEP) experiments automation and control software. With this software you can control all three machines which are
usual used in DEP experiments: function generator, microscope camera and microfluidic pump. The range of control is limited
on the DEP application. 

At this moment we try to make the software function with most video cameras or DSRL cameras (though the video camera option or capture card
is recommended), Agilent Function generators (through the seral port,)  In the future control over Fluidgent microfluidic pumps will be added
and compatibility will be improved.

It is a part of OpenDEP project, and one of the three programs delivered by the OpenDEP project: 
1. [OpenDEP Compute](https://github.com/IoanTivig/OpenDEP) (for spectra fitting and data conversion)
2. [OpenDEP Control](https://github.com/IoanTivig/OpenDEP_Control) (for experiments automation and control of machines)
3. OpenDEP View (for visualization of spectra and spectra generation based on parameters).

Published under GNU GPL v3.0 license.

## Installation
1. Download the latest release from this repository.
2. Add the repository to your IDE (tested with PyCharm).
3. Install the requirements from requirements.txt file.
4. Run the main.py file.
5. Enjoy!

PS: Soon the software will be available as a standalone executable file. 
If you need any help with the installation, please contact me.

## Publications
1. [OpenDEP: An Open-Source Platform for Dielectrophoresis Spectra Acquisition and Analysis](https://pubs.acs.org/doi/10.1021/acsomega.3c06052)

## Other DEP Tools
1. [MyDEP](https://mydepsoftware.github.io/)

## Other
Please be aware that the software is still in development, so bugs may occur. If you find any bugs, please contact me.
The software is tested on Windows 11, but it should work on other operating systems as well, if digiCamControl is not used.
If you want to use your DSRL camera without a capture card you will need to install [digiCamControl](https://digicamcontrol.com/).
The software is tested with Agilent 33220A function generator, but it should work with other Agilent function generators as well.
If you want to use other function generators, you will need to change the code in the function_generator.py file.


