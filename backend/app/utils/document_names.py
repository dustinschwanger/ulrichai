# backend/app/utils/document_names.py

import re
from typing import Dict

class DocumentNameMapper:
    """
    Temporary helper for mapping file names to display names.
    This will be replaced when we build the admin upload interface.
    """
    
    # Static mapping for now - can be moved to database later
    MANUAL_MAPPINGS: Dict[str, str] = {
        "hreffectiveness.pdf": "HR Effectiveness",
        "leadership_framework.pdf": "Leadership Framework",
        "organizational_culture.pdf": "Organizational Culture",
        # Add more mappings as needed
    }
    
    @classmethod
    def get_display_name(cls, filename: str) -> str:
        """
        Get a clean display name for a document.
        
        Args:
            filename: The original filename
            
        Returns:
            A cleaned up display name
        """
        # Check manual mapping first
        if filename.lower() in cls.MANUAL_MAPPINGS:
            return cls.MANUAL_MAPPINGS[filename.lower()]
        
        # Auto-generate from filename
        # Remove extension
        name = filename.rsplit('.', 1)[0]
        
        # Replace underscores and hyphens with spaces
        name = name.replace('_', ' ').replace('-', ' ')
        
        # Handle CamelCase
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split())
        
        # Handle common abbreviations
        abbreviations = {
            'Hr': 'HR',
            'Ai': 'AI',
            'Ml': 'ML',
            'Rbl': 'RBL',
            'Kpi': 'KPI',
            'Roi': 'ROI',
            'Ceo': 'CEO',
            'Cfo': 'CFO',
            'Cto': 'CTO',
            'Vp': 'VP',
            'Svp': 'SVP',
            'Evp': 'EVP'
        }
        
        for abbr, replacement in abbreviations.items():
            name = name.replace(abbr, replacement)
        
        return name
    
    @classmethod
    def get_filename_from_display(cls, display_name: str) -> str:
        """
        Reverse lookup - get filename from display name.
        
        Args:
            display_name: The display name
            
        Returns:
            The original filename if found, None otherwise
        """
        for filename, name in cls.MANUAL_MAPPINGS.items():
            if name == display_name:
                return filename
        
        # If not found in manual mappings, we can't reliably reverse it
        return None