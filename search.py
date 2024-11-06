#!/usr/bin/env python3
import sys
import re
import subprocess
from pathlib import Path
import logging
import os
import argparse

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_manpage_source():
    """Get the path to the NixOS configuration manual source."""
    logger.debug("Looking for configuration.nix manual location...")
    try:
        result = subprocess.run(['man', '-w', 'configuration.nix'], 
                              capture_output=True, text=True)
        path = result.stdout.strip()
        logger.debug(f"Found manual at: {path}")
        return path
    except subprocess.CalledProcessError:
        logger.error("Could not find configuration.nix manual")
        sys.exit(1)

def read_manpage(path):
    """Read the man page source file."""
    logger.debug(f"Reading man page from: {path}")
    try:
        with open(path, 'r') as f:
            content = f.read()
            logger.debug(f"Successfully read {len(content)} characters")
            return content
    except IOError as e:
        logger.error(f"Error reading man page: {e}")
        sys.exit(1)

def filter_section_content(section, description_only=False):
    """Filter section content based on flags while preserving formatting."""
    if not description_only:
        return section
    
    lines = section.split('\n')
    filtered_lines = []
    
    # Get the option name line (first line)
    if lines:
        filtered_lines.append(lines[0].strip())
    
    # Add the RS command for proper indentation
    # filtered_lines.append('.RS 4')
    
    i = 1
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip metadata sections
        if any(marker in line for marker in [
            '\\fIType:', '\\fIDefault:', '\\fIExample:', '\\fIDeclared by:'
        ]) or '<nixpkgs/' in line:
            i += 1
            continue
            
        # Handle Note and Important sections
        logger.debug(f"Checking line for Note/Important: '{line}'")
        if line in ['Note', 'Important']:
            logger.debug(f"Found {line} section")
            filtered_lines.extend([
                '.sp',
                '.RS 4'
            ])
            
            # Add Note/Important with single .br before description
            filtered_lines.extend([
                f'\\fB{line}\\fP',
                '.br',
                lines[i + 1].strip() if i + 1 < len(lines) else '',
                '.RE'
            ])
            i += 2
            continue
            
        # Include regular description lines
        if line:  # Just check if line is not empty
            filtered_lines.append(line)
        
        i += 1
    
    # Add closing tags in correct order
    filtered_lines.extend([
        '.RE',
        '.RE',
        '.PP'
    ])
    
    return '\n'.join(filtered_lines)


def extract_sections(content, prefix, description_only=False):
    """Extract sections that match the given prefix."""
    logger.debug(f"Extracting sections matching prefix: {prefix}")
    
    sections = re.split(r'\.PP\s*\n', content)
    logger.debug(f"Split content into {len(sections)} sections")
    
    matched_sections = []
    for i, section in enumerate(sections, 1):
        patterns = [
            r'\\fB([^\\]+)\\fR',
            r'\\fB([\w\d\.\\&-]+)\\fR',
            r'\\fB([^\\]*(?:\\&[^\\]*)*?)\\fR'
        ]
        
        option_name = None
        raw_match = None
        
        for pattern in patterns:
            option_match = re.match(pattern, section.strip())
            if option_match:
                raw_match = option_match.group(1)
                option_name = raw_match.replace('\\&.', '.')
                break
        
        if option_name:
            logger.debug(f"Section {i}: Found option '{option_name}'")
            if option_name.startswith(prefix):
                logger.debug(f"✓ Matched: {option_name}")
                filtered_section = filter_section_content(section, description_only)
                if filtered_section.strip():  # Only include non-empty sections
                    matched_sections.append(filtered_section)
            else:
                logger.debug(f"✗ No match: {option_name}")
    
    logger.debug(f"Found {len(matched_sections)} matching sections")
    return matched_sections


def write_filtered_manpage(sections, output_path):
    """Write the filtered sections to a new man page file."""
    logger.debug(f"Writing filtered man page to: {output_path}")
    try:
        with open(output_path, 'w') as f:
            logger.debug("Writing man page header")
            f.write('.TH "CONFIGURATION.NIX" "5" "2024" "NixOS" "NixOS Manual (filtered)"\n')
            f.write('.SH "FILTERED OPTIONS"\n')
            
            logger.debug(f"Writing {len(sections)} sections")
            content = '\n'.join(sections)  # Remove extra spacing between sections
            f.write(content)
            
            logger.debug("Writing man page footer")
            f.write('\n.SH "NOTES"\n')
            f.write('This is a filtered version of the configuration.nix manual.\n')
            
            logger.debug("Successfully wrote filtered man page")
    except IOError as e:
        logger.error(f"Error writing filtered man page: {e}")
        sys.exit(1)


# def open_manpage(path):
#     """Open the man page using man command."""
#     logger.debug(f"Opening man page: {path}")
#     try:
#         abs_path = os.path.abspath(path)
#         os.execvp('man', ['man', abs_path])
#     except OSError as e:
#         logger.error(f"Error opening man page: {e}")
#         sys.exit(1)

def open_manpage(path):
    """Open the man page using man command and delete it afterwards."""
    logger.debug(f"Opening man page: {path}")
    try:
        abs_path = os.path.abspath(path)
        pid = os.fork()
        if pid == 0:  # Child process
            os.execvp('man', ['man', abs_path])
        else:  # Parent process
            os.waitpid(pid, 0)  # Wait for man to finish
            os.remove(abs_path)  # Delete the file
    except OSError as e:
        logger.error(f"Error opening man page: {e}")
        sys.exit(1)

def main():
    logger.info("Starting NixOS manual filter script")
    
    parser = argparse.ArgumentParser(description='Filter NixOS configuration manual')
    parser.add_argument('prefix', help='Option prefix to filter by')
    parser.add_argument('-d', '--description-only', 
                       action='store_true',
                       help='Show only option names and descriptions')
    
    args = parser.parse_args()
    
    logger.info(f"Filtering manual for prefix: {args.prefix}")
    if args.description_only:
        logger.info("Showing descriptions only")
    
    manpage_path = get_manpage_source()
    content = read_manpage(manpage_path)
    
    matched_sections = extract_sections(content, args.prefix, args.description_only)
    
    if not matched_sections:
        logger.warning(f"No options found matching prefix: {args.prefix}")
        sys.exit(1)
    
    output_path = Path(f"configuration.nix.{args.prefix}.5")
    write_filtered_manpage(matched_sections, output_path)
    
    logger.info(f"Created filtered man page: {output_path}")
    logger.info("Opening man page...")
    
    open_manpage(output_path)

if __name__ == "__main__":
    main()
