def render_template(title: str, nav_html: str, content: str) -> str:
    """
    Deterministic simple templating without external dependencies.
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - AI Intelligence Archive</title>
</head>
<body>
    <nav>
        {nav_html}
    </nav>
    <main>
        {content}
    </main>
</body>
</html>
"""
