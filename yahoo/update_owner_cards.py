#!/usr/bin/env python3
"""
Update owner analysis HTML to make owner cards collapsible.
"""

import re

def update_owner_analysis():
    """Add collapsible functionality to owner cards."""
    
    file_path = 'html_reports/prod_ready/owner_analysis.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match owner card headers and replace them
    # Look for: <div class="owner-header">
    #           <div class="owner-name">NAME</div>
    #           <div style="color: #666; font-size: 0.9em;">EMAIL</div>
    #           </div>
    
    pattern = r'<div class="owner-header">\s*<div class="owner-name">([^<]+)</div>\s*<div style="color: #666; font-size: 0\.9em;">([^<]+)</div>\s*</div>'
    
    replacement = r'''<div class="owner-header" onclick="toggleOwner(this)">
                        <div>
                            <div class="owner-name">\1</div>
                            <div style="color: #666; font-size: 0.9em;">\2</div>
                        </div>
                        <span class="collapse-icon">🔽</span>
                    </div>
                    <div class="owner-content">'''
    
    updated_content = re.sub(pattern, replacement, content)
    
    # Add closing div for each owner-content before the next owner-card
    # Look for </div> followed by <div class="owner-card"> and add </div> before the new card
    pattern2 = r'(</div>\s*</div>\s*)\n\s*<div class="owner-card">'
    replacement2 = r'\1\n                    </div>\n                </div>\n        \n                <div class="owner-card">'
    
    updated_content = re.sub(pattern2, replacement2, updated_content)
    
    # Handle the last owner card - add closing div before the final closing tags
    pattern3 = r'(</div>\s*</div>\s*)\n\s*</div>\s*</div>\s*</div>\s*$'
    replacement3 = r'\1\n                    </div>\n                </div>\n        \n            </div>\n        </div>\n    </div>'
    
    updated_content = re.sub(pattern3, replacement3, updated_content, flags=re.MULTILINE)
    
    # Add JavaScript functions at the end before </body>
    js_code = '''
    <script>
        let allCollapsed = false;
        
        function toggleOwner(header) {
            const content = header.nextElementSibling;
            const icon = header.querySelector('.collapse-icon');
            
            if (content.classList.contains('collapsed')) {
                content.classList.remove('collapsed');
                icon.classList.remove('collapsed');
                icon.textContent = '🔽';
            } else {
                content.classList.add('collapsed');
                icon.classList.add('collapsed');
                icon.textContent = '▶️';
            }
        }
        
        function toggleAllOwners() {
            const button = document.querySelector('.collapse-all-btn');
            const headers = document.querySelectorAll('.owner-header');
            const contents = document.querySelectorAll('.owner-content');
            const icons = document.querySelectorAll('.collapse-icon');
            
            if (allCollapsed) {
                // Expand all
                contents.forEach(content => content.classList.remove('collapsed'));
                icons.forEach(icon => {
                    icon.classList.remove('collapsed');
                    icon.textContent = '🔽';
                });
                button.textContent = '📁 Collapse All';
                allCollapsed = false;
            } else {
                // Collapse all
                contents.forEach(content => content.classList.add('collapsed'));
                icons.forEach(icon => {
                    icon.classList.add('collapsed');
                    icon.textContent = '▶️';
                });
                button.textContent = '📂 Expand All';
                allCollapsed = true;
            }
        }
    </script>
</body>'''
    
    updated_content = updated_content.replace('</body>', js_code)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Updated owner_analysis.html with collapsible functionality")
    print("Added:")
    print("- Collapsible owner panels with click handlers")
    print("- Collapse/Expand all button in header")
    print("- Smooth animations and hover effects")

if __name__ == "__main__":
    update_owner_analysis()