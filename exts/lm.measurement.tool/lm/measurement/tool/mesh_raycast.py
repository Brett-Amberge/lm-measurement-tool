import carb
import omni.kit.mesh.raycast
import omni.usd

PHYSICS_WAIT_FRAMES = 20


class MeshRaycast:
    def __init__(self):
        self._usd_context = omni.usd.get_context()
        self._mr = omni.kit.mesh.raycast.acquire_mesh_raycast_interface()
        self._meshPaths = []
        self._rootPath = None
        self._limit_to_selection = False

    def createScene(self, rootPrim, filter_fn):
        self._limit_to_selection = False
        self.sub = self._mr.get_mesh_raycast_event_stream().create_subscription_to_pop_by_type(
            int(omni.kit.mesh.raycast.RaycastEventType.BVH_REBUILT), self._on_bvh_rebuilt
        )
        self._mr.set_bvh_refresh_rate(omni.kit.mesh.raycast.BvhRefreshRate.FAST, True)
        self._mr.set_allowed_mesh_paths([])
        self._meshPaths = self._mr.get_mesh_paths()
        self._filter_fn = filter_fn

    def createSelectionScene(self, meshes):
        self._limit_to_selection = True

        self._meshPaths.clear()
        for mesh in meshes:
            self._meshPaths.append(mesh.pathString)

        self._mr.set_bvh_refresh_rate(omni.kit.mesh.raycast.BvhRefreshRate.FAST, True)
        self._mr.set_allowed_mesh_paths(self._meshPaths)

    def clearScene(self):
        self.sub = None
        self._mr.set_bvh_refresh_rate(omni.kit.mesh.raycast.BvhRefreshRate.SLOW, False)
        self._meshPaths.clear()

    def raycast_closest(self, origin, dir, maxDist):
        hitResult = self._mr.closestRaycast(origin, dir, maxDist)
        hitReport = {}
        if hitResult.meshIndex >= 0:
            hitReport["hit"] = True
            hitReport["position"] = hitResult.position
            hitReport["normal"] = hitResult.normal
            hitReport["collision"] = self._mr.get_mesh_path_from_index(hitResult.meshIndex)
        else:
            hitReport["hit"] = False
        return hitReport

    def spherecast(self, origin, radius, dir, maxDist):
        overlap_result = self._mr.spherecast(origin, dir, radius, maxDist)
        overlap_report = {}
        if len(overlap_result):
            overlap_report["overlap"] = True
            overlap_report["collisions"] = [
                self._mr.get_mesh_path_from_index(mesh_index) for mesh_index in overlap_result
            ]
        else:
            overlap_report["overlap"] = False
        return overlap_report

    def overlap_vertices(self, origin, radius):
        overlap_result = self._mr.overlap_vertices(origin, radius)
        overlap_report = {}
        if len(overlap_result):
            overlap_report["overlap"] = True
            overlap_report["collisions"] = {}
            overlap_report["collisions_faces"] = {}
            overlap_report["collision_vert_positions"] = {}
            for r in overlap_result:
                mesh_path = self._mr.get_mesh_path_from_index(r.meshIndex)
                overlap_report["collisions"][mesh_path] = r.vertexIndices
                overlap_report["collisions_faces"][mesh_path] = r.faceIndices
                overlap_report["collision_vert_positions"][mesh_path] = [self._mr.get_vertex_local_position(mesh_path, i) for i in r.vertexIndices]
        else:
            overlap_report["overlap"] = False
        return overlap_report

    def get_flood_data(self, mesh_paths, density):
        positions = []
        normals = []
        for mesh_path in mesh_paths:
            result = self._mr.getFloodPoints(mesh_path.pathString, density, False)
            positions.extend(result["positions"])
            normals.extend(result["normals"])
        return positions, normals

    def get_mesh_paths(self):
        return self._meshPaths

    def _on_bvh_rebuilt(self, event: carb.events.IEvent):
        if not self._limit_to_selection:
            self._meshPaths = self._mr.get_mesh_paths()
