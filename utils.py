state = {
    "self": {
        "x": self.x,
        "y": self.y,
        "facing_angle": self.facing_angle,
        "health": self.health,
        "energy": self.energy
    },
    "visible_objects": [
        {
            "type": obj.etype,
            "x": obj.x,
            "y": obj.y,
            "distance": distance_to(self, obj),
            "angle": math.atan2(obj.y - self.y, obj.x - self.x)
        } for obj in visible
    ]
}
