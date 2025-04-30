# Desktop Wallpapers slideshow tool (for Windows)

In file **desktop_slideshow.py**, the constant `BACKGROUNDS_DIRECTORY` has to be modified to correspond to the directory containing the wallpapers to display. <br />
Every 3 minutes (can be configurable through constant `DELAY_BETWEEN_UPDATES`), a random image from the directory will be copied to `%AppData%\Microsoft\Windows\Themes`
and renamed as `TranscodedWallpaper` (with no extension). <br />
This file is used by Windows to set the wallpaper (when no slideshow is activated and a single image is chosen).

Then, a powershell script **update_screen.ps1** is launched to force the update of the desktop wallpaper.

The purpose is to be able to set a Wallpaper Slideshow even if you don't have the permission rights to update the Wallpaper in Windows Personalization parameters,
for example when there is a Group Policy and you don't have admin rights.

The tool is thought to be launched with a VBScript (with extension .vbs) so the running window can be hidden:
```vbscript
Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "python PATH\TO\desktop_slideshow.py"
oShell.Run strArgs, 0, false
```
This VBScript can be put inside the Startup directory (`%AppData%\Microsoft\Windows\Start Menu\Programs\Startup`) so that it is laucnhed directly when computer starts.

In addition to this, a tray icon is used to be able to monitor the program and be able to kill it as the command window launching it is hidden. <br />
Python module `infi.systray` is used to configure this tray icon. <br />
An option is set to be able to go instantaneously to next wallpaper (without waiting the delay), <br />
and another option is set to be able to go back to the previous wallpaper.
