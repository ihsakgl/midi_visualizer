def resize_objects(obj, old_width, old_height, new_width, new_height):
    if hasattr(obj, "x_position") and obj.x_position is not None: obj.x_position *= new_width / old_width
    if hasattr(obj, "y_position"): obj.y_position *= new_height / old_height
    if hasattr(obj, "width"): obj.width *= new_width / old_width
    if hasattr(obj, "height"): obj.height *= new_height / old_height
    if hasattr(obj, "radius"): obj.radius *= (new_width + new_height) / (old_width + old_height) / 2
    if hasattr(obj, "screen_width"): obj.screen_width = new_width
    if hasattr(obj, "screen_height"): obj.screen_height = new_height
   

