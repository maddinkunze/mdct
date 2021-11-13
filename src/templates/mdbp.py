import bpy, json, os, mathutils
import numpy as np
from bpy_extras.io_utils import ImportHelper
# from mathutils import Color


############################
## ---------------------- ##
## --- Misc functions --- ##
## ---------------------- ##
############################

def _rgetattr(obj, parts):
    for part in parts:
        obj = getattr(obj, part)
    return obj

def rsetattr(obj, path, value):
    parts = path.split(".")
    obj = _rgetattr(obj, parts[:-1])
    setattr(obj, parts[-1], value)

def rgetattr(obj, path):
    parts = path.split(".")
    return _rgetattr(obj, parts)

############################
## ---------------------- ##
## --- Init functions --- ##
## ---------------------- ##
############################


# ------------------------ #
# --- Driver functions --- #
# ------------------------ #


def update_drivers():
    for obj in (bpy.data.node_groups.values() + bpy.data.objects.values() + bpy.data.materials.values()):
        if obj.animation_data:
            for driver in obj.animation_data.drivers:
                exp = driver.driver.expression
                driver.driver.expression = exp[:]  # Create independet copy


def create_update_variables_function(options):
    def update_variables(scene):
        std_variables = options["options"]["environments"]["variables"]
        for variable in std_variables:
            bpy.app.driver_namespace[variable] = eval(std_variables[variable])
            
        if scene.name in options["environments"].keys():
            env_variables = options["environments"][scene.name]["variables"]
            for variable in env_variables:
                bpy.app.driver_namespace[variable] = eval(env_variables[variable])
            
        # update_drivers()
        
    return update_variables


def add_app_handler(handler, function):
    function_list = getattr(bpy.app.handlers, handler)
    for f in function_list:
        if f.__name__ == function.__name__:
            function_list.remove(f)
    function_list.append(function)


def create_random_function():
    class Random:
        def __init__(self, frame=0, variation=10000):
            self.frame = frame
            self.seed = mathutils.noise.random() * variation
            self.random = 0
            self.change(frame)
        def change(self, frame=0):
            self.random = (mathutils.noise.cell((frame, self.seed, 0)) + 1) / 2  # Returns [-1; 1] - +1 -> [0; 2] - /2 -> [0; 1]
            self.frame = frame
    
    def get_key(obj_or_id):
        if isinstance(obj_or_id, bpy.types.Object):
            key = "object:" + obj_or_id.name_full
            
        elif isinstance(obj_or_id, str):
            key = "string:" + obj_or_id
            
        elif isinstance(obj_or_id, int):
            key = "int:" + str(obj_or_id)
            
        elif isinstance(obj_or_id, float):
            key = "float:" + str(obj_or_id)
            
        else:
            key = "other:" + str(obj_or_id)
            
        return key
    
    objects = {}
    def random_val(obj_or_id, frame):
        key = get_key(obj_or_id)
        if not key in objects.keys():
            objects[key] = Random()
        objects[key].change(frame)
        return objects[key].random
        
    return random_val


def create_srgb_function():
    def srgb(c):
        a = .055
        if c <= .04045:
            return c / 12.92
        else:
            return ((c + a) / (1 + a)) ** 2.4

    return srgb


def random_particle_count(obj, seed_value, count_value):
    obj.settings.count = count_value
    return seed_value
        

def register_driver_namespace():
    bpy.app.driver_namespace["label"] = 0  # Currently showing label colors/textures
    bpy.app.driver_namespace["random"] = create_random_function()  # Unique random number for whole frame
    bpy.app.driver_namespace["srgb"] = create_srgb_function()  # Blenders weird color transform -> gamma curves etc.
    # bpy.app.driver_namespace["random_particle_count"] = random_particle_count  # Allowing randomisation of particle count (mainly for Hair)


# ------------------------ #
# --- Create functions --- #
# ------------------------ #

scenes = []

def create_scene(name, options):
    if bpy.data.scenes.find(name) != -1:
        bpy.data.scenes.remove(bpy.data.scenes[name])
        
    scene_options = get_clean_options("environments", name, options)
        
    scene = bpy.data.scenes.new(name)
    scene.frame_end = scene_options["frames"]
    scene.render.resolution_x = scene_options["size"][0]
    scene.render.resolution_y = scene_options["size"][1]
    render_path = os.path.join(scene_options["path"], name)
    if not os.path.isabs(render_path):
        render_path = "//" + render_path
    scene.render.filepath = render_path
    inscenes = False
    for _scene in scenes:
        if _scene.name == name:
            inscenes = True
    if not inscenes:
        scenes.append(scene)
    
    for setting in scene_options["settingsScene"]:
        setting_options = get_clean_options("settingsScene", setting, scene_options)
        set_scene_settings(scene, setting_options)
    
    create_view_layers(scene, options["options"]["environments"]["layers"])
    create_collections(scene, options["options"]["environments"]["collections"])
    create_world(scene, name, options)
    create_env_objects(scene, name, options)
    
    render_path = os.path.join(options["directory"], scene_options["path"])
    if not os.path.isabs(render_path):
        render_path = "//" + render_path
    create_compositing_node_tree(scene, scene_options["compositorPreset"], scene_options["compositorValues"], render_path)


def set_scene_settings(scene, setting_options):
    setting_names = {}
    if setting_options["type"] == "bloom":
        setting_names = {"enabled": "eevee.use_bloom", "radius": "eevee.bloom_radius", "intensity": "eevee.bloom_intensity", "threshold": "eevee.bloom_threshold"}
    elif setting_options["type"] == "gtao":  # Ambient Occlustion
        setting_names = {"enabled": "eevee.use_gtao", "distance": "eevee.gtao_distance"}
    elif setting_options["type"] == "ssr":  # Screen Space Reflections
        setting_names = {"enabled": "eevee.use_ssr", "halfRes": "eevee.use_ssr_halfres", "refraction": "eevee.use_ssr_refraction"}

    for setting_name in setting_names:
        if setting_name in setting_options.keys():
            rsetattr(scene, setting_names[setting_name], setting_options[setting_name])

    
def create_view_layers(scene, layers, delete_others=True):
    layers_to_delete = scene.view_layers.values()  # Shoud only contain "View Layer", but just in case
    
    for layer in layers:
        create_view_layer(scene, layer["name"], layer["passes"])
    
    for layer in layers_to_delete:
        scene.view_layers.remove(layer)
        

def create_view_layer(scene, name, passes):
    if scene.view_layers.find(name) != -1:
        scene.view_layers.remove(scene.view_layers[name])
        
    view_layer = scene.view_layers.new(name)
    
    pass_attributes = {"Ambient Occlusion":"use_pass_ambient_occlusion", "Combined":"use_pass_combined", "Specular Light":"use_pass_glossy_direct", "Emission":"use_pass_emit", "Environment":"use_pass_environment", "Shadow":"use_pass_shadow", "Bloom": "eevee.use_pass_bloom", "Z":"use_pass_z"}
    
    for pass_attribute in pass_attributes:
        rsetattr(view_layer, pass_attributes[pass_attribute], False)
        if pass_attribute in passes:
            rsetattr(view_layer, pass_attributes[pass_attribute], True)


def create_world(scene, id, options):
    if bpy.data.worlds.find(id) != -1:
        bpy.data.worlds.remove(bpy.data.worlds[id])
        
    world = bpy.data.worlds.new(id)
    scene.world = world
    
    world.use_nodes = True
    create_world_background(world, id, options)


def create_world_background(world, id, options):
    if options["environments"][id]["type"] == "360image":
        create_world_background_360image(world, id, options) # Defined in Node functions
    elif options["environments"][id]["type"] == "360imagelabel":
        create_world_background_360imagelabel(world, id, options) # Defined in Node functions
    elif options["environments"][id]["type"] == "360imagelabeljson":
        create_world_background_360imagelabeljson(world, id, options) # Defined in Node functions
    elif options["environments"][id]["type"] == "360imagecolor":
        create_world_background_360imagecolor(world, id, options) # Defined in Node functions


def create_env_objects(scene, env_id, options):
    cameras = options["environments"][env_id]["objects"]["cameras"]
    for cam_id in cameras:
        create_env_camera(scene, env_id, cam_id, options["environments"][env_id]["objects"])

    lights = options["environments"][env_id]["objects"]["lights"]
    for light_id in lights:
        create_env_light(scene, env_id, light_id, options["environments"][env_id]["objects"])

    meshes = options["environments"][env_id]["objects"]["meshes"]
    for mesh_id in meshes:
        create_env_mesh(scene, env_id, mesh_id, options["environments"][env_id]["objects"])


def create_env_camera(scene, env_id, cam_id, options):
    cam_options = get_clean_options("cameras", cam_id, options)
    name = create_name(env_id, cam_id, "cameras")
    if bpy.data.cameras.find(name) != -1:
        bpy.data.cameras.remove(bpy.data.cameras[name])
                
    camera = bpy.data.cameras.new(name)
    camera_obj = create_new_object(name, camera)
    scene.camera = camera_obj
    
    add_driver_to_obj(camera_obj, "location", cam_options["position"][0], index=0)  # index=0 -> X
    add_driver_to_obj(camera_obj, "location", cam_options["position"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(camera_obj, "location", cam_options["position"][2], index=2)  # index=2 -> Z
    
    add_driver_to_obj(camera_obj, "rotation_euler", cam_options["rotation"][0], index=0)  # index=0 -> X
    add_driver_to_obj(camera_obj, "rotation_euler", cam_options["rotation"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(camera_obj, "rotation_euler", cam_options["rotation"][2], index=2)  # index=2 -> Z
    
    add_driver_to_obj(camera, "lens", cam_options["focal"])
    
    for collection in scene.collection.children:
        if remove_name(env_id, collection.name, "collections") in cam_options["collections"]:
            collection.objects.link(camera_obj)


def create_env_light(scene, env_id, light_id, options):
    light_options = get_clean_options("lights", light_id, options)
    name = create_name(env_id, light_id, "lights")
    
    if bpy.data.lights.find(name) != -1:
        bpy.data.lights.remove(bpy.data.lights[name])
    
    light_types = {"point": "POINT", "area": "AREA", "sun": "SUN"}
    
    light = bpy.data.lights.new(name, light_types[light_options["type"]])
    light_obj = create_new_object(name, light)
    
    add_driver_to_obj(light_obj, "location", light_options["position"][0], index=0)  # index=0 -> X
    add_driver_to_obj(light_obj, "location", light_options["position"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(light_obj, "location", light_options["position"][2], index=2)  # index=2 -> Z
    
    add_driver_to_obj(light_obj, "rotation_euler", light_options["rotation"][0], index=0)  # index=0 -> X
    add_driver_to_obj(light_obj, "rotation_euler", light_options["rotation"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(light_obj, "rotation_euler", light_options["rotation"][2], index=2)  # index=2 -> Z

    add_driver_to_obj(light, "energy", light_options["power"])
    if light_options["type"] == "point":
        add_driver_to_obj(light, "shadow_soft_size", light_options["size"])
    elif light_options["type"] == "area":
        shapes = {"Rectangle": "RECTANGLE", "Ellipse": "ELLIPSE"}
        light.shape = shapes[light_options["shape"]]
        add_driver_to_obj(light, "size", light_options["dimensions"][0])
        add_driver_to_obj(light, "size_y", light_options["dimensions"][1])
    elif light_options["type"] == "sun":
        pass  # no options for suns
    light.use_contact_shadow = True
    
    for collection in scene.collection.children:
        if remove_name(env_id, collection.name, "collections") in light_options["collections"]:
            collection.objects.link(light_obj)


def create_env_mesh(scene, env_id, mesh_id, options):
    mesh_options = get_clean_options("meshes", mesh_id, options)
    name = create_name(env_id, mesh_id, "meshes")
    
    if bpy.data.meshes.find(name) != -1:
        bpy.data.meshes.remove(bpy.data.meshes[name])
    
    if mesh_options["type"] == "simple":
        mesh_obj = create_env_mesh_simple(name, mesh_options)
    elif mesh_options["type"] == "catcherShadowSimple":
        mesh_obj = create_env_mesh_shadow_catcher_simple(name, mesh_options)
    elif mesh_options["type"] == "catcherShadowMesh":
        mesh_obj = create_env_mesh_shadow_catcher_mesh(name, mesh_options)
    elif mesh_options["type"] == "catcherReflectionSimple":
        mesh_obj = create_env_mesh_reflection_catcher_simple(name, mesh_options)
    elif mesh_options["type"] == "catcherReflectionMesh":
        mesh_obj = create_env_mesh_reflection_catcher_mesh(name, mesh_options)
    elif mesh_options["type"] == "emitterParticlesSimple":
        mesh_obj = create_env_mesh_emitter_particles_simple(name, mesh_options)
    elif mesh_options["type"] == "emitterObjectsSimple":
        mesh_obj = create_env_mesh_emitter_objects_simple(name, mesh_options)
    else:
        print("│ Warning: Object", mesh_id, "of type", mesh_options["type"], "cannot be added.")
        print("└        : Object type doesn't exist (yet). You may need to update.")
        print()
        return
                    
    for collection in scene.collection.children:
        if remove_name(env_id, collection.name, "collections") in mesh_options["collections"]:
            collection.objects.link(mesh_obj)


def create_env_mesh_simple(name, options):
    mesh = bpy.data.meshes.new(name)
    mesh_obj = create_new_object(name, mesh)
    return mesh_obj


def create_env_mesh_shadow_catcher_simple(name, mesh_options):
    mesh = create_mesh_plane(name, mesh_options["dimensions"][0], mesh_options["dimensions"][1])
    mesh_obj = create_new_object(name, mesh)
    
    add_driver_to_obj(mesh_obj, "scale", mesh_options["scale"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "scale", mesh_options["scale"][1], index=1)  # index=1 -> Y
    
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][2], index=2)  # index=2 -> Z
    
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][2], index=2)  # index=2 -> Z

    return mesh_obj


def create_env_mesh_shadow_catcher_mesh(name, mesh_options):
    mesh = bpy.data.meshes.new(name)
    mesh_obj = create_new_object(name, mesh)
    return mesh_obj


def create_env_mesh_reflection_catcher_simple(name, mesh_options):
    mesh = create_mesh_plane(name, mesh_options["dimensions"][0], mesh_options["dimensions"][1])
    mesh_obj = create_new_object(name, mesh)
    
    add_driver_to_obj(mesh_obj, "scale", mesh_options["scale"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "scale", mesh_options["scale"][1], index=1)  # index=1 -> Y
    
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][2], index=2)  # index=2 -> Z
    
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][2], index=2)  # index=2 -> Z

    material = create_reflection_catcher_material(name, mesh_options["materialPreset"], mesh_options["materialValues"])
    mesh.materials.append(material)

    return mesh_obj


def create_env_mesh_reflection_catcher_mesh(name, mesh_options):
    mesh = create_mesh_plane(name, mesh_options["dimensions"][0], mesh_options["dimensions"][1])
    mesh_obj = create_new_object(name, mesh)
    return mesh_obj


def create_env_mesh_emitter_particles_simple(name, mesh_options):
    mesh = create_mesh_plane(name, mesh_options["dimensions"][0], mesh_options["dimensions"][1])
    mesh_obj = create_new_object(name, mesh)

    add_driver_to_obj(mesh_obj, "scale", mesh_options["scale"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "scale", mesh_options["scale"][1], index=1)  # index=1 -> Y
    
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][2], index=2)  # index=2 -> Z
    
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][2], index=2)  # index=2 -> Z

    modifier = mesh_obj.modifiers.new(name, "PARTICLE_SYSTEM")
    particle_system = modifier.particle_system
    particles = particle_system.settings
    
    particles

    return mesh_obj


def create_env_mesh_emitter_objects_simple(name, mesh_options):
    mesh = create_mesh_plane(name, mesh_options["dimensions"][0], mesh_options["dimensions"][1])
    mesh_obj = create_new_object(name, mesh)

    add_driver_to_obj(mesh_obj, "scale", mesh_options["scale"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "scale", mesh_options["scale"][1], index=1)  # index=1 -> Y
    
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(mesh_obj, "location", mesh_options["position"][2], index=2)  # index=2 -> Z
    
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][0], index=0)  # index=0 -> X
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][1], index=1)  # index=1 -> Y
    add_driver_to_obj(mesh_obj, "rotation_euler", mesh_options["rotation"][2], index=2)  # index=2 -> Z

    if bpy.data.particles.find(name) != -1:
        bpy.data.particles.remove(bpy.data.particles[name])

    modifier = mesh_obj.modifiers.new(name, "PARTICLE_SYSTEM")
    particle_system = modifier.particle_system
    particles = particle_system.settings
    
    particles.type = "HAIR"
    particles.use_advanced_hair = True
    particles.hair_length = 1
    particles.use_rotation_instance = True  # Object Rotation checkbox
    particles.use_rotations = True  # Rotation checkbox
    particles.rotation_mode = "NOR_TAN"  # Orientation Axis
    particles.use_emit_random = True  # Random Order checkbox
    particles.use_collection_pick_random = True  # Pick Random checkbox
    particles.render_type = "COLLECTION"
    particles.count = int(mesh_options["number"])
    
    driver_seed = particle_system.driver_add("seed")
    driver_seed.driver.use_self = True
    driver_seed.driver.expression = mesh_options["seed"]
    
    add_driver_to_obj(mesh_obj, "show_instancer_for_render", mesh_options["emitterShow"])
    add_driver_to_obj(particles, "rotation_factor_random", mesh_options["rotationRandom"])
    add_driver_to_obj(particles, "phase_factor", mesh_options["phase"])
    add_driver_to_obj(particles, "phase_factor_random", mesh_options["phaseRandom"])
    add_driver_to_obj(particles, "particle_size", mesh_options["sizeObjects"])
    add_driver_to_obj(particles, "size_random", mesh_options["sizeRandom"])
    
    if mesh_options["group"]:
        particles.instance_collection = bpy.data.collections[create_group_name(mesh_options["group"])]

    return mesh_obj


def create_mesh_plane(name, width=1, length=1):
    verts = [[0.5*width, 0.5*length, 0], [-0.5*width, 0.5*length, 0], [-0.5*width, -0.5*length, 0], [0.5*width, -0.5*length, 0]]
    edges = [[0, 1], [1, 2], [2, 3], [3, 0]]
    faces = [[0, 1, 2, 3]]
    mesh = create_mesh_from_pydata(name, verts, edges, faces)
    return mesh


def create_mesh_from_pydata(name, verts, edges, faces):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    mesh.uv_layers.new(name="PyData UV Layer")
    mesh.update()
    return mesh


def create_new_object(name, data):
    if bpy.data.objects.find(name) != -1:
        delete_object_completely(bpy.data.objects[name])
        
    obj = bpy.data.objects.new(name, data)
    return obj


def create_collections(scene, collections):
    for collection in collections:
        create_collection(scene, collection)


def create_collection(scene, options):
    name = create_name(scene.name, options["name"], "collections")  # To make it unique...
    if bpy.data.collections.find(name) != -1:
        bpy.data.collections.remove(bpy.data.collections[name])
        
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    change_collection_layers(scene, name, options["layers"])
    

def change_collection_layers(scene, name, layers):
    for layer in scene.view_layers:
        collection = layer.layer_collection.children[name]

        if layer.name in layers:
            collection.exclude = False
        else:
            collection.exclude = True


def create_group_name(name):
    return name + " (object group)"


def create_name(id, name, type):
    return id + " " + name + " (" + type + ")"


def remove_name(id, name, type):
    return name[len(id+" "):-len(" ("+type+")")]


def create_object_groups(options):
    object_groups = options["options"]["objects"]["groups"]
    
    for obj_group in object_groups:
        create_object_group(obj_group)


def create_object_group(options):
    name = create_group_name(options["name"])
    if bpy.data.collections.find(name) != -1:
        bpy.data.collections.remove(bpy.data.collections[name])
        
    bpy.data.collections.new(name)


def create_object(obj_id, options):
    if options["objects"][obj_id]["type"] == "blenderobject":
        create_object_blenderobject(obj_id, options)


def create_object_blenderobject(obj_id, options):
    obj_options = get_clean_options("objects", obj_id, options)
    
    filepath = os.path.join(options["directory"], obj_options["source"])
    
    with bpy.data.libraries.load(filepath) as (data_in, data_out):
        data_out.objects = [obj_options["object"]]
        
    for obj in data_out.objects:
        obj_name = create_name(obj_id, obj_options["object"], "object")
        if bpy.data.objects.find(obj_name) != -1:
            delete_object_completely(bpy.data.objects[obj_name])
            
        obj.name = obj_name
        obj.rotation_euler.y += 1.57  # Blenders particle system uses weird rotation -> rotate 90deg to avoid weirdness
        for group_name in obj_options["groups"]:
            bpy.data.collections[create_group_name(group_name)].objects.link(obj)

        if obj.type == 'MESH':
            materials = obj.data.materials
            annid = obj_options["annid"]
            if not materials:
                matname = create_name(obj_id, obj_options["object"], "material")
                material = bpy.data.materials.new(matname)
                materials.append(material)

            for material in materials:
                if not material.use_nodes:
                    material.use_nodes = True
                    for node in material.node_tree.nodes:
                        if node.type == "BSDF_PRINCIPLED":
                            material.node_tree.nodes.inputs["Base Color"] = material.specular_color
                            material.node_tree.nodes.inputs["Metallic"] = material.metallic
                            material.node_tree.nodes.inputs["Specular"] = material.specular_intensity
                            material.node_tree.nodes.inputs["Roughness"] = material.roughness
                            break

                for node in material.node_tree.nodes:
                    if node.type == "OUTPUT_MATERIAL":
                        switch = add_node_group_to_node_tree(material.node_tree, "Image/Label Switch Object")

                        for link in material.node_tree.links:
                            if link.to_socket == node.inputs[0]:
                                material.node_tree.links.new(link.from_socket, switch.inputs[0])
                                material.node_tree.links.remove(link)

                            elif link.to_socket == node.inputs[1]:
                                material.node_tree.links.new(link.from_socket, switch.inputs[1])
                                material.node_tree.links.remove(link)

                        material.node_tree.links.new(switch.outputs[0], node.inputs[0])
                        material.node_tree.links.new(switch.outputs[1], node.inputs[1])
                        drivers = switch.inputs["Color"].driver_add("default_value")
                        for i in range(3):
                            drivers[i].driver.expression = "srgb((" + annid + ") / 255)"  # srgb() to convert from linear to srgb curve
                        if len(drivers) == 4:
                            drivers[3].driver.expression = "1"  # alpha value, if needed


def delete_object_completely(obj):
    if obj.data in bpy.data.meshes.values():  # If obj contains (is) mesh
        for material in obj.data.materials:
            if material and (material.users <= 1):
                for node in material.node_tree.nodes:
                    if hasattr(node, "image") and node.image:
                        bpy.data.images.remove(node.image)
                    if node.type == "GROUP" and node.node_tree:
                        bpy.data.node_groups.remove(node.node_tree)
                bpy.data.materials.remove(material)
        bpy.data.meshes.remove(obj.data)
        
    elif obj.data in bpy.data.cameras.values():
        bpy.data.cameras.remove(obj.data)
        
    try:
        bpy.data.objects.remove(obj)
    except:
        pass


def add_custom_property(object, name, value=0, min=0, max=10, description=""):
    object[name] = value
    object["_RNA_UI"][name] = {"description":description, "default": value, "min":min, "max":max}


def add_driver_to_obj(obj, path, expression, index=0):
    animdata = obj.animation_data
    if not animdata:
        animdata = obj.animation_data_create()
        
    for driver in animdata.drivers:
        if (driver.data_path == path) and (driver.array_index == index):
            animdata.drivers.remove(driver)
    
    driver = animdata.drivers.new(path, index=index)
    driver.driver.type = "SCRIPTED"
    driver.driver.use_self = True
    driver.driver.expression = expression


# ---------------------- #
# --- Draw functions --- #
# ---------------------- #


def img_draw_polygon_bu(imgarray, points, color, size):
    ch = len(color)
    w, h = size

    points = np.array(points)
    min_x = max(int(points[..., 0].min()), 0)
    min_y = max(int(points[..., 1].min()), 0)
    max_x = min(int(points[..., 0].max()), w - 1)
    max_y = min(int(points[..., 1].max()), h - 1)

    array = np.zeros(size)
    change = np.zeros(size)

    lpoint = points[-1]
    lpoint[0] = max(min(lpoint[0], w - 1), 0)
    lpoint[1] = max(min(lpoint[1], h - 1), 0)
    x, y = 0, 0
    fx, fy = 0, 0
    direction = 0  # -1: fy > ly  1: fy < ly
    for point in points:
        d = int(np.sqrt((lpoint[0] - point[0]) ** 2 + (lpoint[1] - point[1]) ** 2) * 2)
        point[0] = max(min(point[0], w - 1), 0)
        point[1] = max(min(point[1], h - 1), 0)
        lx, ly = int(lpoint[0]), int(lpoint[1])
        for i in range(d):
            x = (point[0] - lpoint[0]) * ((i + 1) / d) + lpoint[0]
            y = (point[1] - lpoint[1]) * ((i + 1) / d) + lpoint[1]
            x, y = int(x), int(y)
            array[x, y] = 1

            change[x, y] = 1

            if not i:
                fx, fy = x, y

            if ly == y:
                if lx != x:
                    change[lx, ly] = 0

            lx, ly = x, y

        ndir = (-1 if fy > ly else 1) if fy != ly else direction

        if ndir != direction:
            change[fx, fy] = 1
            change[lx, ly] = 0
            # print(fx, h-fy)

        direction = ndir

        lpoint = point

    for y in range(min_y, max_y + 1):
        curdrawing = False
        for x in range(min_x, max_x + 1):
            if change[x, y]:
                curdrawing = not curdrawing

            if curdrawing:
                array[x, y] = 1

    array = np.rot90(array).flatten()
    colors = np.array(color * w * h)
    mask = array.repeat(ch)
    return np.where(mask, colors, imgarray)


def img_draw_polygon(imgarray, points, color):
    w = imgarray.shape[0]
    if not len(points):
        return
    min_y = int(max(0, min(y for y, x in points)))
    max_y = int(min(w, max(y for y, x in points)))
    polygon = [(float(y), float(x)) for y, x in points]
    if max_y < imgarray.shape[0]:
        max_y += 1
    for y in range(min_y, max_y):
        nodes = []
        j = -1
        for i, p in enumerate(polygon):
            pj = polygon[j]
            if (p[0] < y <= pj[0]) or (pj[0] < y <= p[0]):
                dy = pj[0] - p[0]
                if dy:
                    nodes.append((p[1] + (y-p[0])/(pj[0]-p[0])*(pj[1]-p[1])))
                elif p[0] == y:
                    nodes.append(p[1])
            j = i
        nodes.sort()
        for n, nn in zip(nodes[::2], nodes[1::2]):
            nn += 1
            imgarray[y, int(n):int(nn)] = color

# ---------------------- #
# --- Node functions --- #
# ---------------------- #


def exists_node_group_by_name(name):
    for node_group in bpy.data.node_groups.values():
        if node_group.name == name:
            return True
    
    return False


def delete_all_nodes(node_tree):
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)


def add_driver_node(nodes, value, type="ShaderNode"):
    if isinstance(value, (list, tuple)):
        node_value = nodes.new(type + "RGB")
        drivers = node_value.outputs[0].driver_add("default_value")
        for index, val in enumerate(value):
            driver = drivers[index]
            driver.driver.use_self = True
            driver.driver.expression = value[index]
    else:
        node_value = nodes.new(type + "Value")
        driver = node_value.outputs[0].driver_add("default_value")
        driver.driver.use_self = True
        driver.driver.expression = value
        
    return node_value

        
def create_world_background_360image(world, env_id, options):
    delete_all_nodes(world.node_tree)
    nodes = world.node_tree.nodes
    
    env_options = get_clean_options("environments", env_id, options)
    
    node_output = nodes.new("ShaderNodeOutputWorld")
    node_switch = add_node_group_to_node_tree(world.node_tree, "Image/Label Switch World")
    node_image = nodes.new("ShaderNodeTexEnvironment")
    node_random = add_driver_node(nodes, env_options["strength"])

    node_output.location = (600, 0)
    node_switch.location = (400, 0)
    node_image.location = (0, 0)
    node_random.location = (-220, 0)
    
    world.node_tree.links.new(node_switch.outputs[0], node_output.inputs[0])
    world.node_tree.links.new(node_image.outputs[0], node_switch.inputs[0])
    world.node_tree.links.new(node_random.outputs[0], node_switch.inputs[2])
    
    image_name = create_name(env_id, "Image", "env_image")
    if bpy.data.images.find(image_name) != -1:
        bpy.data.images.remove(bpy.data.images[image_name])
        
    img_image = bpy.data.images.load(os.path.join(options["directory"], options["environments"][env_id]["image"]))
    img_image.name = image_name
    img_image.colorspace_settings.name = env_options["colorspaceImage"]
    node_image.image = img_image
    node_switch.inputs[1].default_value = (0, 0, 0, 1)  # Set default Color to black (1 = Alpha)
    
    
def create_world_background_360imagelabel(world, env_id, options):
    delete_all_nodes(world.node_tree)
    nodes = world.node_tree.nodes
    
    env_options = get_clean_options("environments", env_id, options)
    
    node_output = nodes.new("ShaderNodeOutputWorld")
    node_switch = add_node_group_to_node_tree(world.node_tree, "Image/Label Switch World")
    node_image = nodes.new("ShaderNodeTexEnvironment")
    node_label = nodes.new("ShaderNodeTexEnvironment")
    node_random = add_driver_node(nodes, env_options["strength"])
    
    node_output.location = (600, 0)
    node_switch.location = (400, 0)
    node_image.location = (0, 0)
    node_label.location = (0, -220)
    node_random.location = (0, -440)
    
    world.node_tree.links.new(node_switch.outputs[0], node_output.inputs[0])
    world.node_tree.links.new(node_image.outputs[0], node_switch.inputs[0])
    world.node_tree.links.new(node_label.outputs[0], node_switch.inputs[1])
    world.node_tree.links.new(node_random.outputs[0], node_switch.inputs[2])
    
    image_name = create_name(env_id, "Image", "env_image")
    label_name = create_name(env_id, "Label", "env_image")
    if bpy.data.images.find(image_name) != -1:
        bpy.data.images.remove(bpy.data.images[image_name])
    if bpy.data.images.find(label_name) != -1:
        bpy.data.images.remove(bpy.data.images[label_name])
    
    img_image = bpy.data.images.load(os.path.join(options["directory"], options["environments"][env_id]["image"]))
    img_label = bpy.data.images.load(os.path.join(options["directory"], options["environments"][env_id]["label"]))

    img_image.name = image_name
    img_label.name = label_name
    img_image.colorspace_settings.name = env_options["colorspaceImage"]
    img_label.colorspace_settings.name = env_options["colorspaceLabel"]
    
    node_image.image = img_image
    node_label.image = img_label
    
    node_label.interpolation = "Closest"


def create_world_background_360imagelabeljson(world, env_id, options):
    delete_all_nodes(world.node_tree)
    nodes = world.node_tree.nodes

    env_options = get_clean_options("environments", env_id, options)

    node_output = nodes.new("ShaderNodeOutputWorld")
    node_switch = add_node_group_to_node_tree(world.node_tree, "Image/Label Switch World")
    node_image = nodes.new("ShaderNodeTexEnvironment")
    node_label = nodes.new("ShaderNodeTexEnvironment")
    node_random = add_driver_node(nodes, env_options["strength"])

    node_output.location = (600, 0)
    node_switch.location = (400, 0)
    node_image.location = (0, 0)
    node_label.location = (0, -220)
    node_random.location = (0, -440)

    world.node_tree.links.new(node_switch.outputs[0], node_output.inputs[0])
    world.node_tree.links.new(node_image.outputs[0], node_switch.inputs[0])
    world.node_tree.links.new(node_label.outputs[0], node_switch.inputs[1])
    world.node_tree.links.new(node_random.outputs[0], node_switch.inputs[2])

    image_name = create_name(env_id, "Image", "env_image")
    label_name = create_name(env_id, "Label", "env_image")
    if bpy.data.images.find(image_name) != -1:
        bpy.data.images.remove(bpy.data.images[image_name])
    if bpy.data.images.find(label_name) != -1:
        bpy.data.images.remove(bpy.data.images[label_name])

    img_image = bpy.data.images.load(os.path.join(options["directory"], options["environments"][env_id]["image"]))

    f = open(os.path.join(options["directory"], options["environments"][env_id]["label"]))
    label = json.load(f)
    f.close()
    img_label = bpy.data.images.new(label_name, label["imageWidth"], label["imageHeight"])
    array = np.zeros([img_label.size[0], img_label.size[1], img_label.channels])
    for shape in label["shapes"]:
        c = shape["group_id"] / 255  # Blender expects value between 0 and 1 --> 0-255 -> 0-1
        if shape["shape_type"] == "polygon":
            img_draw_polygon(array, shape["points"], [c, c, c, 1])
        elif shape["shape_type"] == "rectangle":
            p = shape["points"]
            img_draw_polygon(array, [p[0], [p[0][0], p[1][1]], p[1], [p[1][0], p[0][1]]], [c, c, c, 1])

    img_label.pixels = np.rot90(array).flatten()

    img_image.name = image_name
    img_image.colorspace_settings.name = env_options["colorspaceImage"]

    node_image.image = img_image
    node_label.image = img_label

    node_label.interpolation = "Closest"

    
def create_world_background_360imagecolor(world, env_id, options):
    delete_all_nodes(world.node_tree)
    nodes = world.node_tree.nodes
    
    env_options = get_clean_options("environments", env_id, options)
    
    node_output = nodes.new("ShaderNodeOutputWorld")
    node_switch = add_node_group_to_node_tree(world.node_tree, "Image/Label Switch World")
    node_image = nodes.new("ShaderNodeTexEnvironment")
    node_random = add_driver_node(nodes, env_options["strength"])

    node_output.location = (600, 0)
    node_random.location = (0, -220)
    node_switch.location = (400, 0)
    node_image.location = (0, 0)
    
    world.node_tree.links.new(node_switch.outputs[0], node_output.inputs[0])
    world.node_tree.links.new(node_image.outputs[0], node_switch.inputs[0])
    world.node_tree.links.new(node_random.outputs[0], node_switch.inputs[2])
    
    image_name = create_name(env_id, "Image", "env_image")
    if bpy.data.images.find(image_name) != -1:
        bpy.data.images.remove(bpy.data.images[image_name])
    
    img_image = bpy.data.images.load(os.path.join(options["directory"], env_options["image"]))
    img_image.name = image_name
    img_image.colorspace_settings.name = env_options["colorspaceImage"]
    node_image.image = img_image

    color = env_options["color"]
    while (len(color) < 3): color += [color[0]]  # If color = [1] -> color = [1, 1, 1]
    if    (len(color) < 4): color += [1]         # If color = [1, 0.5, 0.6] -> color = [1, 0.5, 0.6, 1] (Alpha value = 1)
    node_switch.inputs[1].default_value = color


def add_node_group_to_node_tree(node_tree, node_group_name, type="ShaderNodeGroup"):
    node = node_tree.nodes.new(type)
    node.node_tree = bpy.data.node_groups[node_group_name]
    return node


def create_image_label_switch_world_node_group():
    group_name = "Image/Label Switch World"
    if exists_node_group_by_name(group_name):
        bpy.data.node_groups.remove(bpy.data.node_groups[group_name])  # Remove
        #bpy.data.node_groups[group_name].name = group_name + "_old"    # Rename
        
    node_group = bpy.data.node_groups.new(group_name, "ShaderNodeTree")
    
    group_input = node_group.nodes.new("NodeGroupInput")
    group_output = node_group.nodes.new("NodeGroupOutput")
    
    group_mixrgb = node_group.nodes.new("ShaderNodeMixRGB")
    group_background = node_group.nodes.new("ShaderNodeBackground")
    
    group_is_label = node_group.nodes.new("ShaderNodeValue")
    driver_is_label = group_is_label.outputs[0].driver_add("default_value")
    driver_is_label.driver.expression = "label"
    
    
    group_input.location = (0, 0)
    group_output.location = (600, 0)
    group_is_label.location = (0, 100)
    group_mixrgb.location = (200, 99)
    group_background.location = (400, 5)
    
    node_group.inputs.new("NodeSocketColor", "Image")
    node_group.inputs.new("NodeSocketColor", "Label")
    node_group.inputs.new("NodeSocketFloat", "Strength (Random)")
    node_group.outputs.new("NodeSocketShader", "Shader")
    
    node_group.links.new(group_is_label.outputs[0], group_mixrgb.inputs[0])
    node_group.links.new(group_input.outputs[0], group_mixrgb.inputs[1])
    node_group.links.new(group_input.outputs[1], group_mixrgb.inputs[2])
    node_group.links.new(group_input.outputs[2], group_background.inputs[1])
    node_group.links.new(group_mixrgb.outputs[0], group_background.inputs[0])
    node_group.links.new(group_background.outputs[0], group_output.inputs[0])


def create_image_label_switch_object_node_group():
    group_name = "Image/Label Switch Object"
    if exists_node_group_by_name(group_name):
        bpy.data.node_groups.remove(bpy.data.node_groups[group_name])  # Remove

    node_group = bpy.data.node_groups.new(group_name, "ShaderNodeTree")

    group_input = node_group.nodes.new("NodeGroupInput")
    group_output = node_group.nodes.new("NodeGroupOutput")

    group_mixshader = node_group.nodes.new("ShaderNodeMixShader")
    group_mixvolume = node_group.nodes.new("ShaderNodeMixShader")

    group_is_label = node_group.nodes.new("ShaderNodeValue")
    driver_is_label = group_is_label.outputs[0].driver_add("default_value")
    driver_is_label.driver.expression = "label"

    group_input.location = (0, 0)
    group_output.location = (600, 0)
    group_is_label.location = (0, 100)
    group_mixshader.location = (200, 99)
    group_mixvolume.location = (200, 299)

    node_group.inputs.new("NodeSocketShader", "Base Surface")
    node_group.inputs.new("NodeSocketShader", "Base Volume")
    node_group.inputs.new("NodeSocketColor", "Color")
    node_group.outputs.new("NodeSocketShader", "Surface")
    node_group.outputs.new("NodeSocketShader", "Volume")

    node_group.links.new(group_is_label.outputs[0], group_mixshader.inputs[0])
    node_group.links.new(group_is_label.outputs[0], group_mixvolume.inputs[0])
    node_group.links.new(group_input.outputs[0], group_mixshader.inputs[1])
    node_group.links.new(group_input.outputs[2], group_mixshader.inputs[2])
    node_group.links.new(group_input.outputs[1], group_mixvolume.inputs[1])
    node_group.links.new(group_mixshader.outputs[0], group_output.inputs["Surface"])
    node_group.links.new(group_mixvolume.outputs[0], group_output.inputs["Volume"])


def create_mix_values_node_group():
    group_name = "Mix Values"
    if exists_node_group_by_name(group_name):
        bpy.data.node_groups.remove(bpy.data.node_groups[group_name])  # Remove
        
    node_group = bpy.data.node_groups.new(group_name, "ShaderNodeTree")
    
    group_input = node_group.nodes.new("NodeGroupInput")
    group_output = node_group.nodes.new("NodeGroupOutput")
    
    group_inverse = node_group.nodes.new("ShaderNodeMath")
    group_inverse.operation = "SUBTRACT"
        
    group_value1 = node_group.nodes.new("ShaderNodeMath")
    group_value1.operation = "MULTIPLY"
    
    group_value2 = node_group.nodes.new("ShaderNodeMath")
    group_value2.operation = "MULTIPLY"
    
    group_return = node_group.nodes.new("ShaderNodeMath")
    group_return.operation = "ADD"
    
    group_input.location = (0, 0)
    group_inverse.location = (200, 100)
    group_value1.location = (400, 100)
    group_value2.location = (400, -100)
    group_return.location = (600, 0)
    group_output.location = (800, 0)
    
    node_group.inputs.new("NodeSocketFloat", "Mix")
    node_group.inputs.new("NodeSocketFloat", "Value 1")
    node_group.inputs.new("NodeSocketFloat", "Value 2")
    node_group.outputs.new("NodeSocketFloat", "Mixed Value")
    
    group_inverse.inputs[0].default_value = 1  # Inversing the input -> 1 - mix -> inputs[0] must be 1
    node_group.links.new(group_input.outputs[0], group_inverse.inputs[1])
    node_group.links.new(group_inverse.outputs[0], group_value1.inputs[0])
    node_group.links.new(group_input.outputs[0], group_value2.inputs[0])
    node_group.links.new(group_input.outputs[1], group_value1.inputs[1])
    node_group.links.new(group_input.outputs[2], group_value2.inputs[1])
    node_group.links.new(group_value1.outputs[0], group_return.inputs[0])
    node_group.links.new(group_value2.outputs[0], group_return.inputs[1])
    node_group.links.new(group_return.outputs[0], group_output.inputs[0])
    

def create_random_value_node_group():
    group_name = "Random Value"
    if exists_node_group_by_name(group_name):
        bpy.data.node_groups.remove(bpy.data.node_groups[group_name])  # Remove
        
    node_group = bpy.data.node_groups.new(group_name, "ShaderNodeTree")
    
    group_input = node_group.nodes.new("NodeGroupInput")
    group_output = node_group.nodes.new("NodeGroupOutput")
    
    group_random = node_group.nodes.new("ShaderNodeValue")
    group_random.name = "Random"
    driver_random = group_random.outputs[0].driver_add("default_value")
    driver_random.driver.use_self = True
    driver_random.driver.expression = "random(self, frame)"
    
    group_is_label = node_group.nodes.new("ShaderNodeValue")
    group_is_label.name = "Is label?"
    driver_is_label = group_is_label.outputs[0].driver_add("default_value")
    driver_is_label.driver.expression = "label"
    
    group_random_value = add_node_group_to_node_tree(node_group, "Mix Values")
    group_label_value = add_node_group_to_node_tree(node_group, "Mix Values")
    
    group_input.location = (0, 0)
    group_random.location = (0, 100)
    group_is_label.location = (200, 100)
    group_random_value.location = (200, 0)
    group_label_value.location = (400, 0)
    group_output.location = (600, 0)
    
    node_group.inputs.new("NodeSocketFloat", "Min")
    node_group.inputs.new("NodeSocketFloat", "Max")
    node_group.outputs.new("NodeSocketFloat", "Random")
    
    node_group.inputs[0].default_value = 1.0
    node_group.inputs[1].default_value = 1.0
    
    node_group.links.new(group_input.outputs[0], group_random_value.inputs[1])
    node_group.links.new(group_input.outputs[1], group_random_value.inputs[2])
    node_group.links.new(group_random.outputs[0], group_random_value.inputs[0])
    node_group.links.new(group_is_label.outputs[0], group_label_value.inputs[0])
    node_group.links.new(group_random_value.outputs[0], group_label_value.inputs[1])
    node_group.links.new(group_label_value.outputs[0], group_output.inputs[0])
    group_label_value.inputs[2].default_value = 1
    
    
def create_reflection_catcher_streetv1_node_group():
    group_name = "Street v1 Reflection Catcher"
    if exists_node_group_by_name(group_name):
        bpy.data.node_groups.remove(bpy.data.node_groups[group_name])
        
    node_group = bpy.data.node_groups.new(group_name, "ShaderNodeTree")
    
    group_input = node_group.nodes.new("NodeGroupInput")
    group_output = node_group.nodes.new("NodeGroupOutput")
    
    group_shader = node_group.nodes.new("ShaderNodeBsdfPrincipled")
    group_roughness_calc = node_group.nodes.new("ShaderNodeMath")
    
    group_geometry = node_group.nodes.new("ShaderNodeNewGeometry")
    group_bumps1 = node_group.nodes.new("ShaderNodeBump")
    group_bumps2 = node_group.nodes.new("ShaderNodeBump")
    group_noise1 = node_group.nodes.new("ShaderNodeTexNoise")
    group_noise2 = node_group.nodes.new("ShaderNodeTexNoise")
    group_flatten = node_group.nodes.new("ShaderNodeMath")
    
    group_input.location = (0, 0)
    group_geometry.location = (-200, -305)
    group_noise1.location = (0, -305)
    group_noise2.location = (0, -530)
    group_flatten.location = (200, -530)
    group_bumps2.location = (400, -550)
    group_roughness_calc.location = (600, 0)
    group_bumps1.location = (600, -450)
    group_shader.location = (800, 0)
    group_output.location = (1100, 0)
    
    node_group.inputs.new("NodeSocketColor", "Color")
    node_group.inputs.new("NodeSocketFloat", "Roughness")
    node_group.inputs.new("NodeSocketFloat", "Big Bumps")
    node_group.inputs.new("NodeSocketFloat", "Small Bumps")
    node_group.outputs.new("NodeSocketShader", "Shader")
    
    node_group.inputs[0].default_value = [0.007, 0.007, 0.007, 1]
    node_group.inputs[1].default_value = 0.5
    node_group.inputs[2].default_value = 0.2
    node_group.inputs[3].default_value = 0.1
    
    group_noise1.inputs["Scale"].default_value = 1
    group_noise2.inputs["Scale"].default_value = 120
    group_shader.inputs["Clearcoat"].default_value = 0.25
    group_shader.inputs["Clearcoat Roughness"].default_value = 0.25
    group_roughness_calc.operation = "MULTIPLY"
    group_roughness_calc.inputs[1].default_value = 0.7
    group_flatten.operation = "MULTIPLY"
    group_flatten.use_clamp = True
    group_flatten.inputs[1].default_value = 1.5
    
    node_group.links.new(group_input.outputs[0], group_shader.inputs["Base Color"])
    node_group.links.new(group_input.outputs[1], group_roughness_calc.inputs[0])
    node_group.links.new(group_roughness_calc.outputs[0], group_shader.inputs["Roughness"])
    node_group.links.new(group_input.outputs[2], group_bumps1.inputs["Strength"])
    node_group.links.new(group_input.outputs[3], group_bumps2.inputs["Strength"])
    node_group.links.new(group_geometry.outputs[0], group_noise1.inputs["Vector"])
    node_group.links.new(group_geometry.outputs[0], group_noise2.inputs["Vector"])
    node_group.links.new(group_noise1.outputs[0], group_bumps1.inputs["Height"])
    node_group.links.new(group_noise2.outputs[0], group_flatten.inputs[0])
    node_group.links.new(group_flatten.outputs[0], group_bumps2.inputs["Height"])
    node_group.links.new(group_bumps2.outputs[0], group_bumps1.inputs["Normal"])
    node_group.links.new(group_bumps1.outputs[0], group_shader.inputs["Normal"])
    node_group.links.new(group_shader.outputs[0], group_output.inputs[0])


def create_shadow_catcher_streetv1_node_group():
    group_name = "Street v1 Shadow Catcher"
    if exists_node_group_by_name(group_name):
        bpy.data.node_groups.remove(bpy.data.node_groups[group_name])
        
    node_group = bpy.data.node_groups.new(group_name, "ShaderNodeTree")
    
    group_input = node_group.nodes.new("NodeGroupInput")
    group_output = node_group.nodes.new("NodeGroupOutput")
    group_shader = node_group.nodes.new("ShaderNodeBsdfPrincipled")
    
    group_input.location = (0, 0)
    group_shader.location = (200, 0)
    group_output.location = (400, 0)
    
    node_group.inputs.new("NodeSocketColor", "Color")
    node_group.outputs.new("NodeSocketShader", "Shader")
    
    node_group.inputs[0].default_value = [0.8, 0.8, 0.8, 1]
    
    node_group.links.new(group_input.outputs[0], group_shader.inputs["Base Color"])
    node_group.links.new(group_shader.outputs[0], group_output.inputs[0])


def create_compositing_maddin_v1_node_group():
    group_name = "Maddin v1 Compositing Node"
    if exists_node_group_by_name(group_name):
        bpy.data.node_groups.remove(bpy.data.node_groups[group_name])
        
    node_group = bpy.data.node_groups.new(group_name, "CompositorNodeTree")
    
    group_input = node_group.nodes.new("NodeGroupInput")
    group_output = node_group.nodes.new("NodeGroupOutput")
    group_image_contents = node_group.nodes.new("CompositorNodeMixRGB")
    
    group_reflection_image_blur = node_group.nodes.new("CompositorNodeBlur")
    group_reflection_difference = node_group.nodes.new("CompositorNodeMixRGB")
    group_reflection_extract_env = node_group.nodes.new("CompositorNodeMath")
    group_reflection_extract_obj = node_group.nodes.new("CompositorNodeMath")
    group_reflection_env_remove = node_group.nodes.new("CompositorNodeMixRGB")
    group_reflection_obj_remove = node_group.nodes.new("CompositorNodeMixRGB")
    group_reflection_blur = node_group.nodes.new("CompositorNodeBlur")
    group_reflection_sharpen = node_group.nodes.new("CompositorNodeMath")
    group_reflection_lighten = node_group.nodes.new("CompositorNodeMath")
    group_reflection_extract_ao = node_group.nodes.new("CompositorNodeMixRGB")
    group_reflection_remove_ao = node_group.nodes.new("CompositorNodeMixRGB")
    
    group_shadow_mix = node_group.nodes.new("CompositorNodeMixRGB")
    group_ambient_occlusion_avg = node_group.nodes.new("CompositorNodeLevels")
    group_ambient_occlusion_inv = node_group.nodes.new("CompositorNodeMath")
    group_ambient_occlusion_mul = node_group.nodes.new("CompositorNodeMath")
    group_ambient_occlusion_mix = node_group.nodes.new("CompositorNodeMixRGB")
    group_mix_shadows_with_environment = node_group.nodes.new("CompositorNodeMixRGB")
    group_mix_shadows_with_reflection = node_group.nodes.new("CompositorNodeMixRGB")
    
    group_mix_all = node_group.nodes.new("CompositorNodeMixRGB")
    group_value_label = node_group.nodes.new("CompositorNodeValue")
    group_extract_label = node_group.nodes.new("CompositorNodeMixRGB")
    group_mix_label = node_group.nodes.new("CompositorNodeMixRGB")
    
    
    group_input.name = "Input"
    group_output.name = "Output"
    group_image_contents.name = "Image Contents"
    group_reflection_image_blur.name = "Reflection Image Blur"
    group_reflection_difference.name = "Reflection Difference"
    group_reflection_extract_env.name = "Reflection Extract Env"
    group_reflection_extract_obj.name = "Reflection Extract Obj"
    group_reflection_env_remove.name = "Reflection Env Remove"
    group_reflection_obj_remove.name = "Reflection Obj Remove"
    group_reflection_blur.name = "Reflection Blur"
    group_reflection_sharpen.name = "Reflection Sharpen"
    group_reflection_lighten.name = "Reflection Lighten"
    group_reflection_extract_ao.name = "Reflection Extract AO"
    group_reflection_remove_ao.name = "Reflection Remove AO"
    group_shadow_mix.name = "Shadow Mix"
    group_ambient_occlusion_avg.name = "Ambient Occlusion Avg (Average)"
    group_ambient_occlusion_inv.name = "Ambient Occlusion Inv (Reciprocal)"
    group_ambient_occlusion_mul.name = "Ambient Occlusion Mul (Multiply)"
    group_ambient_occlusion_mix.name = "Ambient Occlusion Mix"
    group_mix_shadows_with_environment.name = "Mix Shadows with Environments"
    group_mix_shadows_with_reflection.name = "Mix Shadows with Reflection"
    group_mix_all.name = "Mix All"
    group_value_label.name = "Value Label"
    group_extract_label.name = "Extract Label"
    group_mix_label.name = "Mix Label"
    
    
    group_input.location = (0, 0)
    group_image_contents.location = (200, 0)
    group_output.location = (2400, 0)
    
    group_reflection_image_blur.location = (200, -800)
    group_reflection_difference.location = (200, -1150)
    group_reflection_extract_ao.location = (200, -1350)
    group_reflection_extract_env.location = (200, -1550)
    group_reflection_extract_obj.location = (200, -1750)
    group_reflection_remove_ao.location = (400, -1150)
    group_reflection_env_remove.location = (600, -1150)
    group_reflection_obj_remove.location = (800, -1150)
    group_reflection_blur.location = (1000, -900)
    group_reflection_sharpen.location = (1200, -800)
    group_reflection_lighten.location = (1400, -800)
    
    group_shadow_mix.location = (200, -200)
    group_ambient_occlusion_avg.location = (200, -400)
    group_ambient_occlusion_inv.location = (400, -400)
    group_ambient_occlusion_mul.location = (600, -300)
    group_ambient_occlusion_mix.location = (800, -200)
    group_mix_shadows_with_environment.location = (1000, -100)
    group_mix_shadows_with_reflection.location = (1800, -100)
    
    group_mix_all.location = (2000, 0)
    group_value_label.location = (0, 100)
    group_extract_label.location = (400, 0)
    group_mix_label.location = (2200, 0)
    
    
    group_image_contents.blend_type = "SUBTRACT"
    group_shadow_mix.blend_type = "MULTIPLY"
    group_ambient_occlusion_inv.operation = "DIVIDE"
    group_ambient_occlusion_mul.operation = "MULTIPLY"
    group_ambient_occlusion_mul.use_clamp = True
    group_ambient_occlusion_mix.blend_type = "MULTIPLY"
    group_mix_shadows_with_environment.blend_type = "ADD"
    group_mix_shadows_with_reflection.blend_type = "ADD"
    
    group_reflection_difference.blend_type = "DIFFERENCE"
    group_reflection_extract_env.operation = "LESS_THAN"
    group_reflection_extract_obj.operation = "LESS_THAN"
    group_reflection_extract_ao.blend_type = "DIFFERENCE"
    group_reflection_remove_ao.blend_type = "SUBTRACT"
    group_reflection_sharpen.operation = "POWER"
    group_reflection_env_remove.blend_type = "MULTIPLY"
    group_reflection_obj_remove.blend_type = "SUBTRACT"
    group_reflection_lighten.operation = "MULTIPLY"
    #group_reflection_lighten.use_clamp = True
    
    group_mix_all.blend_type = "ADD"
    group_extract_label.blend_type = "SUBTRACT"
    
    group_ambient_occlusion_inv.inputs[0].default_value = 1
    group_reflection_image_blur.use_relative = True
    group_reflection_image_blur.use_extended_bounds = True
    group_reflection_image_blur.factor_x = 0.2
    group_reflection_image_blur.factor_y = 0.2
    group_reflection_extract_env.inputs[1].default_value = 0.000001
    group_reflection_extract_obj.inputs[1].default_value = 0.000001
    group_reflection_blur.use_relative = True
    group_reflection_blur.use_extended_bounds = True
    group_reflection_blur.factor_x = 0.2
    group_reflection_blur.factor_y = 0.2
    group_reflection_sharpen.inputs[1].default_value = 1.2
    group_reflection_lighten.inputs[1].default_value = 8
    
    driver = group_value_label.outputs[0].driver_add("default_value")
    driver.driver.expression = "label"
    
    node_group.inputs.new("NodeSocketColor", "Raw Image / Image")
    node_group.inputs.new("NodeSocketColor", "Raw Image / Env")
    node_group.inputs.new("NodeSocketColor", "Raw Image / BloomCol")
    node_group.inputs.new("NodeSocketColor", "Shadow Catcher / Shadow")
    node_group.inputs.new("NodeSocketColor", "Shadow Catcher / AO")
    node_group.inputs.new("NodeSocketColor", "Shadow Catcher / Env")
    node_group.inputs.new("NodeSocketColor", "Reflection Catcher / GlossDir")
    node_group.inputs.new("NodeSocketColor", "Reflection Catcher / AO")
    node_group.inputs.new("NodeSocketColor", "Reflection Catcher Reference / GlossDir")
    node_group.inputs.new("NodeSocketColor", "Reflection Catcher Reference / Env")
    node_group.inputs.new("NodeSocketColor", "Reflection Catcher Reference / AO")
    node_group.outputs.new("NodeSocketColor", "Image")
    
    node_group.links.new(group_input.outputs["Raw Image / Image"], group_image_contents.inputs[1])
    node_group.links.new(group_input.outputs["Raw Image / Image"], group_extract_label.inputs[1])
    node_group.links.new(group_input.outputs["Raw Image / Env"], group_image_contents.inputs[2])
    node_group.links.new(group_input.outputs["Raw Image / Env"], group_shadow_mix.inputs[1])
    node_group.links.new(group_input.outputs["Raw Image / Env"], group_reflection_extract_obj.inputs[0])
    node_group.links.new(group_input.outputs["Raw Image / BloomCol"], group_extract_label.inputs[2])
    node_group.links.new(group_input.outputs["Shadow Catcher / Shadow"], group_shadow_mix.inputs[2])
    node_group.links.new(group_input.outputs["Shadow Catcher / AO"], group_ambient_occlusion_avg.inputs[0])
    node_group.links.new(group_input.outputs["Shadow Catcher / AO"], group_ambient_occlusion_mul.inputs[0])
    node_group.links.new(group_input.outputs["Shadow Catcher / Env"], group_mix_shadows_with_environment.inputs[1])
    node_group.links.new(group_input.outputs["Reflection Catcher / GlossDir"], group_reflection_image_blur.inputs[0])
    node_group.links.new(group_input.outputs["Reflection Catcher / GlossDir"], group_reflection_difference.inputs[1])
    node_group.links.new(group_input.outputs["Reflection Catcher / AO"], group_reflection_extract_ao.inputs[1])
    node_group.links.new(group_input.outputs["Reflection Catcher Reference / GlossDir"], group_reflection_difference.inputs[2])
    node_group.links.new(group_input.outputs["Reflection Catcher Reference / Env"], group_reflection_extract_env.inputs[0])
    node_group.links.new(group_input.outputs["Reflection Catcher Reference / AO"], group_reflection_extract_ao.inputs[2])
    node_group.links.new(group_output.inputs["Image"], group_mix_label.outputs[0])
    
    node_group.links.new(group_reflection_difference.outputs[0], group_reflection_remove_ao.inputs[1])
    node_group.links.new(group_reflection_extract_ao.outputs[0], group_reflection_remove_ao.inputs[2])
    node_group.links.new(group_reflection_remove_ao.outputs[0], group_reflection_env_remove.inputs[1])
    node_group.links.new(group_reflection_extract_env.outputs[0], group_reflection_env_remove.inputs[2])
    node_group.links.new(group_reflection_env_remove.outputs[0], group_reflection_obj_remove.inputs[1])
    node_group.links.new(group_reflection_extract_obj.outputs[0], group_reflection_obj_remove.inputs[2])
    
    node_group.links.new(group_reflection_obj_remove.outputs[0], group_reflection_blur.inputs[0])
    node_group.links.new(group_reflection_blur.outputs[0], group_reflection_sharpen.inputs[0])
    node_group.links.new(group_reflection_sharpen.outputs[0], group_reflection_lighten.inputs[0])

    node_group.links.new(group_shadow_mix.outputs[0], group_ambient_occlusion_mix.inputs[1])
    node_group.links.new(group_ambient_occlusion_avg.outputs[0], group_ambient_occlusion_inv.inputs[1])
    node_group.links.new(group_ambient_occlusion_inv.outputs[0], group_ambient_occlusion_mul.inputs[1])
    node_group.links.new(group_ambient_occlusion_mul.outputs[0], group_ambient_occlusion_mix.inputs[2])
    node_group.links.new(group_ambient_occlusion_mix.outputs[0], group_mix_shadows_with_environment.inputs[2])
    node_group.links.new(group_mix_shadows_with_environment.outputs[0], group_mix_shadows_with_reflection.inputs[1])
    node_group.links.new(group_image_contents.outputs[0], group_mix_all.inputs[2])
    node_group.links.new(group_mix_shadows_with_reflection.outputs[0], group_mix_all.inputs[1])
    node_group.links.new(group_reflection_lighten.outputs[0], group_mix_shadows_with_reflection.inputs[0])
    node_group.links.new(group_reflection_image_blur.outputs[0], group_mix_shadows_with_reflection.inputs[2])
    node_group.links.new(group_value_label.outputs[0], group_mix_label.inputs[0])
    node_group.links.new(group_mix_all.outputs[0], group_mix_label.inputs[1])
    node_group.links.new(group_extract_label.outputs[0], group_mix_label.inputs[2])
    

def create_node_groups():
    create_mix_values_node_group()
    create_image_label_switch_world_node_group()
    create_image_label_switch_object_node_group()
    create_random_value_node_group()
    
    create_reflection_catcher_streetv1_node_group()
    create_shadow_catcher_streetv1_node_group()
    create_compositing_maddin_v1_node_group()


def create_reflection_catcher_material(name, id, values):
    if bpy.data.materials.find(name) != -1:
        bpy.data.materials.remove(bpy.data.materials[name])
        
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    delete_all_nodes(mat.node_tree)
    mat_nodes = mat.node_tree.nodes
    
    reflection_nodes = {"streetv1": "Street v1 Reflection Catcher"}
    
    node_output = mat_nodes.new("ShaderNodeOutputMaterial")
    node_group = add_node_group_to_node_tree(mat.node_tree, reflection_nodes[id])
    
    node_output.location = (400, 0)
    node_group.location = (200, 0)
    
    mat.node_tree.links.new(node_group.outputs[0], node_output.inputs[0])
    
    y_pos = 0
    for key in node_group.inputs.keys():
        if key in values.keys():
            node_value = add_driver_node(mat_nodes, values[key])
            mat.node_tree.links.new(node_value.outputs[0], node_group.inputs[key])
            node_value.location = (0, y_pos)
            y_pos -= 100
            
    return mat


def create_shadow_catcher_material(name, id, values):
    if bpy.data.materials.find(name) != -1:
        bpy.data.materials.remove(bpy.data.materials[name])
        
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    delete_all_nodes(mat.node_tree)
    mat_nodes = mat.node_tree.nodes
    
    reflection_nodes = {"streetv1": "Street v1 Shadow Catcher"}
    
    node_output = mat_nodes.new("ShaderNodeOutputMaterial")
    node_group = add_node_group_to_node_tree(mat.node_tree, reflection_nodes[id])
    
    node_output.location = (400, 0)
    node_group.location = (200, 0)
    
    mat.node_tree.links.new(node_group.outputs[0], node_output.inputs[0])
    
    y_pos = 0
    for key in node_group.inputs.keys():
        if key in values.keys():
            node_value = add_driver_node(mat_nodes, values[key])
            mat.node_tree.links.new(node_value.outputs[0], node_group.inputs[key])
            node_value.location = (0, y_pos)
            y_pos -= 100
            
    return mat


def create_compositing_node_tree(scene, id, values, output_path):
    scene.use_nodes = True
    delete_all_nodes(scene.node_tree)
    scene_nodes = scene.node_tree.nodes
    
    compositing_nodes = {"maddinv1": "Maddin v1 Compositing Node"}

    node_output = scene_nodes.new("CompositorNodeComposite")
    node_viewer = scene_nodes.new("CompositorNodeViewer")
    node_group = add_node_group_to_node_tree(scene.node_tree, compositing_nodes[id], "CompositorNodeGroup")
    
    node_group.location = (300, 0)
    node_output.location = (500, 0)
    node_viewer.location = (500, -150)
    
    scene.node_tree.links.new(node_group.outputs[0], node_output.inputs[0])
    scene.node_tree.links.new(node_group.outputs[0], node_viewer.inputs[0])
    
    layer_nodes = {}
    
    y_pos = 0
    for layer in scene.view_layers:
        node_layer = scene_nodes.new("CompositorNodeRLayers")
        node_layer.scene = scene
        node_layer.layer = layer.name
        node_layer.location = (0, y_pos)
        layer_nodes[layer.name] = node_layer
        y_pos -= 500
        
    for key in node_group.inputs.keys():
        if " / " in key:
            layer, output = key.split(" / ")
            if layer in layer_nodes.keys():
                scene.node_tree.links.new(layer_nodes[layer].outputs[output], node_group.inputs[key])
        
        elif key in values.keys():
            node_value = add_driver_node(mat_nodes, values[key], "CompositorNode")
            scene.node_tree.links.new(node_value.outputs[0], node_group.inputs[key])
            node_value.location = (0, y_pos)
            y_pos -= 100


##############################
## ------------------------ ##
## --- Render functions --- ##
## ------------------------ ##
##############################


def is_data_scene(scene):
    return True


def update_maddins_panel():
    if not bpy.context.screen:
        return
    bpy.context.screen.update_tag()


def update_render_stats(scene):
    frame_num = scene.frame_end - scene.frame_start + 1
    frame_now = scene.frame_current - scene.frame_start + 1
    progress = int(frame_now / frame_num * 20)
    #bpy.types.OBJECT_PT_maddins_data_panel.progress = "[" + "#"*progress + "-"*(20-progress) + "] " + str(frame_now) + "/" + str(frame_num)
    #update_maddins_panel()
    current = "Image (0/1)"
    if bpy.app.driver_namespace["label"]:
        current = "Label (1/1)"
    print("Rendering: "+current)
    print("Scene: "+scene.name)
    print("Scene Progress: "+"[" + "#"*progress + "-"*(20-progress) + "] " + str(frame_now) + "/" + str(frame_num))


def render_next_scene(scene=None):
    index = 0
    if scene:
        index = scenes.index(scene) + 1
        
    if index == len(scenes):
        if bpy.app.driver_namespace["label"]:
            bpy.types.OBJECT_PT_maddins_data_panel.imagelabel = "Labels"
            bpy.types.OBJECT_PT_maddins_data_panel.scene = "\\O_o/"
            bpy.types.OBJECT_PT_maddins_data_panel.progress = "Finished!"
            #update_maddins_panel()
        else:
            render_all_data_scenes(label=1)

        return  # if index==len(scenes) --> all scenes renderd -> stop (return)

    scene = scenes[index]
    
    if bpy.app.driver_namespace["label"]:
        scene.render.filter_size = 0  # Filter makes everything smooth, but label needs sharp edges
        scene.render.image_settings.compression = 0  # compression off
        if scene.render.filepath[-6:] != "_label":
            scene.render.filepath += "_label"  # add _label to filename, if not already part
    else:
        scene.render.filter_size = 1.5  # see above, added for realism
        scene.render.image_settings.compression = 15  # see above, added for realism and save space
        if scene.render.filepath[-6:] == "_label":
            scene.render.filepath = scene.render.filepath[:-6]  # remove _label from filename, if it is part
        
    bpy.types.OBJECT_PT_maddins_data_panel.scene = scene.name + "  -  " + str(index+1) + "/" + str(len(scenes))
    bpy.types.OBJECT_PT_maddins_data_panel.progress = "[--------------------] 0/0"
    #update_maddins_panel()
    bpy.ops.render.render(animation=True, scene=scene.name)


def render_all_data_scenes_bu(label=0):
    add_app_handler("render_write", update_render_stats)
    add_app_handler("render_complete", render_next_scene)
    bpy.types.OBJECT_PT_maddins_data_panel.imagelabel = "Images"
    if label:
        bpy.types.OBJECT_PT_maddins_data_panel.imagelabel = "Labels"
    bpy.app.driver_namespace["label"] = label
            
    render_next_scene()


def render_set_scene_settings(scene):
    if bpy.app.driver_namespace["label"]:
        scene.render.filter_size = 0  # Filter makes everything smooth, but label needs sharp edges
        scene.render.dither_intensity = 0  # Dither adds s+p effect, but label needs plain color
        scene.render.image_settings.compression = 0  # compression off
        if scene.render.filepath[-6:] != "_label":
            scene.render.filepath += "_label"  # add _label to filename, if not already part
    else:
        scene.render.filter_size = 1.5  # see above, added for realism
        scene.render.dither_intensity = 1 # see above, added for realism
        scene.render.image_settings.compression = 15  # see above, added for realism and save space
        if scene.render.filepath[-6:] == "_label":
            scene.render.filepath = scene.render.filepath[:-6]  # remove _label from filename, if it is part


def render_all_data_scenes():
    if bpy.context.window and bpy.context.window.scene:
        render_all_data_scenes_screen()
    else:
        render_all_data_scenes_noscreen()


def render_all_data_scenes_noscreen():
    add_app_handler("render_write", update_render_stats)
    for index, scene in enumerate(scenes):
        for label in range(2):
            bpy.app.driver_namespace["label"] = label
            render_set_scene_settings(scene)
            bpy.ops.render.render(animation=True, scene=scene.name)

        print()
        print("Finished scene '" + scene.name + "'", str(index + 1) + "/" + str(len(scenes)))
        print()


def render_all_data_scenes_screen():
    add_app_handler("render_write", update_render_stats)
    for index, scene in enumerate(scenes):
        for label in range(2):
            bpy.app.driver_namespace["label"] = label
            render_set_scene_settings(scene)
            bpy.ops.render.render(animation=True, scene=scene.name)  # currently same as noscreen

        print()
        print("Finished scene '"+scene.name+"'", str(index+1)+"/"+str(len(scenes)))
        print()


def render_custom_scenes(scenes):
    for scene in scenes:
        bpy.context.scene = scene
        bpy.ops.render.render(animation=True)


############################
## ---------------------- ##
## --- File functions --- ##
## ---------------------- ##
############################


def read_json_data(filepath):
    file = open(filepath)
    data = json.load(file)
    file.close()
    return data


def read_standard_options():
    global standard_options
    try:
        standard_options = read_json_data("templates/template.json")["standards"]
    except Exception as err:
        print("│ Warning: No standard options found!")
        print("├        :", err)
        print("└        : This can later lead to KeyErrors. Please use the template for your specififc version.")
        print()
        standard_options = {}
        

def get_clean_options(type, id, options={}):
    return {**standard_options[type][options[type][id]["type"]], **options[type][id]}


def read_maddins_data(context, filepath):
    data = read_json_data(filepath)

    datapath = os.path.dirname(filepath)
    options = {**data, "directory": datapath}

    add_app_handler("frame_change_pre", create_update_variables_function(options))  # Update custom variables on every frame change

    read_standard_options()
    load_objects(options)
    load_environments(options)

    return {'FINISHED'}


def load_environments(options):
    environments = options["environments"]
    
    for env_id in environments:
        create_scene(env_id, options)


def load_objects(options):
    objects = options["objects"]
    
    create_object_groups(options)
    
    for obj_id in objects:
        create_object(obj_id, options)


##########################
## -------------------- ##
## --- UI functions --- ##
## -------------------- ##
##########################

class ToggleImageLabel(bpy.types.Operator):
    """Toggle object materials between Image and Label"""
    bl_idname = "maddins_operators.toggle_image_label"
    bl_label = "Toggle Image/Label view"
    
    def execute(self, context):
        bpy.app.driver_namespace["label"] = abs(bpy.app.driver_namespace["label"] - 1)
        update_drivers()
        return {'FINISHED'}


class StartRenderAll(bpy.types.Operator):
    """Render all Environments automatically"""
    bl_idname = "maddins_operators.render_all_scenes"
    bl_label = "Render all imported Scenes"
    
    def execute(self, context):
        render_all_data_scenes()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        self.layout.label(text="WARNING!")
        self.layout.label(text="Rendering can take some time!")
        self.layout.label(text="There is no visual feedback!")
        self.layout.label(text="You may want to open the System console for progress.")
        self.layout.label(text="Your PC may hang up during render!")
        self.layout.label(text="Are you sure?")


class ImportMaddinsData(bpy.types.Operator, ImportHelper):
    """Import data created by Maddins Data Creation Tool"""
    bl_idname = "maddins_operators.open"
    bl_label = "Maddin's File Import"

    # ImportHelper mixin class uses this
    filename_ext = [".json"]
    
    filter_glob: bpy.props.StringProperty(
        default="*.json;*.madd.json;*.madd",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return read_maddins_data(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportMaddinsData.bl_idname, text="Maddin's Files (.json/.madd)")


class MaddinsDataPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Maddins Data Creation Tool"
    bl_idname = "OBJECT_PT_maddins_data_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    imagelabel = "..."
    scene = "\\O_o/"
    progress = "[---------------] 0/0"
    def draw(self, context):
        layout = self.layout

        layout.operator("maddins_operators.toggle_image_label", text="Toggle image <--> label view", icon='NONE')
        layout.operator("maddins_operators.render_all_scenes", text="Render all imported Scenes", icon='NONE')
        layout.label(text="Rendering: "+self.imagelabel)
        layout.label(text="Current Scene: "+self.scene)
        layout.label(text="Scene Progress: "+self.progress)


def register():
    bpy.utils.register_class(ImportMaddinsData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(ToggleImageLabel)
    bpy.utils.register_class(StartRenderAll)
    bpy.utils.register_class(MaddinsDataPanel)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(bpy.types.Operator.bl_rna_get_subclass_py('IMPORT_MADDIN_OT_open'))
    bpy.utils.unregister_class(ToggleImageLabel)
    bpy.utils.unregister_class(StartRenderAll)
    bpy.utils.unregister_class(MaddinsDataPanel)


if __name__ == "__main__":
    register()

    create_node_groups()
    # [PLACEHOLDER read_maddins_data] #
    # read_maddins_data(bpy.context, "path/to/file.madd.json")
    register_driver_namespace()
    update_drivers()

    if not bpy.context.window:
        render_all_data_scenes()
