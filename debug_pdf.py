from pypdf import PdfReader
import re

def reconstruct_paragraphs(text):
    """Merges fragmented lines into paragraphs (handles bad PDF/DOCX conversions)."""
    lines = text.split('\n')
    cleaned_lines = []
    buffer = ""
    
    for line in lines:
        line = line.strip()
        
        if not line:
            # Only flush if the buffer seems to be a complete sentence/header
            if buffer and buffer.endswith(('.', '!', '?', ':')):
                cleaned_lines.append(buffer)
                buffer = ""
            # Otherwise, assume it's an intra-paragraph break (double spacing) and keep buffer
            continue
            
        # If we have a buffer, check if we should merge
        if buffer:
            # If buffer ended with punctuation, we usually expect a flush, 
            # BUT if we are here, it means we didn't hit a blank line (or we ignored it).
            # If the previous line ended with punctuation, and we see a new line now:
            # It implies a new sentence started immediately? 
            # Or maybe it was a header like "ASUNTO:" followed by text?
            
            # Let's keep the merge logic simple: 
            # If there was a blank line in betweeen, we handled it above.
            # If we are contiguous lines:
            
            # Case 1: Buffer ended with punctuation.
            # Usually creates a new block unless it's a list or something.
            # But wait, if I skipped the blank line, I *must* merge now with a space.
            
            # Let's refine: The "Flush on blank line IF punct" logic handles the paragraph breaks.
            # So here, we just ALWAYS merge?
            # No, because if I have:
            # "Hello."
            # "World."
            # (No blank line). distinct paragraphs?
            # Ideally PDF paragraphs have blank lines.
            
            # Let's try: Always merge with space, UNLESS the previous buffer ended with punctuation AND the current line looks like a Start of Sentence (Uppercase)?
            # But "con todo." starts with lowercase. "fiesta" starts with lowercase.
            
            # Safety: If buffer ends with punct, and current line starts with Upper... might be separate.
            # But in the "double space" world, the blank line logic rules.
            # If we are here, and buffer exists, we merge.
            
            # One edge case: Headers usually have no punct? "IDEA CREATIVA:" has colon.
            # "ASUNTO: Propuesta..."
            # ASUNTO: -> Ends with colon. 
            # Propuesta -> Starts with Upper.
            # If there was a blank line, `ASUNTO:` would output. `Propuesta` would be new line.
            # That might be OK?
            
            # Let's stick to the "Flush on blank line ONLY if Punctuation" rule.
            # And here, we just merge.
             buffer += " " + line
             
             # Wait, if `ASUNTO:` was followed by `Propuesta` on next line (no blank),
             # It becomes `ASUNTO: Propuesta`. This is Desirable!
             
             # What if "End of sentence." \n "Start of new." (No blank)
             # Becomes "End of sentence. Start of new." -> One paragraph. 
             # Also usually fine for analysis.
             
        else:
            buffer = line
            
    if buffer: cleaned_lines.append(buffer)
    return "\n".join(cleaned_lines)

file_path = "Prueba HNKN (1).pdf"
print(f"--- Processing {file_path} ---")

try:
    reader = PdfReader(file_path)
    raw_text = "\n".join([p.extract_text() for p in reader.pages])
    
    cleaned = reconstruct_paragraphs(raw_text)
    print("\n[CLEANED TEXT PREVIEW (First 1000 chars)]:")
    print(cleaned[:1000])

except Exception as e:
    print(f"Error: {e}")
