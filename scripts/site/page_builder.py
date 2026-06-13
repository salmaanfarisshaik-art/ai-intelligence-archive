from scripts.site.template_engine import render_template

class PageBuilder:
    def __init__(self, nav_html: str):
        self.nav_html = nav_html
        
    def build_index(self) -> str:
        content = """
        <div class="container">
            <h1>AI Intelligence Archive</h1>
            <p>Welcome to the deterministic intelligence archive.</p>
        </div>
        """
        return render_template("Home", self.nav_html, content)
