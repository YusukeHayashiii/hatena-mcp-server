"""Markdown import and processing module for Hatena Blog MCP Server.

This module provides functionality to convert Markdown files (with optional
Front Matter metadata) into BlogPost objects ready for publishing to Hatena Blog.

Features:
- YAML Front Matter parsing for metadata
- Markdown to HTML conversion
- Automatic title extraction from H1 or filename
- Support for categories and draft status
"""

from pathlib import Path
from typing import Optional, Union, Dict, Any
from datetime import datetime

import markdown
import frontmatter

from .models import BlogPost


class MarkdownImporter:
    """Handles importing and converting Markdown content to BlogPost objects.
    
    Supports YAML Front Matter with the following fields:
    - title: Article title (string)
    - summary: Article summary/description (string) 
    - categories: List of category names (list of strings)
    - draft: Draft status (boolean, default: False)
    """
    
    def __init__(self, *, enable_front_matter: bool = True) -> None:
        """Initialize the Markdown importer.
        
        Args:
            enable_front_matter: Whether to parse YAML Front Matter
        """
        self.enable_front_matter = enable_front_matter
        self.markdown_processor = markdown.Markdown(
            extensions=[
                'fenced_code',
                'tables', 
                'toc',
                'nl2br'
            ]
        )
    
    def load_from_file(self, path: Union[str, Path]) -> BlogPost:
        """Load a Markdown file and convert it to a BlogPost.
        
        Args:
            path: Path to the Markdown file
            
        Returns:
            BlogPost object ready for publishing
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the Markdown content is invalid
        """
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError as e:
            raise ValueError(f"Failed to read file as UTF-8: {e}")
        
        return self.convert(content, filename=file_path.name)
    
    def convert(self, markdown_text: str, *, filename: Optional[str] = None) -> BlogPost:
        """Convert Markdown text to a BlogPost object.
        
        Args:
            markdown_text: Raw Markdown content (may include Front Matter)
            filename: Optional filename for title fallback
            
        Returns:
            BlogPost object with converted content
            
        Raises:
            ValueError: If the conversion fails
        """
        try:
            # Parse Front Matter if enabled
            if self.enable_front_matter:
                post = frontmatter.loads(markdown_text)
                metadata = post.metadata
                content = post.content
            else:
                metadata = {}
                content = markdown_text
            
            # Convert Markdown to HTML
            self.markdown_processor.reset()
            html_content = self.markdown_processor.convert(content)
            
            # Extract title
            title = self._extract_title(metadata, content, filename)
            
            # Extract other metadata
            categories = self._extract_categories(metadata)
            draft = metadata.get('draft', False)
            summary = metadata.get('summary', '')
            
            # Create BlogPost object
            blog_post = BlogPost(
                title=title,
                content=html_content,
                categories=categories,
                summary=summary,
                draft=draft,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            return blog_post
            
        except Exception as e:
            raise ValueError(f"Failed to convert Markdown: {e}")
    
    def _extract_title(self, metadata: Dict[str, Any], content: str, filename: Optional[str]) -> str:
        """Extract title from metadata, H1 heading, or filename.
        
        Priority: metadata.title > first H1 > filename without extension
        """
        # Priority 1: Front Matter title
        if 'title' in metadata and metadata['title']:
            return str(metadata['title']).strip()
        
        # Priority 2: First H1 heading in content
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# ') and len(line) > 2:
                return line[2:].strip()
        
        # Priority 3: Filename without extension
        if filename:
            return Path(filename).stem
        
        # Fallback
        return "Untitled"
    
    def _extract_categories(self, metadata: Dict[str, Any]) -> list[str]:
        """Extract categories from metadata.
        
        Supports both 'categories' and 'category' fields.
        """
        categories = []
        
        # Try 'categories' field first
        if 'categories' in metadata:
            cats = metadata['categories']
            if isinstance(cats, list):
                categories.extend([str(c).strip() for c in cats if c and str(c).strip()])
            elif isinstance(cats, str):
                # Split comma-separated categories
                categories.extend([c.strip() for c in cats.split(',') if c.strip()])
        
        # Try 'category' field as fallback
        elif 'category' in metadata:
            cat = metadata['category']
            if isinstance(cat, str) and cat.strip():
                categories.append(cat.strip())
        
        return categories
    
