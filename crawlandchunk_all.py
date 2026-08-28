import requests
from bs4 import BeautifulSoup
import csv
import os
import re

# Patterns
heading_pattern = re.compile(r'^(\d+)\.\d+\.\d+\.?.*')  # e.g. 12.1.4.
condic_pattern = re.compile(r'\bcondic(?!io)(?!ion)\w*\b', re.IGNORECASE)
subsection_marker_pattern = re.compile(r'^(pr\.|\d+\.)$')

rows = []

for book_num in range(1, 51):
    url = f'https://droitromain.univ-grenoble-alpes.fr/Corpus/d-{book_num:02d}.htm'
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"Skipping book {book_num} due to error: {e}")
        continue

    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text('\n')
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    current_heading = None
    current_lines = []
    blocks = []

    # Group lines under headings in document order
    for line in lines:
        m = heading_pattern.match(line)
        if m:
            # close previous block
            if current_heading is not None:
                blocks.append((current_heading, current_lines))
            current_heading = line.split()[0]  # e.g. "12.1.4."
            current_lines = [line]
        else:
            if current_heading is not None:
                current_lines.append(line)

    if current_heading is not None:
        blocks.append((current_heading, current_lines))

    # Process each block
    for heading, blines in blocks:
        m = heading_pattern.match(heading)
        if not m:
            continue

        # sanity check: heading's book number should match current book_num
        heading_book = int(m.group(1))
        if heading_book != book_num:
            continue

        body_lines = blines[1:]  # skip heading line
        if not body_lines:
            continue

        has_markers = any(subsection_marker_pattern.match(l) for l in body_lines)
        subsections = []

        if has_markers:
            current_subheading = None
            current_sub_lines = []

            for line in body_lines:
                if subsection_marker_pattern.match(line):
                    # close previous subsection
                    if current_subheading is not None:
                        body_text = '\n'.join(current_sub_lines).strip()
                        subsections.append((current_subheading, body_text))
                    elif current_sub_lines:
                        # text before first explicit marker → implicit principium
                        body_text = '\n'.join(current_sub_lines).strip()
                        subsections.append(('pr. (implicit)', body_text))
                    current_subheading = line
                    current_sub_lines = []
                else:
                    current_sub_lines.append(line)

            # tail subsection
            if current_subheading is not None:
                body_text = '\n'.join(current_sub_lines).strip()
                subsections.append((current_subheading, body_text))
            elif current_sub_lines:
                body_text = '\n'.join(current_sub_lines).strip()
                subsections.append(('[entire fragment]', body_text))
        else:
            # fragment without internal markers
            body_text = '\n'.join(body_lines).strip()
            subsections.append(('[entire fragment]', body_text))

        # Filter subsections by condic* pattern
        for subheading, body in subsections:
            if condic_pattern.search(body):
                rows.append({
                    'book': book_num,
                    'heading': heading,
                    'subsection': subheading,
                    'text': body
                })

# Write single CSV
os.makedirs('output', exist_ok=True)
out_path = os.path.join('output', 'condic_all_books_condicstar_narrow.csv')

with open(out_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['book', 'heading', 'subsection', 'text'])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f"Total rows extracted across books 1–50: {len(rows)}")
print(f"Written to: {out_path}")