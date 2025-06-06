def resize_objects(obj, base_width, base_height, new_width, new_height,
                   new_visualizer_rect, base_visualizer_rect, is_visualizer_element: bool):
    # Calculate scaling factors
    visualizer_scale_x = new_visualizer_rect.width / base_visualizer_rect.width
    visualizer_scale_y = new_visualizer_rect.height / base_visualizer_rect.height
    screen_scale_x = new_width / base_width
    screen_scale_y = new_height / base_height
    avg_screen_scale = (screen_scale_x + screen_scale_y) / 2

    # Decide which scale is going to be used
    scale_x = visualizer_scale_x if is_visualizer_element else screen_scale_x
    scale_y = visualizer_scale_y if is_visualizer_element else screen_scale_y

    # Update screen attributes
    if hasattr(obj, "screen_width"):
        obj.screen_width = new_width
    if hasattr(obj, "screen_height"):
        obj.screen_height = new_height
    if hasattr(obj, "visualizer_rect"):
        obj.visualizer_rect = new_visualizer_rect

    # Resizing
    if hasattr(obj, "width") and obj.width is not None:
        obj.width *= scale_x
    if hasattr(obj, "height") and obj.height is not None:
        obj.height *= scale_y
    if hasattr(obj, "radius") and obj.radius is not None:
        obj.radius *= avg_screen_scale
    if hasattr(obj, "x") and obj.x is not None:
        obj.x *= scale_x
    if hasattr(obj, "y") and obj.y is not None:
        obj.y *= scale_y
    if hasattr(obj, "x_offset"):
        obj.x_offset *= scale_x
    if hasattr(obj, "crop_top"):
        obj.crop_top *= scale_y
        obj.crop_top = int(obj.crop_top)


def is_colliding(element, mx, my):
    "Checks whether user has clicked a certain element with mouse"
    return mx >= element.x and my >= element.y and mx <= element.x + element.width and my <= element.y + element.height