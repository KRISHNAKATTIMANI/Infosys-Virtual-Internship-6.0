from django import template

register = template.Library()


@register.filter
def mod(value, arg):
    """Returns the modulo of value divided by arg"""
    try:
        return int(value) % int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def div(value, arg):
    """Returns the integer division of value divided by arg"""
    try:
        return int(value) // int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def format_time(seconds):
    """Format seconds into Xm Ys format"""
    try:
        seconds = int(seconds)
        minutes = seconds // 60
        secs = seconds % 60
        if minutes > 0:
            return f"{minutes}m {secs}s"
        return f"{secs}s"
    except (ValueError, TypeError):
        return "-"
