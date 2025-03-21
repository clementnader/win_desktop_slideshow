# Desktop Wallpapers slideshow tool (for Windows)

File **desktop_slideshow.py** contains the path to the directory of wallpapers. <br />
Every 3 minutes (can be configurable), a random image from the directory will be copied to `%AppData%\Microsoft\Windows\Themes`
and renamed as `TranscodedWallpaper` (with no extension). <br />
This file is used by Windows to set the wallpaper (when no slideshow is activated and a single image is chosen).

Then, a powershell script **update_screen.ps1** is launched to force the update of the desktop wallpaper.

The purpose is to be able to set a Wallpaper Slideshow even if you don't have the permission rights to update the Wallpaper in Windows Personalization parameters,
for example with a Group Policy, when you don't have admin rights.

The tool is thought to be launched with a VBScript so the running window can be hidden:
```vbscript
Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "python PATH\TO\desktop_slideshow.py"
oShell.Run strArgs, 0, false
```

In addition to this, a tray icon is used to be able to monitor the program and be able to kill it as the window is hidden. <br />
Python module `infi.systray` is used to configure this tray icon. <br />
An option is set to be able to go instantaneously to Next Wallpaper (without waiting the 3 minutes), <br />
and another option is set to be able to go back to the previous wallpaper.
