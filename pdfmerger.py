import sys
import os
from pypdf import PdfWriter, PdfReader


def main():
    # ── 1. Parse command-line arguments ──────────────────────────────────────
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    extract_text = "--extract-text" in flags

    # ── 2. Validate that an output name was supplied ──────────────────────────
    if not args:
        print("Error: Merge file name not specified.")
        print("Usage: python pdfmerger.py filename")
        sys.exit(1)

    base_name = args[0]
    output_filename = base_name if base_name.lower().endswith(".pdf") else base_name + ".pdf"

    # ── 3. Create the merger (writer) object ──────────────────────────────────
    writer = PdfWriter()

    # ── 4 & 5. Collect .pdf files from the current directory ─────────────────
    all_files = os.listdir(".")
    pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]

    # ── 6. Sort alphabetically ────────────────────────────────────────────────
    pdf_files.sort()

    # ── 9. Exclude the output file (avoid merging into itself) ────────────────
    pdf_files = [f for f in pdf_files if f.lower() != output_filename.lower()]

    # ── 7. Report files found ─────────────────────────────────────────────────
    print(f"\nPDF files found: {len(pdf_files)}")
    if pdf_files:
        print("List:")
        for f in pdf_files:
            print(f"  {f}")
    else:
        print("No PDF files to merge. Exiting.")
        sys.exit(0)

    # ── 8. Prompt user to continue ────────────────────────────────────────────
    print()
    answer = input("Continue (y/n): ").strip().lower()
    if answer != "y":
        print("Operation cancelled.")
        sys.exit(0)

    # ── 9. Append each PDF into the writer ───────────────────────────────────
    merged_count = 0
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                writer.add_page(page)
            merged_count += 1
            print(f"  Added: {pdf_file}  ({len(reader.pages)} page(s))")
        except Exception as e:
            print(f"  WARNING: Could not read '{pdf_file}': {e}")

    if merged_count == 0:
        print("\nNo files were successfully merged. Exiting.")
        sys.exit(1)

    # ── 10. Export the merged PDF ─────────────────────────────────────────────
    with open(output_filename, "wb") as out_file:
        writer.write(out_file)
    print(f"\n✓ Merged {merged_count} file(s) → '{output_filename}'")

    # ── Bonus: Extract text ───────────────────────────────────────────────────
    if extract_text:
        txt_filename = base_name + ".txt"
        print(f"\nExtracting text → '{txt_filename}' ...")
        merged_reader = PdfReader(output_filename)
        text_parts = []
        for i, page in enumerate(merged_reader.pages, start=1):
            page_text = page.extract_text() or ""
            text_parts.append(f"--- Page {i} ---\n{page_text}\n")
        full_text = "\n".join(text_parts)
        with open(txt_filename, "w", encoding="utf-8") as txt_file:
            txt_file.write(full_text)
        print(f"✓ Text extracted → '{txt_filename}'  ({len(merged_reader.pages)} page(s) processed)")


if __name__ == "__main__":
    main()
