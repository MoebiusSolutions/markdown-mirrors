import argparse
import re
import jinja2
import os
import sys
import yaml

class Main:
    def __init__(self):
        self.title_pattern_1 = re.compile(r"^(.+)\n=+$", re.MULTILINE)
        self.title_pattern_2 = re.compile(r"^# (.+)$", re.MULTILINE)

    def _parse_args(self, argv):
        parser = argparse.ArgumentParser(description='Generates markdown files pointing to mirrors')
        parser.add_argument("config_file", help="Path of the configuration file")
        subparsers = parser.add_subparsers(required=True, dest="action")
        subparser = subparsers.add_parser("generate", help="Generates the mirror markdown files")
        subparser.add_argument("markdown_dir", help="Path of the markdown files directory")
        subparser = subparsers.add_parser("add_header", help="Adds mirror link to top of each markdown file")
        subparser.add_argument("markdown_dir", help="Path of the markdown files directory")
        return parser.parse_args(argv)

    def _load_config(self, config_file):
        with open(config_file, 'r', encoding='utf8') as f:
            return yaml.safe_load(f)

    def _escape_markdown(self, markdown):
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        return re.sub(r'([_*\[\]()~`>#\+\-=|{}\.!])', r'\\\1', markdown)
    
    def _get_markdown_files(self, source_dir):
        markdown_files=[]
        for filename in os.listdir(source_dir):
            if not filename.endswith('.md'):
                continue
            markdown_files.append(filename)
        markdown_files.sort()
        return markdown_files

    def _generate_mirror_file(self, mirror_definitions, page_template, markdown_dir, markdown_file, mirror_filename_template):
        mirror_file = mirror_filename_template.render(markdown_filename=markdown_file)

        print("Generating [%s]" % mirror_file)

        markdown_file_path = os.path.join(markdown_dir, markdown_file)
        with open(markdown_file_path, 'r', encoding='utf8') as f:
            markdown_title = f.readline().rstrip('\n')
        markdown_filename_escaped=self._escape_markdown(markdown_file)

        mirrors = []
        for mirror_definition in mirror_definitions:
            mirror = {}
            template = jinja2.Environment().from_string(mirror_definition['title'])
            mirror['title'] = template.render(
                markdown_filename=markdown_file,
                markdown_filename_escaped=markdown_filename_escaped)
            template = jinja2.Environment().from_string(mirror_definition['url'])
            mirror['url'] = template.render(
                markdown_filename=markdown_file,
                markdown_filename_escaped=markdown_filename_escaped)
            mirrors.append(mirror)

        mirror_content = page_template.render(
            markdown_title=markdown_title,
            markdown_filename=markdown_file,
            markdown_filename_escaped=markdown_filename_escaped,
            mirrors=mirrors)

        mirror_file_path = os.path.join(markdown_dir, mirror_file)
        with open(mirror_file_path, 'w', encoding='utf8') as f:
            f.write(mirror_content)
        
    def _do_generate(self, mirror_definitions, mirror_filename_template_string, mirror_filename_match_string, mirror_page_template, markdown_dir):
        markdown_files = self._get_markdown_files(markdown_dir)
        template = jinja2.Environment().from_string(mirror_page_template)
        mirror_filename_template = jinja2.Environment().from_string(mirror_filename_template_string)
        mirror_filename_matcher = re.compile(mirror_filename_match_string)
        for markdown_file in markdown_files:
            # Prevent mirror files for mirror files
            if mirror_filename_matcher.match(markdown_file):
                continue
            self._generate_mirror_file(mirror_definitions, template, markdown_dir, markdown_file, mirror_filename_template)

    def _add_mirror_header_to_page(self, markdown_text, markdown_file, mirror_filename_template):
        mirror_file = mirror_filename_template.render(markdown_filename=markdown_file)

        # Search for title patterns
        title_match_1 = self.title_pattern_1.search(markdown_text)
        title_match_2 = self.title_pattern_2.search(markdown_text)

        # Stop if the mirror link already exists
        mirror_link = "[mirrors](%s)" % mirror_file
        if mirror_link in markdown_text:
            return markdown_text

        print("Adding mirror link to [%s]" % markdown_file)

        # If a title is found, add the mirror link after it
        if title_match_1:
            # For title format 1
            title_end = title_match_1.end()
            updated_markdown = "%s\n\n(%s)%s" % (markdown_text[:title_end], mirror_link, markdown_text[title_end:])
        elif title_match_2:
            # For title format 2
            title_end = title_match_2.end()
            updated_markdown = "%s\n\n(%s)%s" % (markdown_text[:title_end], mirror_link, markdown_text[title_end:])
        else:
            # If no title is found, return the original markdown
            updated_markdown = markdown_text
        return updated_markdown

    def _do_add_header(self, mirror_filename_template_string, mirror_filename_match_string, markdown_dir):
        markdown_files = self._get_markdown_files(markdown_dir)
        mirror_filename_template = jinja2.Environment().from_string(mirror_filename_template_string)
        mirror_filename_matcher = re.compile(mirror_filename_match_string)
        for markdown_file in markdown_files:
            # Prevent header in mirror files
            if mirror_filename_matcher.match(markdown_file):
                continue
        
            markdown_file_path = os.path.join(markdown_dir, markdown_file)
            with open(markdown_file_path, 'r', encoding='utf8') as f:
                page_content = self._add_mirror_header_to_page(f.read(), markdown_file, mirror_filename_template)
            with open(markdown_file_path, 'w', encoding='utf8') as f:
                f.write(page_content)

    def run(self, argv):
        args = self._parse_args(argv)
        config = self._load_config(args.config_file)

        if args.action == "generate":
            self._do_generate(
                config['mirrors'],
                config['mirror_filename_template'],
                config['mirror_filename_matcher'],
                config['mirror_page_template'],
                args.markdown_dir)
        elif args.action == "add_header":
            self._do_add_header(
                config['mirror_filename_template'],
                config['mirror_filename_matcher'],
                args.markdown_dir)
        else:
            args.print_usage()
            sys.exit(0)

if __name__ == "__main__":
    main = Main()
    main.run(sys.argv[1:])