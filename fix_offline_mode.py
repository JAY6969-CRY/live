#!/usr/bin/env python
"""
Fix for offline mode issues with custom questions and stock performance display.
This script makes the necessary modifications to the existing code to address these issues.
"""
import os
import shutil
import re

def fix_indentation_issue():
    """Fix indentation issues in app.py causing custom questions not to work."""
    app_path = os.path.join("web", "app.py")
    
    if os.path.exists(app_path):
        print(f"Fixing indentation issues in {app_path}...")
        
        with open(app_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Fix indentation issues with custom questions
        fixed_content = re.sub(
            r"(\s+)for q in market_questions:(\n\s+)if st\.button\(q, key=f\"market_q_{q}\"\):(\n\s+)st\.session_state\.question = q(\n\s+)st\.rerun\(\)",
            r"\1for q in market_questions:\2    if st.button(q, key=f\"market_q_{q}\"):\3        st.session_state.question = q\4        st.rerun()",
            content
        )
        
        # Fix indentation issues with stock symbols
        fixed_content = re.sub(
            r"(\s+)for j, symbol in enumerate\(stocks\):(\n\s+)with cols\[j\]:(\n\s+)if st\.button\(symbol, key=f\"example_symbol_{symbol}\"\):(\n\s+)st\.session_state\.stock_symbol = symbol(\n\s+)st\.rerun\(\)",
            r"\1for j, symbol in enumerate(stocks):\2    with cols[j]:\3        if st.button(symbol, key=f\"example_symbol_{symbol}\"):\4            st.session_state.stock_symbol = symbol\5            st.rerun()",
            fixed_content
        )
        
        with open(app_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)
            
        print("✓ Fixed indentation issues in web/app.py")
    else:
        print("✗ Could not find web/app.py")

def ensure_stock_performance_display():
    """Ensure stock performance data is displayed with news sources."""
    temp_file = "temp_offline_enhanced_app.py"
    
    if os.path.exists(temp_file):
        print(f"Ensuring stock performance data is displayed in {temp_file}...")
        
        with open(temp_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Add stock performance display to source display
        if "stock_performance" not in content:
            # Find the source display section
            source_display_pattern = r"(# Display source articles with better formatting.*?st\.divider\(\))"
            source_display_section = re.search(source_display_pattern, content, re.DOTALL)
            
            if source_display_section:
                source_section = source_display_section.group(1)
                
                # Add stock performance display
                stock_performance_code = """
                                        # Display stock performance if available
                                        if "ticker" in source and source["ticker"] in STOCK_DATA:
                                            stock = STOCK_DATA[source["ticker"]]
                                            change_class = "stock-up" if stock["change"] > 0 else "stock-down"
                                            change_symbol = "▲" if stock["change"] > 0 else "▼"
                                            change_html = f'<span class="{change_class}">{change_symbol} ₹{abs(stock["change"]):.2f} ({abs(stock["change_pct"]):.2f}%)</span>'
                                            
                                            st.markdown("---")
                                            st.markdown(f"**{stock['name']}** - ₹{stock['price']:.2f} {change_html}", unsafe_allow_html=True)
                                """
                
                # Add before the divider
                modified_section = source_section.replace("                                    if i < len(result[\"sources\"]) - 1:", 
                                               stock_performance_code + "\n                                    if i < len(result[\"sources\"]) - 1:")
                
                # Replace in content
                modified_content = content.replace(source_section, modified_section)
                
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(modified_content)
                
                print(f"✓ Added stock performance display to {temp_file}")
            else:
                print(f"✗ Could not find source display section in {temp_file}")
        else:
            print(f"✓ Stock performance display already present in {temp_file}")
    else:
        print(f"✗ Could not find {temp_file}")

def fix_custom_questions():
    """Fix custom questions not being accepted."""
    temp_file = "temp_offline_enhanced_app.py"
    
    if os.path.exists(temp_file):
        print(f"Fixing custom questions in {temp_file}...")
        
        with open(temp_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if custom question handling is already fixed
        if "custom_question if custom_question else" not in content:
            # Add custom question handling
            analyze_pattern = r"analysis = analyze_stock\(stock_symbol(?:, custom_question)?\)"
            
            if re.search(analyze_pattern, content):
                # Replace with proper handling
                modified_content = re.sub(
                    analyze_pattern,
                    "analysis = analyze_stock(stock_symbol, custom_question)",
                    content
                )
                
                # Update question display
                question_display_pattern = r"question_display = analysis\.get\('question'\)"
                if re.search(question_display_pattern, content):
                    modified_content = re.sub(
                        question_display_pattern,
                        "question_display = custom_question if custom_question else analysis.get('question', f\"What's happening with {stock_symbol}?\")",
                        modified_content
                    )
                
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(modified_content)
                
                print(f"✓ Fixed custom questions in {temp_file}")
            else:
                print(f"✗ Could not find analyze_stock function call in {temp_file}")
        else:
            print(f"✓ Custom questions already fixed in {temp_file}")
    else:
        print(f"✗ Could not find {temp_file}")

def main():
    """Main function to fix all issues."""
    print("Fixing issues with custom questions and stock performance display...")
    
    # Fix indentation issues
    fix_indentation_issue()
    
    # Ensure stock performance display
    ensure_stock_performance_display()
    
    # Fix custom questions
    fix_custom_questions()
    
    print("\nAll fixes applied! Please restart the offline app to see the changes.")
    print("Run: python run_offline_enhanced.py")

if __name__ == "__main__":
    main() 