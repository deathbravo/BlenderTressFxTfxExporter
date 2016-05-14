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


import ctypes
import bpy
from mathutils import Vector, Matrix

def RoundF(a): 
    delta = 0.0001  # Round numbers up to 4 digits after decimal point
    d = 1/delta
    a = round(a*d)
    return a/d
	

def Dist_V_to_a_Face(v,f):
    v0 = f.v[0]
    v1 = f.v[1]
    v2 = f.v[2]
    vec1 = Mathutils.Vector(v0.co.x-v1.co.x,v0.co.y-v1.co.y,v0.co.z-v1.co.z)
    vec2 = Mathutils.Vector(v2.co.x-v1.co.x,v2.co.y-v1.co.y,v2.co.z-v1.co.z)
    A = vec1[1]*vec2[2]-vec1[2]*vec2[1]
    B = vec1[0]*vec2[2]-vec1[2]*vec2[0]
    C = vec1[0]*vec2[1]-vec1[1]*vec2[0]
    D = -(A*v0.co.x+B*v0.co.y+C*v0.co.z)
    m = 1/math.sqrt(A*A+B*B+C*C)
    if (D>0):
        m = -m
    cos_Alfa = m*A
    cos_Beta = m*B
    cos_Gamma = m*C
    p = -m*D
    Alfa = math.degrees(math.acos(cos_Alfa))
    Beta = math.degrees(math.acos(cos_Beta))
    Gamma = math.degrees(math.acos(cos_Gamma))
    d = abs(v.co.x*cos_Alfa+v.co.y*cos_Beta+v.co.z*cos_Gamma-p)
    d = RoundF(d)
    return d    
    

def Index_Vert_to_Faces(v,faces):
	fl = False
	d_min = 0
	fi_min = 0  
	for f in faces:
		d = Dist_V_to_a_Face(v,f)
		if fl:
			if (d_min > d):
				d_min = d
				fi_min = f.index
		else:
			d_min = d
			fl = True  
	return fi_min

class TressFXFileObject(ctypes.Structure):
	_fields_ = [('version', ctypes.c_float),
				('numHairStrands', ctypes.c_uint),
				('numVerticesPerStrand', ctypes.c_uint),
				('followToGuideStrandRatio', ctypes.c_uint),
				('bothEndsImmovable', ctypes.c_bool),
				('reserved1', ctypes.c_uint * 31),
				('verticesOffset', ctypes.c_uint),
				('perStrandThicknessOffset', ctypes.c_uint),
				('perStrandTexCoordOffset', ctypes.c_uint),
				('perVertexColorOffset', ctypes.c_uint),
				('guideHairStrandOffset', ctypes.c_uint),
				('perVertexTexCoordOffset', ctypes.c_uint),
				('reserved2', ctypes.c_uint * 32)]

class Point(ctypes.Structure):
	_fields_ = [('x', ctypes.c_float),
				('y', ctypes.c_float),
				('z', ctypes.c_float)]	

class TressFXSkinFileObject(ctypes.Structure):
	_fields_ = [('version', ctypes.c_uint),
				('numHairs', ctypes.c_uint),
				('numTriangles', ctypes.c_uint),
				('reserved1', ctypes.c_uint * 31), 
				('hairToMeshMap_Offset', ctypes.c_uint),
				('perStrandUVCoordniate_Offset', ctypes.c_uint),
				('reserved1', ctypes.c_uint * 31)]      
	
class HairToTriangleMapping(ctypes.Structure):
	_fields_ = [('mesh', ctypes.c_uint),
				('triangle', ctypes.c_uint),
				('barycentricCoord_x', ctypes.c_float),
				('barycentricCoord_y', ctypes.c_float),
				('barycentricCoord_z', ctypes.c_float),
				('reserved', ctypes.c_uint)]  
					
class TfxExporter:

	def SaveTFXBinaryFile(self,filepath, pss, locs):
		numCurves = 0
		numVerticesPerStrand = 9999
		
		npss = len(pss)
		for i in range(npss):
			ps = pss[i]
			pnum = len(ps.particles)
			curves = ps.particles
			
			numCurves = numCurves + pnum
			curveFn = curves[0]
			dz = len(curveFn.hair_keys)
			if(dz<numVerticesPerStrand):
				numVerticesPerStrand = dz
		
		#print (self.config["use_bothEndsImmovable"])
		print("total particles num:"+str(numCurves))
		

		rootPositions = []

		tfxobj = TressFXFileObject()
		tfxobj.version = 3.0
		tfxobj.numHairStrands = numCurves
		tfxobj.numVerticesPerStrand = numVerticesPerStrand
		tfxobj.followToGuideStrandRatio = 0
		tfxobj.bothEndsImmovable = 1 if self.config["use_bothEndsImmovable"] else 0
		tfxobj.verticesOffset = ctypes.sizeof(TressFXFileObject)
		tfxobj.perStrandThicknessOffset = 0
		tfxobj.perStrandTexCoordOffset = 0
		tfxobj.perVertexColorOffset = 0
		tfxobj.guideHairStrandOffset = 0
		tfxobj.perVertexTexCoordOffset = 0

		f = open(filepath, "wb")
		f.write(tfxobj)

		for i in range(npss):
			print("exporting particle system {}".format(i))
			ps = pss[i]
			loc = locs[i]
			pnum = len(ps.particles)
			curves = ps.particles
			print(loc)
			for j in range(pnum):
				curveFn = curves[j]
				#dz = len(curveFn.hair_keys)
				
				for k in range(0, numVerticesPerStrand):
					pos = loc+ curveFn.hair_keys[k].co
					#print(particle.hair_keys[k].co_local )
					#print(particle.hair_keys[k].co)
					p = Point()
					p.x = pos.x
					p.y = pos.y
					
					if(self.config["use_InvertZ"]):
						p.z = -pos.z # flip in z-axis
					else:
						p.z = pos.z

					f.write(p)
					
					# # root pos used to find face index
					if(k==0):
						rootPositions.append(pos)
						#print(pos)
						#print(curveFn.hair_keys[k].co_local )
						#print(curveFn.hair_keys[k].co)
						#print(loc + curveFn.hair_keys[k].co)
		
		f.close()
		
		return rootPositions	
	
  
			
	def SaveTFXSkinBinaryFile(filepath, faceIdList, baryCoordList, uvCoordList): 
		tfxSkinObj = TressFXSkinFileObject()
		tfxSkinObj.version = 1
		tfxSkinObj.numHairs = len(faceIdList)
		tfxSkinObj.numTriangles = 0
		tfxSkinObj.hairToMeshMap_Offset = ctypes.sizeof(TressFXSkinFileObject)
		tfxSkinObj.perStrandUVCoordniate_Offset = tfxSkinObj.hairToMeshMap_Offset + len(faceIdList) * ctypes.sizeof(HairToTriangleMapping)
		
		f = open(filepath, "wb")
		f.write(tfxSkinObj)
		
		for i in range(len(faceIdList)):
			mapping = HairToTriangleMapping()
			mapping.mesh = 0
			mapping.triangle = faceIdList[i]
			
			uvw = baryCoordList[i]
			mapping.barycentricCoord_x = uvw.x
			mapping.barycentricCoord_y = uvw.y
			mapping.barycentricCoord_z = uvw.z
			
			f.write(mapping)
			
		# per strand uv coordinate
		for i in range(len(uvCoordList)):
			uv_coord = uvCoordList[i]
			p = Point()
			p.x = uv_coord.x
			p.y = 1.0 - uv_coord.y # DirectX has it inverted
			p.z = uv_coord.z 
			
			f.write(p)    
		
		f.close()
		 
		return
	
	def get_particle_systems(self):
		for obj in self.scene.objects:
			if (obj.type=="MESH" ):  #selected objects system
				if( self.config["use_export_selected"] and not obj.select):
					continue
					
				nps = len(obj.particle_systems)
				print("mesh " + obj.name +" has particle system:" + str(nps))
				#print(obj.location)
				if(nps>0):
					for i in range(nps):
						ps = obj.particle_systems[i]
						if(ps!=None):
							if (not ps in self.valid_pss):
								self.valid_pss.append(ps)	
								self.co_pss.append(obj.location)
		return
		
	def export(self):
		#print("in TfxExporter.export 2")
		self.get_particle_systems()

		npss = len(self.valid_pss)
		print("particle sys num:"+ str(npss))
		
		ps = self.valid_pss[0]
		pnum = len(ps.particles)
		#print("particle num of 1st sys:"+str(pnum))
		
		self.SaveTFXBinaryFile(self.path , self.valid_pss, self.co_pss)

		#need to export skin?
		if(self.config["use_exportSkinCheckBox"] == False):
			return True
		
		#get the mesh used as base to grow hair or fur
		mesh = ps.parent
		if(mesh!=None):
			for i in range(len(rootPositions)):
				rootPoint = rootPositions[i]
				triangleId = Index_Vert_to_Faces(rootPoint,mesh.faces) # find the id of the nearest face 
				faceIdList.append(triangleId)
				
				#barycentric list
			
				#UV list
			
			#SaveTFXSkinBinaryFile
			
		return True

	def __init__(self,path,keys,operator):
		self.valid_pss=[]	#valid particle systems
		self.co_pss=[]	#location of particle systems
		self.path=path
		self.scene=bpy.context.scene
		self.config=keys



def save(operator, context,
	filepath="",
	use_selection=False,
	**keys
	):
	#print("in export_tfx.save")
	exp = TfxExporter(filepath,keys,operator)
	exp.export()


	return {'FINISHED'}  


