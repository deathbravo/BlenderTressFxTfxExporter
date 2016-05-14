#-----------------------------------------------------------------------------
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#-----------------------------------------------------------------------------

bl_info = {
    "name": "TressFX tfx Exporter",
    "author": "deathbravo",
    "blender": (2, 74, 0),
    "location": "File > Import-Export",
    "description": ("Export tfx from particle hair."),
    "warning": "",
    "wiki_url": (""),
    "tracker_url": "",
    "category": "Import-Export"}


if "bpy" in locals():
    import imp
    if "export_tfx" in locals():
        imp.reload(export_tfx)


import bpy
from bpy.props import StringProperty, BoolProperty

from bpy_extras.io_utils import (ExportHelper,
                                 path_reference_mode,
                                 axis_conversion,
                                 )


class ExportTFX(bpy.types.Operator, ExportHelper):
    '''Selection to TFX'''
    bl_idname = "export_scene.tfx"
    bl_label = "Export TFX"
    bl_options = {'PRESET'}

    filename_ext = ".tfx"
    filter_glob = StringProperty(default="*.tfx", options={'HIDDEN'})


    use_export_selected = BoolProperty(
            name="Selected Objects",
            description="Export only selected objects (and visible in active layers if that applies).",
            default=True,
            )
 
    use_bothEndsImmovable = BoolProperty(
            name="Both ends immovable",
            description="",
            default=False,
            )

    use_InvertZ = BoolProperty(
            name="Invert Z",
            description="",
            default=False,
            )	

    use_exportSkinCheckBox = BoolProperty(
            name="Export skin data",
            description="",
            default=False,
            )
			
    use_randomStrandCheckBox = BoolProperty(
            name="Randomize strands for LOD",
            description="",
            default=True,
            )


    @property
    def check_extension(self):
        return True#return self.batch_mode == 'OFF'

    def check(self, context):
        return True


    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")


        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            "xna_validate",
                                            ))

        from . import export_tfx
        return export_tfx.save(self, context, **keywords)


def menu_func(self, context):
    self.layout.operator(ExportTFX.bl_idname, text="TressFX (.tfx)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
