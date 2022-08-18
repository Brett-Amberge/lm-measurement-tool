import omni.ext
import omni.ui as ui
import omni.kit.commands
from pxr import Sdf, Gf

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print(f"[omni.hello.world] some_public_function was called with {x}")
    return x ** x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[omni.hello.world] MyExtension startup")

        self._window = ui.Window("Cut plane tool", width=300, height=300)

        def spawnPlane(isOn, axis):
            if isOn:
                omni.kit.commands.execute('CreateMeshPrimWithDefaultXform', prim_type='Plane')
                omni.kit.commands.execute('MovePrims',
	                paths_to_move={'/World/Plane': '/World/' + axis + 'Plane'})
            else:
                omni.kit.commands.execute('DeletePrims', paths=['/World/' + axis + 'Plane'])
                
        def plane_stack(lab, axis):
            with ui.HStack():
                label = ui.Label(lab)
                box = ui.CheckBox()
                box.model.add_value_changed_fn(lambda x: spawnPlane(box.model.get_value_as_bool(), axis))
                field = ui.MultiFloatDragField(0.0)
                field.model.add_item_changed_fn(lambda x,y: movePlane(box.model.get_value_as_bool(), axis))

        with self._window.frame:
            with ui.VStack():
                x = plane_stack("X-axis:", "X")
                y = plane_stack("Y-axis:", "Y")
                z = plane_stack("Z-axis:", "Z")

    def on_shutdown(self):
        print("[omni.hello.world] MyExtension shutdown")
