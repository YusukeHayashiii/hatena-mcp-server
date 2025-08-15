"""Unit tests for MarkdownImporter module."""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile
from datetime import datetime

from hatena_blog_mcp.markdown_importer import MarkdownImporter
from hatena_blog_mcp.models import BlogPost


class TestMarkdownImporter:
    """Test suite for MarkdownImporter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.importer = MarkdownImporter(enable_front_matter=True)
        self.importer_no_frontmatter = MarkdownImporter(enable_front_matter=False)
    
    def test_init_default(self):
        """Test default initialization."""
        importer = MarkdownImporter()
        assert importer.enable_front_matter is True
        assert importer.markdown_processor is not None
    
    def test_init_disable_frontmatter(self):
        """Test initialization with Front Matter disabled."""
        importer = MarkdownImporter(enable_front_matter=False)
        assert importer.enable_front_matter is False
    
    def test_convert_simple_markdown(self):
        """Test simple Markdown conversion without Front Matter."""
        markdown_text = """# Test Title

This is a simple paragraph.

- List item 1
- List item 2

```python
print("Hello, World!")
```
"""
        
        result = self.importer.convert(markdown_text)
        
        assert isinstance(result, BlogPost)
        assert result.title == "Test Title"
        assert '<h1 id="test-title">Test Title</h1>' in result.content
        assert "<p>This is a simple paragraph.</p>" in result.content
        assert "<ul>" in result.content
        assert "<li>List item 1</li>" in result.content
        assert "<code" in result.content  # Code block
        assert result.categories == []
        assert result.categories == []
        assert result.draft is False  # Default: not draft
        assert result.summary == ""
    
    def test_convert_with_frontmatter(self):
        """Test Markdown conversion with Front Matter."""
        markdown_text = """---
title: Custom Title
summary: This is a summary
categories: [tech, programming]
tags: [python, markdown]
draft: true
---

# Markdown Title (should be ignored)

Content here.
"""
        
        result = self.importer.convert(markdown_text)
        
        assert result.title == "Custom Title"
        assert result.summary == "This is a summary"
        assert result.categories == ["tech", "programming"]
        assert result.draft is True  # draft: true
        assert '<h1 id="markdown-title-should-be-ignored">Markdown Title (should be ignored)</h1>' in result.content
    
    def test_convert_frontmatter_string_categories(self):
        """Test Front Matter with comma-separated string categories."""
        markdown_text = """---
title: Test Post
categories: tech, programming, python
tags: tutorial, guide
---

Content.
"""
        
        result = self.importer.convert(markdown_text)
        
        assert result.categories == ["tech", "programming", "python"]
    
    def test_convert_frontmatter_single_category(self):
        """Test Front Matter with single category/tag field."""
        markdown_text = """---
title: Test Post
category: single-category
tag: single-tag
---

Content.
"""
        
        result = self.importer.convert(markdown_text)
        
        assert result.categories == ["single-category"]
    
    def test_convert_no_frontmatter_mode(self):
        """Test conversion with Front Matter disabled."""
        markdown_text = """---
title: Should be ignored
categories: [ignored]
---

# Real Title

Content.
"""
        
        result = self.importer_no_frontmatter.convert(markdown_text)
        
        # Should extract title from first H1, ignoring Front Matter
        assert result.title == "Real Title"
        assert result.categories == []
        # Content should include the Front Matter as literal text (converted to HTML)
        assert "<hr />" in result.content  # --- becomes <hr />
        assert "title: Should be ignored" in result.content
    
    def test_title_extraction_priority(self):
        """Test title extraction priority: Front Matter > H1 > filename."""
        
        # Test 1: Front Matter title has highest priority
        markdown_with_fm = """---
title: Front Matter Title
---

# H1 Title

Content.
"""
        result = self.importer.convert(markdown_with_fm, filename="file.md")
        assert result.title == "Front Matter Title"
        
        # Test 2: H1 title when no Front Matter
        markdown_h1 = """# H1 Title

Content.
"""
        result = self.importer.convert(markdown_h1, filename="file.md")
        assert result.title == "H1 Title"
        
        # Test 3: Filename when no Front Matter or H1
        markdown_plain = """Just content without title."""
        result = self.importer.convert(markdown_plain, filename="my-article.md")
        assert result.title == "my-article"
        
        # Test 4: Fallback to "Untitled"
        result = self.importer.convert(markdown_plain, filename=None)
        assert result.title == "Untitled"
    
    def test_load_from_file_success(self):
        """Test successful file loading."""
        content = """---
title: File Test
categories: [file, test]
---

# File Content

This content comes from a file.
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = self.importer.load_from_file(temp_path)
            
            assert result.title == "File Test"
            assert result.categories == ["file", "test"]
            assert "This content comes from a file." in result.content
        finally:
            Path(temp_path).unlink()  # Clean up
    
    def test_load_from_file_not_found(self):
        """Test file not found error."""
        with pytest.raises(FileNotFoundError, match="Markdown file not found"):
            self.importer.load_from_file("nonexistent.md")
    
    def test_load_from_file_is_directory(self):
        """Test error when path is a directory."""
        with pytest.raises(ValueError, match="Path is not a file"):
            self.importer.load_from_file(".")
    
    def test_convert_invalid_yaml(self):
        """Test handling of invalid YAML Front Matter."""
        markdown_text = """---
title: Test
invalid_yaml: [unclosed list
---

Content.
"""
        
        # Should handle gracefully and still process content
        with pytest.raises(ValueError, match="Failed to convert Markdown"):
            self.importer.convert(markdown_text)
    
    def test_metadata_edge_cases(self):
        """Test various edge cases in metadata extraction."""
        
        # Empty categories/tags
        markdown_text = """---
title: Test
categories: []
tags: []
---

Content.
"""
        result = self.importer.convert(markdown_text)
        assert result.categories == []
        
        # None values
        markdown_text = """---
title: Test
categories: 
tags: 
---

Content.
"""
        result = self.importer.convert(markdown_text)
        assert result.categories == []
        
        # Mixed empty and valid
        markdown_text = """---
title: Test
categories: [valid, "", "  ", another]
tags: "one, , three"
---

Content.
"""
        result = self.importer.convert(markdown_text)
        assert result.categories == ["valid", "another"]  # Empty strings filtered out
    
    def test_html_conversion_features(self):
        """Test that Markdown features are properly converted to HTML."""
        markdown_text = """# Main Title

## Subtitle

**Bold text** and *italic text*.

[Link](https://example.com)

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |

```python
def hello():
    return "world"
```

> Blockquote text
"""
        
        result = self.importer.convert(markdown_text)
        
        # Check various HTML elements are present
        assert '<h1 id="main-title">Main Title</h1>' in result.content
        assert '<h2 id="subtitle">Subtitle</h2>' in result.content
        assert "<strong>Bold text</strong>" in result.content
        assert "<em>italic text</em>" in result.content
        assert '<a href="https://example.com">Link</a>' in result.content
        assert "<table>" in result.content
        assert "<tr>" in result.content
        assert "<td>" in result.content
        assert "<code" in result.content
        assert "<blockquote>" in result.content
    
    def test_blogpost_attributes(self):
        """Test that BlogPost object has correct attributes."""
        result = self.importer.convert("# Test")
        
        # Check all required BlogPost attributes exist
        assert hasattr(result, 'id')
        assert hasattr(result, 'title')
        assert hasattr(result, 'content')
        assert hasattr(result, 'categories')
        assert hasattr(result, 'draft')
        assert hasattr(result, 'summary')
        assert hasattr(result, 'created_at')
        assert hasattr(result, 'updated_at')
        
        # Check default values
        assert result.id is None
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)