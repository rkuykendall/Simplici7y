from django import forms
from django.forms.widgets import ClearableFileInput
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class OptimizedFileInput(ClearableFileInput):
    """
    Custom file input widget that provides better upload experience.
    """

    def __init__(self, attrs=None):
        default_attrs = {
            "accept": "image/*,.zip,.sit,.hqx,.bin,.dmg,.pkg,.sit.hqx",
            "multiple": False,
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the file input with enhanced features.
        """
        # Base rendering
        html = super().render(name, value, attrs, renderer)

        # Add JavaScript for file size validation and progress
        extra_html = format_html(
            """
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const fileInput = document.getElementById('id_{name}');
                    if (fileInput) {{
                        fileInput.addEventListener('change', function(e) {{
                            const file = e.target.files[0];
                            if (file) {{
                                // Check file size (50MB limit)
                                const maxSize = 50 * 1024 * 1024;
                                if (file.size > maxSize) {{
                                    alert('File is too large. Maximum size is 50MB.');
                                    e.target.value = '';
                                    return;
                                }}
                                
                                // Show file info
                                const fileInfo = document.getElementById('file-info-{name}');
                                if (fileInfo) {{
                                    const sizeStr = formatFileSize(file.size);
                                    fileInfo.innerHTML = `Selected: ${{file.name}} (${{sizeStr}})`;
                                    fileInfo.style.display = 'block';
                                }}
                            }}
                        }});
                    }}
                    
                    function formatFileSize(bytes) {{
                        if (bytes === 0) return '0 Bytes';
                        const k = 1024;
                        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                        const i = Math.floor(Math.log(bytes) / Math.log(k));
                        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
                    }}
                }});
            </script>
            <div id="file-info-{name}" style="display: none; margin-top: 5px; font-size: 0.9em; color: #666;"></div>
        """,
            name=name,
        )

        return mark_safe(html + extra_html)


class OptimizedImageInput(OptimizedFileInput):
    """
    Specialized file input for images with preview.
    """

    def __init__(self, attrs=None):
        default_attrs = {
            "accept": "image/*",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render image input with preview capability.
        """
        html = super().render(name, value, attrs, renderer)

        # Add image preview
        preview_html = format_html(
            """
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const imageInput = document.getElementById('id_{name}');
                    if (imageInput) {{
                        imageInput.addEventListener('change', function(e) {{
                            const file = e.target.files[0];
                            const preview = document.getElementById('preview-{name}');
                            
                            if (file && file.type.startsWith('image/')) {{
                                const reader = new FileReader();
                                reader.onload = function(e) {{
                                    preview.src = e.target.result;
                                    preview.style.display = 'block';
                                }};
                                reader.readAsDataURL(file);
                            }} else {{
                                preview.style.display = 'none';
                            }}
                        }});
                    }}
                }});
            </script>
            <img id="preview-{name}" src="" alt="Preview" style="display: none; max-width: 300px; max-height: 200px; margin-top: 10px; border: 1px solid #ddd; padding: 5px;">
        """,
            name=name,
        )

        return mark_safe(html + preview_html)
