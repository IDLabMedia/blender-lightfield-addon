# Blender Addon for Light Field Rendering
<img src="https://img.shields.io/badge/compatible-2.8+-orange?logo=blender&style=flat-square" />

<img src="docs/teaser.PNG"  height="150"/> <img src="docs/teaser2.png"  height="150"/>

This addon allows to **quickly create several multi-camera setups in Blender**. It automatically renders and saves the generated images (and depth information). The addon currently supports 4 basic multi-camera setup types, which can be combined to create large image datasets:

<p float="left">
  <img src="/docs/Plane.PNG" width="170" />
  <img src="/docs/Cuboid.PNG" width="170" />
  <img src="/docs/Cylinder.PNG" width="170" />
  <img src="/docs/Sphere.PNG" width="170" />
</p>

- **Plane**: all cameras are positioned on a rectangular grid and rotated to look along the normal of the plane.
- **Cuboid**: the Plane setup is copied to the 6 faces of a cuboid.
- **Cylinder**: the Plane setup is wrapped around a cylinder.
- **Sphere**: each camera is positioned on a sphere and rotated to look along the normal of that sphere at its position. To get mostly evenly spaced cameras, the 3D positions of the vertices of an Icosphere are used.

## Requirements
Blender 2.80 or higher.

## Include in Blender
Blender requires access to the python files in this repository, so download or clone it:
```sh
$ git clone https://github.com/IDLabMedia/blender-lightfield-addon.git
```

Navigate to the directory in which Blender is installed, more specifically where the blender executable (`blender.exe` on Windows) is located, for example:
```sh
Windows: C:\Program Files\Blender Foundation\Blender
Linux: /usr/share/blender/
```
Then continue down to where the addons are stored, e.g. (the X.XX` symbolizes the version of your Blender install):
```sh
Windows: C:\Program Files\Blender Foundation\Blender\X.XX\scripts\addons
Linux: /usr/share/blender/X.XX/scripts/addons/
```
Create a new directory and copy all python files from this repository to that new directory. When opening Blender, go to `Edit > Preferences ... > Add-ons` and search for "6D Lightfield Renderer". Make sure the addon is enabled by checking the checkbox.
<p float="left">
	<img src="docs/addon_window.PNG" height="250"/>
</p>

## Usage
<img src="docs/settings.gif" />

To start using the addon in Blender, open the 3D Viewport view and type `N` to open the right Sidebar. You will see a new tab there, called `Lightfield`. 
<p float="left">
<img src="docs/blender_lightfield_tab1.PNG"  height="350"/>
</p>

Clicking the <img src="docs/plus_icon.PNG"  height="13"/> icon on the left of that opens a dropdown that allows you to select the desired camera setup. The options are: Lightfield Plane, Cuboid, Cylinder and Sphere. Selecting one creates a default camera setup of the chosen type. The setup can be configured in this Sidebar, as well as by going into the `Proporties` <img src="docs/properties_icon.PNG"  height="20"/> tab that is by default already open on the right side of Blender and selecting the `Object data properties` icon <img src="docs/data_properties_icon.PNG"  height="20"/>.
<p float="left">
<img src="docs/blender_lightfield_tab2.PNG"/>
</p>

Moving, rotating and scaling the camera setups can be done from the 3D Viewport. Changing the number of cameras and the camera intrinsics (resolution, focal length, etc.) is done in the `Object data properties` <img src="docs/data_properties_icon.PNG"  height="20"/>.

**Rendering**: in the right Sidebar of the 3D Viewport, under tab `Lightfield > Output`, set the desired output path. Then start the rendering process by pressing the `Render Lightfield` button at the top of the Sidebar. Blender will now render one image for each camera in the setup and store them in the output folder. 

**Image format**: by default, the output images are stored as PNG files. It is possible to also store the depth maps by selecting the checkbox next to `Depth (OpenEXR)` in the Sidebar. This will, for each camera, combine the output image and depth into one `.exr` file, where the first 3 channels contain the (red, green, blue) color data, and the fourth channel the depth (by default in meters). The OpenEXR files contain 16 bits of floating-point data per channel per pixel. [This reduces the actual “bit depth” to 10-bit, with a 5-bit power value and 1-bit sign](https://docs.blender.org/manual/en/latest/files/media/image_formats.html#openexr).

**Camera config file**: by pressing the `Render Lightfield` button, a `lightfield.cfg` and `lightfield.json` file are created, containing information about the camera intrinsics (lens type, projection type, sensor width, resolution, etc.), the camera setup type (Plane, Cuboid, Cylinder, Sphere), and the position and rotation of each camera according to the Blender axial system (Z up, right-handed).

**Compositing**: this addon also works when Compositing nodes are used.

