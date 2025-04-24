def resize_objects(obj, old_width, old_height, new_width, new_height, new_visualizer_rect, old_visualizer_rect, is_visualizer_element: bool):
    # Calculate scale factors
    visualizer_scale_x = new_visualizer_rect.width / old_visualizer_rect.width
    visualizer_scale_y = new_visualizer_rect.height / old_visualizer_rect.height
    screen_scale_x = new_width / old_width
    screen_scale_y = new_height / old_height
    avg_screen_scale = (screen_scale_x + screen_scale_y) / 2


    # Choose appropriate scale factors
    scale_x = visualizer_scale_x if is_visualizer_element else screen_scale_x
    scale_y = visualizer_scale_y if is_visualizer_element else screen_scale_y
    
    # Update screen-related values
    if hasattr(obj, "screen_width"):
        obj.screen_width = new_width
    if hasattr(obj, "screen_height"):
        obj.screen_height = new_height
    if hasattr(obj, "visualizer_rect"):
        obj.visualizer_rect = new_visualizer_rect

    

    # Apply resizing safely
    if hasattr(obj, "width") and obj.width is not None:
        obj.width *= scale_x
    if hasattr(obj, "height") and obj.height is not None:
        obj.height *= scale_y
    if hasattr(obj, "radius") and obj.radius is not None:
        obj.radius *= avg_screen_scale
    if hasattr(obj, "x_position") and obj.x_position is not None:
        obj.x_position *= scale_x
    if hasattr(obj, "y_position") and obj.y_position is not None:
        obj.y_position -= old_visualizer_rect.y
        obj.y_position *= scale_y
        obj.y_position += new_visualizer_rect.y

    if hasattr(obj, "x_offset"):
        obj.x_offset *= scale_x
    

