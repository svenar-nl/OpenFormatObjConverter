import os
import re
import sys

class Vertex:
    index = 0
    coordinates = [0, 0, 0]
    normal = [0, 0, 0]
    uv = [0, 0, 0]

    def __init__(self, index, coordinates, normal, uv) -> None:
        self.index = index
        self.coordinates = coordinates
        self.normal = normal
        self.uv = uv
    
    def get_v(self):
        coordinates = []
        for coord in self.coordinates:
            coordinates.append(str(coord))
        
        return "v " + " ".join(coordinates)
    
    def get_vn(self):
        normal = []
        for norm in self.normal:
            normal.append(str(norm))
        return "vn " + " ".join(normal)
    
    def get_vt(self):
        uv = []
        for uv_coord in self.uv:
            uv.append(str(uv_coord))
        return "vt " + " ".join(uv)
    
    def get_index(self):
        return self.index

class Face:
    vertices = []

    def __init__(self, vertices) -> None:
        self.vertices = vertices
    

    def get_f(self):
        return "f " + " ".join([str(vert.get_index() + 1) + "/" + str(vert.get_index() + 1) + "/" + str(vert.get_index() + 1) for vert in self.vertices])

class Mesh:
    index = 0
    vertex_offset = 0
    idx_data = []
    vert_data = []

    vertices = []
    faces = []
    material = None

    def __init__(self, index) -> None:
        self.index = index
        self.vertex_offset = 0
        self.idx_data = []
        self.vert_data = []
        self.vertices = []
        self.faces = []
    
    def set_vertex_offset(self, vertex_offset) -> None:
        self.vertex_offset = vertex_offset
    
    def add_idx(self, data) -> None:
        for id in data:
            self.idx_data.append(int(id))
    
    def add_vert(self, data) -> None:
        self.vert_data.append(data)
    
    def generate(self) -> None:
        vert_index = self.vertex_offset

        # print(str(self.index) + " - " + str(len(self.vert_data)))
        for raw_vert in self.vert_data:
            coord = raw_vert.split(" / ")[0].split(" ")
            for i in range(len(coord)):
                coord[i] = float(coord[i])
            
            normal = raw_vert.split(" / ")[1].split(" ")
            for i in range(len(normal)):
                normal[i] = float(normal[i])
            
            uv = raw_vert.split(" / ")[3].split(" ")
            if len(uv) != 2:
                uv = raw_vert.split(" / ")[4].split(" ")
            uv[0] = float(uv[0])
            uv[1] = -float(uv[1])
            # for i in range(len(uv)):
            #     uv[i] = float(uv[i])
            
            vertex = Vertex(vert_index, coord, normal, uv)
            self.vertices.append(vertex)
            vert_index += 1

        for i in range(0, len(self.idx_data), 3):
            v1 = self.vertices[self.idx_data[i]]
            v2 = self.vertices[self.idx_data[i + 1]]
            v3 = self.vertices[self.idx_data[i + 2]]

            face = Face([v1, v2, v3])
            self.faces.append(face)

class Material:
    name = ""
    Ka = [0, 0, 0]
    Kd = [0, 0, 0]
    Ks = [0, 0, 0]
    Ns = 0
    Ni = 0
    d = 0
    illum = 0
    map_Kd = ""
    map_bump = ""
    map_Ks = ""

    def __init__(self, name) -> None:
        self.name = name
        self.Ka = [0, 0, 0]
        self.Kd = [0, 0, 0]
        self.Ks = [0, 0, 0]
        self.Ns = 0
        self.Ni = 0
        self.d = 0
        self.illum = 0
        self.map_Kd = ""
        self.map_bump = ""
        self.map_Ks = ""
    
    def generate(self):
        if len(self.name) == 0:
            return ""
        
        mtl = ""
        mtl += "newmtl " + self.name + "\n"
        # mtl += "Ka " + " ".join([str(o) for o in self.Ka]) + "\n"
        # mtl += "Kd " + " ".join([str(o) for o in self.Kd]) + "\n"
        # mtl += "Ks " + " ".join([str(o) for o in self.Ks]) + "\n"
        # mtl += "Ns " + str(self.Ns) + "\n"
        # mtl += "Ni " + str(self.Ni) + "\n"
        # mtl += "d " + str(self.d) + "\n"
        # mtl += "illum " + str(self.illum) + "\n"
        if len(self.map_Kd) > 0:
            mtl += "map_Kd " + self.map_Kd + "\n"
        if len(self.map_bump) > 0:
            mtl += "map_bump " + self.map_bump + "\n"
        if len(self.map_Ks) > 0:
            mtl += "map_Ks " + self.map_Ks + "\n"
        mtl += "\n"
        return mtl

class MaterialParser:
    shaders = []
    def __init__(self, raw_shader_list) -> None:
        self.shaders = raw_shader_list
    
    def generate(self):
        materials = []

        index = 0
        for shader in self.shaders:
            material = Material("MAT_" + str(index))
            material.map_Kd = shader # TODO make something better
            materials.append(material)
            index += 1

        return materials

class MeshParser:
    mesh_file_lines = ""
    meshes = []
    materials = []

    def __init__(self, mesh_file_path, materials) -> None:
        self.meshes = []
        self.materials = materials

        with open(mesh_file_path) as f:
            self.mesh_file_lines = f.read()
    
    def generate(self, debug):
        self.mesh_file_lines = re.sub(r"\t", "", self.mesh_file_lines)
        depth = 0
        mesh = None
        in_idx = -1
        in_verts = -1

        mesh_index = -1
        for line in self.mesh_file_lines.splitlines():
            if "{" in line:
                depth += 1
            if "}" in line:
                depth -= 1

            if "mtl" in line.lower() or "geometry" in line.lower():
                
                if mesh is not None:
                    self.meshes.append(mesh)

                # mesh_index = int(re.sub(r"\D", "", line))
                mesh_index += 1
                # print(mesh_index)
                mesh = Mesh(mesh_index)
                try:
                    mesh.material = self.materials[mesh_index]
                except:
                    pass
                
            
            if "idx" in line.lower() or "indices" in line.lower():
                in_idx = depth + 1
                continue
            
            if "verts" in line.lower() or "vertices" in line.lower():
                in_verts = depth + 1
                continue
            
            if in_idx > 0:
                if depth < in_idx:
                    in_idx = -1
                if not "{" in line and not "}" in line:
                    mesh.add_idx(line.split(" "))
            
            if in_verts > 0:
                if depth < in_verts:
                    in_verts = -1
                if not "{" in line and not "}" in line:
                    mesh.add_vert(line)
        
        if mesh is not None:
            self.meshes.append(mesh)
        
        for i in range(len(self.meshes)):
            if i == 0:
                self.meshes[i].set_vertex_offset(0)
            else:
                index = i
                offset = 0
                while index > 0:
                    index -= 1
                    offset += len(self.meshes[index].vert_data)
                self.meshes[i].set_vertex_offset(offset)

        for mesh in self.meshes:
            mesh.generate()

        obj = ""

        for mesh in self.meshes:
            for vert in mesh.vertices:
                obj += vert.get_v() + "\n"
        
        for mesh in self.meshes:
            for vert in mesh.vertices:
                obj += vert.get_vn() + "\n"
        
        for mesh in self.meshes:
            for vert in mesh.vertices:
                obj += vert.get_vt() + "\n"
        
        for mesh in self.meshes:
            if mesh.material is not None:
                obj += "usemtl " + mesh.material.name + "\n"
            for face in mesh.faces:
                obj += face.get_f() + "\n"
        
        vert_count = 0
        face_count = 0
        material_count = 0
        for mesh in self.meshes:
            vert_count += len(mesh.vertices)
            face_count += len(mesh.faces)
            material_count += 1 if mesh.material is not None else 0
        
        mtl = ""
        for material in self.materials:
            mtl += material.generate()

        print("--------------------")
        print(f"Mesh count: {len(self.meshes)}")
        print(f"Vertex count: {vert_count}")
        print(f"Face count: {face_count}")
        print(f"Material count: {material_count}")
        print("--------------------")

        return {"obj": obj, "mtl": mtl}

def parse_odr(lines):
    odr_data = {"shaders": [], "skeletons": [], "lodgroup": {}}

    shadinggroups = []
    skeletons = ""

    # Shader groups
    regex_shadinggroup = r"(s|S)hadinggroup(\n|\s|){\n\t{0,1}(s|S)haders \d{1,999}\n\t{0,1}{\n\t{2}[^}]+}\n}"

    match_shadinggroup = re.search(regex_shadinggroup, lines)
    if match_shadinggroup:
        tmp_shadinggroups = match_shadinggroup[0]
        tmp_shadinggroups = re.sub(r"(s|S)hadinggroup(\n|\s|){\n\t{0,1}(s|S)haders \d{1,999}\n\t{0,1}{\n", "", tmp_shadinggroups)
        tmp_shadinggroups = re.sub(r"\n\t{0,2}}\n}", "", tmp_shadinggroups)
        tmp_shadinggroups = re.sub(r"\t", "", tmp_shadinggroups)
        tmp_shadinggroups = re.sub(r"\\", "/", tmp_shadinggroups)

        if len(tmp_shadinggroups) > 0:
            for shadinggroup in tmp_shadinggroups.splitlines():
                try:
                    shadinggroups.append(shadinggroup.split(" ")[1])
                except:
                    pass
    
    if len(shadinggroups) == 0:
        sps_data = []
        depth = 0
        sps_name = ""
        in_shaders = -1

        previous_line = ""

        for line in lines.splitlines():
            if "{" in line:
                depth += 1
            if "}" in line:
                depth -= 1
            
            if "shaders" in line.lower():
                in_shaders = depth + 1
                continue

            if depth < in_shaders:
                in_shaders = -1

            if in_shaders != -1:
                if "{" in line:
                    if not "{" in previous_line:
                        sps_name = re.sub(r"\t", "", previous_line)
                if "}" in line and len(sps_name) > 0:
                    sps_name = ""
                
                if len(sps_name) > 0:
                    if not "{" in line:
                        if "DiffuseSampler" in line:
                            sps_data.append(re.sub(r"\\", "/", re.sub(line.split(" ")[0], "", line).lstrip()).replace(".otx", ".png")) # TODO make something better
                        # sps_data[sps_name.replace(".", "")][re.sub(r"\t", "", line.split(" ")[0])] = re.sub(line.split(" ")[0], "", line)

            previous_line = line
        shadinggroups = sps_data
    # Shader groups

    # Skeletons
    regex_skeletons = r"(s|S)kel(eton|)((\n|\s|){\n\t{0,1}[\w\.\s\t\\\-]+\n}|[ \w\\\.\d\-]+)"

    match_skeletons = re.search(regex_skeletons, lines)
    if match_skeletons:
        skeletons = match_skeletons[0]
        skeletons = re.sub(r"(s|S)kel(eton|)(\n|\s|) {*", "", skeletons)
        skeletons = re.sub(r"\n}", "", skeletons)
        skeletons = re.sub(r"\t", "", skeletons)
        skeletons = re.sub(r"\\", "/", skeletons)
    
    new_skeletons = []
    for skel in skeletons.splitlines():
        if skel.lower().endswith(".skel"):
            new_skeletons.append(skel)
    skeletons = new_skeletons
    # Skeletons

    # LOD groups

    depth = 0
    in_lodgroup = -1
    lodgroup_lines = []

    for line in lines.splitlines():
        if "{" in line:
            depth += 1
        if "}" in line:
            depth -= 1
        
        if "lodgroup" in line.lower():
            in_lodgroup = depth + 1
            continue
        
        if in_lodgroup != -1:
            if depth < in_lodgroup:
                in_lodgroup = -1
            
            lodgroup_lines.append(line)

    lodgroup_lines = "\n".join(lodgroup_lines)
    regex_lod = r"(((h|H)igh)|((m|M)ed)|((l|L)ow)|((v|V)low)) [\d\.\w \\\-]+(\n\t+{\n\t+[\w\\\. \d]+\n\t+})*"

    match_lod = re.finditer(regex_lod, lodgroup_lines)
    if match_lod:
        for o in [x.group() for x in match_lod]:
            lod_type = o.split(" ")[0].lower()
            lod_value = ""
            if "{" in o:
                for t in o.split("\t"):
                    for tt in t.split(" "):
                        if tt.lower().endswith(".mesh"):
                            lod_value = re.sub(r"\\", "/", tt)
                            break
            else:
                for t in o.split(" "):
                    if t.lower().endswith(".mesh"):
                        lod_value = re.sub(r"\\", "/", t)
                        break

            if len(lod_value) > 0:
                odr_data["lodgroup"][lod_type] = lod_value

    # LOD groups

    if len(shadinggroups) > 0:
        odr_data["shaders"] = shadinggroups

    if len(skeletons) > 0:
        odr_data["skeletons"] = skeletons

    return odr_data

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Invalid arguments")
        exit(0)

    input_file_path = sys.argv[1]

    if not input_file_path.lower().endswith(".odr"):
        print("Input file must have a .odr extension")
        exit(0)

    # input_file_path = "input/barrierblocks/bm_barrier_blocks.odr"
    # input_file_path = "input/manhat/06x_mh1/06x_mh1_high.mesh"
    # input_file_path = "input/bagload/bm_air_bagload/bm_air_bagload_high.mesh"
    # input_file_path = "input/plank/bm_plank01/bm_plank01_high.mesh"

    with open(input_file_path) as f:
        raw_odr_lines = f.read()
    
    odr_data = parse_odr(raw_odr_lines)

    # print(odr_data)
    # exit(0)
    
    os.chdir(os.path.dirname(input_file_path))

    input_name, ext = os.path.splitext(os.path.basename(input_file_path))

    for lodgroup in odr_data["lodgroup"]:
        output_obj_name = input_name + "_" + lodgroup + ".obj"
        output_mtl_name = input_name + "_" + lodgroup + ".mtl"

        material_parser = MaterialParser(odr_data["shaders"])
        mesh_parser = MeshParser(odr_data["lodgroup"][lodgroup], material_parser.generate())

        model_data = mesh_parser.generate(True)

        obj_headers = "# Converted by OpenFormatConverter\n\n"
        obj_headers += f"mtllib {output_mtl_name}\n\n"

        mtl_headers = "# Converted by OpenFormatConverter\n\n"

        model_data["obj"] = obj_headers + model_data["obj"]
        model_data["mtl"] = mtl_headers + model_data["mtl"]

        with open(output_obj_name, "w") as f:
            f.write(model_data["obj"])
        
        with open(output_mtl_name, "w") as f:
            f.write(model_data["mtl"])