# LM Measurement Tool Omniverse Kit Extension

This project is an extension for any Omniverse Kit application that has an active viewport. The tool enables the user to measure real-world size and distance of meshes and objects within the viewport scene.

# Enabling this extension in Kit

1. Clone this repository to the desired location on your machine with
> git clone https://github.com/Brett-Amberge/lm-measurement-tool
2. In the *Omniverse App* open extension manager: *Window* &rarr; *Extensions*.
3. In the *Extension Manager Window* open a settings page, with a small gear button in the top left bar.
4. Click the green + icon to add an additional path
5. In the settings page there is a list of *Extension Search Paths*. Add cloned repo `exts` subfolder there as another search path, i.e.: `C:\projects\kit-extension-template\exts`

![Extension Manager Window](/images/add-ext-search-path.png)

6. The extension will now appear in the extension manager window. Simply toggle it on to enable it.

# Using this extension

Once the extension is enabled, additional toolbar options will appear in the menu of your Kit Application. Enabling these will enable the measurement tool, as long as the application has an active Viewport Window. With the tool enabled, click anywhere in the Viewport Window where there is an object. Click again to display the distance between the two points in centimeters. This can be repeated to add additional ruler lines as many times as you like. Double click anywhere in the viewport to clear any active measurements.
