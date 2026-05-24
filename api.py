import os
import io
import numpy as np
import joblib
from PIL import Image, ImageDraw, ImageFont, ImageChops
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import data_gen
import train

# Configuration
MODEL_PATH = "ranjana_rf_model.pkl"
CLASSES_PATH = "classes.txt"
DATASET_DIR = "dataset"
GLYPH_CONFIG_PATH = "glyph_configs.json"
LIGATURE_CONFIG_PATH = "ligature_configs.json"

# Build a single transliteration → Devanagari lookup map
DEVANAGARI_MAP = {**data_gen.CONSONANTS, **data_gen.VOWELS, **data_gen.NUMBERS, **data_gen.SYMBOLS}

def load_glyph_configs():
    if os.path.exists(GLYPH_CONFIG_PATH):
        with open(GLYPH_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_glyph_configs(configs):
    with open(GLYPH_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(configs, f, ensure_ascii=False, indent=2)

def load_ligature_configs():
    if os.path.exists(LIGATURE_CONFIG_PATH):
        with open(LIGATURE_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_ligature_configs(configs):
    with open(LIGATURE_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(configs, f, ensure_ascii=False, indent=2)

# Regex for Devanagari grapheme clusters:
# Consonant follow by any number of (Virama + Consonant) and optional (Vowel Sign or other modifiers)
# Or a standalone Vowel
# Standard Devanagari Range: \u0900-\u097F
# Consonants: \u0915-\u0939, \u0958-\u095F
# Vowels: \u0905-\u0914
# Virama: \u094D
# Matras/Modifiers: \u0901-\u0903, \u093E-\u094C, \u094D, \u0951-\u0957, \u0962-\u0963
CLUSTER_REGEX = r'[\u0915-\u0939\u0958-\u095F][\u094D]?[\u093E-\u094C\u0901-\u0903\u0951-\u0957\u0962-\u0963]?|[\u0905-\u0914]'

app = FastAPI(title="Calligraphic-Python API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Configuration
MODEL_PATH = "ranjana_rf_model.pkl"
CLASSES_PATH = "classes.txt"
DATASET_DIR = "dataset"

# In-memory job state
job_state = {
    "generate": {"status": "idle", "message": ""},
    "train": {"status": "idle", "message": "", "accuracy": None},
}

class StatusResponse(BaseModel):
    model_exists: bool
    dataset_exists: bool
    classes_count: int
    dataset_size: int

def get_dataset_info():
    if not os.path.exists(DATASET_DIR):
        return 0, 0
    classes = [d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))]
    total_files = sum([len(files) for r, d, files in os.walk(DATASET_DIR)])
    return len(classes), total_files

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/status", response_model=StatusResponse)
async def get_status():
    classes_count, dataset_size = get_dataset_info()
    return StatusResponse(
        model_exists=os.path.exists(MODEL_PATH),
        dataset_exists=os.path.exists(DATASET_DIR),
        classes_count=classes_count,
        dataset_size=dataset_size
    )

@app.get("/job/{job_name}")
async def get_job_status(job_name: str):
    if job_name not in job_state:
        return {"error": "Unknown job"}
    return job_state[job_name]

def run_generate():
    job_state["generate"]["status"] = "running"
    job_state["generate"]["message"] = "Generating dataset..."
    try:
        data_gen.create_dataset()
        job_state["generate"]["status"] = "done"
        job_state["generate"]["message"] = "Dataset generated successfully!"
    except Exception as e:
        job_state["generate"]["status"] = "error"
        job_state["generate"]["message"] = str(e)

def run_train():
    job_state["train"]["status"] = "running"
    job_state["train"]["message"] = "Training model..."
    job_state["train"]["accuracy"] = None
    try:
        accuracy = train.train()
        job_state["train"]["status"] = "done"
        job_state["train"]["accuracy"] = accuracy
        job_state["train"]["message"] = f"Training complete! Accuracy: {accuracy:.1%}"
    except Exception as e:
        job_state["train"]["status"] = "error"
        job_state["train"]["message"] = str(e)

@app.post("/generate")
async def generate_data(background_tasks: BackgroundTasks):
    if job_state["generate"]["status"] == "running":
        return {"message": "Generation already running"}
    job_state["generate"]["status"] = "idle"
    background_tasks.add_task(run_generate)
    return {"message": "Data generation started"}

@app.post("/train")
async def train_model(background_tasks: BackgroundTasks):
    if job_state["train"]["status"] == "running":
        return {"message": "Training already running"}
    job_state["train"]["status"] = "idle"
    background_tasks.add_task(run_train)
    return {"message": "Training started"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(CLASSES_PATH):
        return {"error": "Model not trained yet"}

    # Load model and classes
    model = joblib.load(MODEL_PATH)
    with open(CLASSES_PATH, "r", encoding="utf-8") as f:
        class_names = f.read().splitlines()

    # Read and process image
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert('L')
    img = img.resize((64, 64))
    img_array = np.array(img).flatten() / 255.0
    img_array = img_array.reshape(1, -1)

    # Predict
    prediction = model.predict(img_array)
    probs = model.predict_proba(img_array)
    confidence = float(np.max(probs))
    class_idx = int(prediction[0])
    
    predicted_class = class_names[class_idx]
    devanagari = DEVANAGARI_MAP.get(predicted_class, predicted_class)

    return {
        "predicted_class": predicted_class,
        "devanagari": devanagari,
        "confidence": confidence,
        "all_probs": {class_names[i]: float(probs[0][i]) for i in range(len(class_names))}
    }

class MonogramRequest(BaseModel):
    text: str
    font_size: int = 80
    fg_color: str = "#2d1b69"
    bg_color: Optional[str] = "#ffffff"  # None = transparent
    padding: int = 40
    line_spacing: int = 10
    vertical: bool = True
    use_overrides: bool = True

class GlyphSaveRequest(BaseModel):
    char: str
    type: str  # "full", "half", "first", "middle", "last"
    scale: float
    x_offset: int
    y_offset: int
    rotation: float = 0.0
    skew_x: float = 0.0
    skew_y: float = 0.0
    crop_top: int = 0
    crop_bottom: int = 0
    crop_left: int = 0
    crop_right: int = 0

class LigatureCharConfig(BaseModel):
    char: str
    scale: float = 1.0
    x_offset: int = 0
    y_offset: int = 0
    y_advance: Optional[int] = None
    rotation: float = 0.0
    skew_x: float = 0.0
    skew_y: float = 0.0
    crop_top: int = 0
    crop_bottom: int = 0
    crop_left: int = 0
    crop_right: int = 0
    mask: Optional[str] = None
    adjustments: Optional[list[dict]] = None

class LigatureSaveRequest(BaseModel):
    sequence: str # e.g. "क+र"
    chars: list[LigatureCharConfig]
    mask: Optional[str] = None # Base64 PNG mask for corrections
    adjustments: Optional[list[dict]] = None # Manual moves/extends

@app.get("/glyphs")
async def get_glyphs():
    return load_glyph_configs()

@app.post("/glyphs/save")
async def save_glyph(req: GlyphSaveRequest):
    configs = load_glyph_configs()
    if req.char not in configs:
        configs[req.char] = {}
    configs[req.char][req.type] = {
        "scale": req.scale,
        "x_offset": req.x_offset,
        "y_offset": req.y_offset,
        "rotation": req.rotation,
        "skew_x": req.skew_x,
        "skew_y": req.skew_y,
        "crop_top": req.crop_top,
        "crop_bottom": req.crop_bottom,
        "crop_left": req.crop_left,
        "crop_right": req.crop_right
    }
    save_glyph_configs(configs)
    return {"message": "Config saved"}

@app.get("/ligatures")
async def get_ligatures():
    return load_ligature_configs()

@app.post("/ligatures/save")
async def save_ligature(req: LigatureSaveRequest):
    configs = load_ligature_configs()
    configs[req.sequence] = [c.dict() for c in req.chars]
    save_ligature_configs(configs)
    return {"message": "Ligature rule saved"}

@app.post("/glyphs/preview")
async def preview_glyph(req: GlyphSaveRequest):
    # Reuse monogram logic for a single char
    font_path = "NithyaRanjanaDU-Regular.otf"
    font_size = 120
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        return {"error": f"Font load failed: {e}"}

    # If it's a half-letter, append halant if not present
    display_char = req.char
    if req.type == "half" and not display_char.endswith('\u094D'):
        display_char += '\u094D'

    # Create a larger canvas for the initial render to avoid clipping before crop
    temp_img = Image.new("RGBA", (300, 300), color=(255, 255, 255, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    scaled_font_size = int(font_size * req.scale)
    scaled_font = ImageFont.truetype(font_path, scaled_font_size)
    
    bb = scaled_font.getbbox(display_char)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    
    # Draw at center
    x = (300 - w) // 2 - bb[0]
    y = (300 - h) // 2 - bb[1]
    temp_draw.text((x, y), display_char, font=scaled_font, fill=(45, 27, 105, 255))
    
    # Apply transformations (Rotation and Skew)
    if req.rotation != 0 or req.skew_x != 0 or req.skew_y != 0:
        if req.rotation != 0:
            temp_img = temp_img.rotate(req.rotation, resample=Image.BICUBIC, expand=False)
        
        if req.skew_x != 0 or req.skew_y != 0:
            tw, th = temp_img.size
            temp_img = temp_img.transform(temp_img.size, Image.AFFINE, 
                                         (1, -req.skew_x, req.skew_x * (th/2), -req.skew_y, 1, req.skew_y * (tw/2)),
                                         resample=Image.BICUBIC)
    
    # Apply cropping by clearing pixels
    if req.crop_top > 0 or req.crop_bottom > 0 or req.crop_left > 0 or req.crop_right > 0:
        tw, th = temp_img.size
        c_left = x + bb[0] + req.crop_left
        c_top = y + bb[1] + req.crop_top
        c_right = x + bb[2] - req.crop_right
        c_bottom = y + bb[3] - req.crop_bottom
        
        if c_top > 0: temp_img.paste((0,0,0,0), (0, 0, tw, c_top))
        if c_bottom < th: temp_img.paste((0,0,0,0), (0, c_bottom, tw, th))
        if c_left > 0: temp_img.paste((0,0,0,0), (0, 0, c_left, th))
        if c_right < tw: temp_img.paste((0,0,0,0), (c_right, 0, tw, th))

    orig_w, orig_h = w, h
    x_base = (200 - orig_w) // 2
    y_base = (200 - orig_h) // 2

    img = Image.new("RGBA", (200, 200), color=(255, 255, 255, 0))
    crop_bb = (x + bb[0], y + bb[1], x + bb[2], y + bb[3])
    cropped_part = temp_img.crop(crop_bb)
    img.paste(cropped_part, (x_base + req.x_offset, y_base + req.y_offset))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@app.get("/glyph/preview")
async def glyph_preview(char: str):
    font_path = "NithyaRanjanaDU-Regular.otf"
    font_size = 150
    try:
        font = ImageFont.truetype(font_path, font_size)
        bb = font.getbbox(char)
        w, h = bb[2]-bb[0], bb[3]-bb[1]
        img = Image.new("RGBA", (w+40, h+40), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.text((20-bb[0], 20-bb[1]), char, font=font, fill=(45, 27, 105, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return Response(content=buf.getvalue(), media_type="image/png")
    except Exception as e:
        return {"error": str(e)}

@app.post("/ligatures/preview")
async def preview_ligature(req: LigatureSaveRequest):
    font_path = "NithyaRanjanaDU-Regular.otf"
    font_size = 100
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        return {"error": f"Font load failed: {e}"}

    # Calculate canvas size based on sequence
    # Use a generous vertical space
    img_h = 200 + (len(req.chars) * (font_size + 20))
    img = Image.new("RGBA", (400, img_h), color=(255, 255, 255, 0))
    
    y_cursor = 50
    ascent, descent = font.getmetrics()
    line_height = ascent + descent

    for c in req.chars:
        # Standard sequential rendering with surgical hooks
        try:
            # 1. Render base character glyph
            char_font = ImageFont.truetype(font_path, int(font_size * c.scale))
            # Get bbox for centering
            bb = char_font.getbbox(c.char)
            cw, ch = bb[2] - bb[0], bb[3] - bb[1]
            
            # Create a layer for this character
            # Add padding for rotation/skewing/stretching
            char_layer = Image.new("RGBA", (cw + 200, ch + 200), (0,0,0,0))
            char_draw = ImageDraw.Draw(char_layer)
            # Render at fixed offset
            char_draw.text((100 - bb[0], 100 - bb[1]), c.char, font=char_font, fill=(45, 27, 105, 255))
            
            # 4. Standard Transforms
            # Skewing
            if c.skew_x != 0 or c.skew_y != 0:
                cw_layer, ch_layer = char_layer.size
                char_layer = char_layer.transform(
                    (cw_layer, ch_layer),
                    Image.AFFINE,
                    (1, -c.skew_x, c.skew_x * (ch_layer/2), -c.skew_y, 1, c.skew_y * (cw_layer/2)),
                    Image.Resampling.BICUBIC
                )

            if c.rotation != 0:
                char_layer = char_layer.rotate(c.rotation, expand=True, resample=Image.Resampling.BICUBIC)
            
            if any([c.crop_top, c.crop_bottom, c.crop_left, c.crop_right]):
                bbox = char_layer.getbbox()
                if bbox:
                    bl, bt, br, bb_y = bbox
                    cw_layer, ch_layer = char_layer.size
                    if c.crop_top > 0:
                        char_layer.paste((0,0,0,0), (0, 0, cw_layer, bt + c.crop_top))
                    if c.crop_bottom > 0:
                        char_layer.paste((0,0,0,0), (0, bb_y - c.crop_bottom, cw_layer, ch_layer))
                    if c.crop_left > 0:
                        char_layer.paste((0,0,0,0), (0, 0, bl + c.crop_left, ch_layer))
                    if c.crop_right > 0:
                        char_layer.paste((0,0,0,0), (br - c.crop_right, 0, cw_layer, ch_layer))

            # 5. Calculate final position
            x_pos = (400 - char_layer.width) // 2 + c.x_offset
            y_pos = y_cursor + c.y_offset

            # 6. Apply Per-Char Surgical Mask (Eraser) using final coordinates
            if c.mask:
                try:
                    import base64
                    mask_data = base64.b64decode(c.mask.split(',')[1])
                    mask_img = Image.open(io.BytesIO(mask_data)).convert("L")
                    char_mask = mask_img.crop((x_pos, y_pos, x_pos + char_layer.width, y_pos + char_layer.height))
                    new_alpha_mask = char_mask.point(lambda x: 0 if x < 128 else 255, 'L')
                    orig_alpha = char_layer.getchannel('A')
                    final_alpha = ImageChops.darker(orig_alpha, new_alpha_mask)
                    char_layer.putalpha(final_alpha)
                except Exception as e:
                    print(f"Char mask error: {e}")

            # 7. Apply Per-Char Manual Adjustments (Cut/Move/Extend) using final coordinates
            if c.adjustments:
                try:
                    for adj in c.adjustments:
                        lx = adj['x'] - x_pos
                        ly = adj['y'] - y_pos
                        low = adj['ow']
                        loh = adj['oh']
                        ldx = adj['dx']
                        ldy = adj['dy']
                        
                        part = char_layer.crop((lx, ly, lx + low, ly + loh))
                        if adj.get('mode') == 'move':
                            char_layer.paste((0,0,0,0), (int(lx), int(ly), int(lx+low), int(ly+loh)))
                        if adj.get('mode') == 'extend' and adj.get('fw') and adj.get('fh'):
                            part = part.resize((int(abs(adj['fw'])), int(abs(adj['fh']))), Image.Resampling.LANCZOS)
                        char_layer.paste(part, (int(lx+ldx), int(ly+ldy)), part)
                except Exception as e:
                    print(f"Char adj error: {e}")

            # Finally composite into main image
            img.paste(char_layer, (x_pos, y_pos), char_layer)
            
            # Advance
            if c.y_advance:
                y_cursor += c.y_advance
            else:
                y_cursor += (ch + 20) # Default
        except Exception as e:
            print(f"Layer failed: {e}")

    # Do not crop tightly to prevent coordinate shifting for surgical tools
    bbox = img.getbbox()
    if not bbox:
        img = Image.new("RGBA", (400, 200), (0,0,0,0))

    # Apply Global Mask (Legacy)
    if req.mask:
        try:
            import base64
            mask_data = base64.b64decode(req.mask.split(",")[1])
            mask_img = Image.open(io.BytesIO(mask_data)).convert("L")
            mask_img = mask_img.resize(img.size, Image.Resampling.LANCZOS)
            final_alpha = img.split()[3]
            new_alpha_mask = mask_img.point(lambda x: 0 if x < 128 else 255, '1')
            combined_alpha = Image.new("L", img.size, 0)
            combined_alpha.paste(final_alpha, (0, 0), mask=new_alpha_mask)
            img.putalpha(combined_alpha)
        except Exception as e:
            print(f"Global mask failed: {e}")

    if req.adjustments:
        try:
            for adj in req.adjustments:
                # adj: {x, y, ow, oh, fw, fh, dx, dy, mode}
                # Capture the part
                part = img.crop((adj['x'], adj['y'], adj['x']+adj['ow'], adj['y']+adj['oh']))
                
                # If mode is 'move', erase the source (Cut)
                if adj.get('mode') == 'move':
                    draw = ImageDraw.Draw(img)
                    draw.rectangle([adj['x'], adj['y'], adj['x']+adj['ow'], adj['y']+adj['oh']], fill=(0,0,0,0))
                
                # If mode is 'extend', stretch the part
                if adj.get('mode') == 'extend' and adj.get('fw') and adj.get('fh'):
                    part = part.resize((int(abs(adj['fw'])), int(abs(adj['fh']))), Image.LANCZOS)
                
                img.paste(part, (int(adj['x']+adj['dx']), int(adj['y']+adj['dy'])), part)
        except Exception as e:
            print(f"Adjustments failed: {e}")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@app.post("/ligatures/inject")
async def inject_ligature(req: LigatureSaveRequest):
    # Render the ligature
    resp = await preview_ligature(req)
    if isinstance(resp, dict) and "error" in resp:
        return resp
    
    # Read the image back
    img_data = b"".join([chunk async for chunk in resp.body_iterator])
    img = Image.open(io.BytesIO(img_data))
    
    # Training sample: white background
    bg = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, (0, 0), img)
    
    try:
        label = f"lig_{req.sequence.replace('+', '_')}"
        data_gen.inject_custom_sample(bg, label)
        return {"message": f"Ligature '{req.sequence}' added to training set as '{label}'. Please retrain to activate."}
    except Exception as e:
        return {"error": f"Injection failed: {e}"}

@app.post("/monogram")
async def generate_monogram(req: MonogramRequest):
    font_path = "NithyaRanjanaDU-Regular.otf"
    text = req.text.strip()
    if not text:
        return {"error": "No text provided"}

    # Transliterate if it's likely Romanized (no Devanagari chars detected)
    import re
    if not re.search(r'[\u0900-\u097F]', text):
        # We need to re-import or re-calculate DEVANAGARI_MAP because it's static
        # For simplicity, move the conversion logic here
        translit_map = {**data_gen.CONSONANTS, **data_gen.VOWELS, **data_gen.NUMBERS, **data_gen.SYMBOLS}
        matra_map = data_gen.MATRAS
        
        # Sort keys by length descending to match longer ones first (kh, aa, etc)
        keys = sorted(translit_map.keys(), key=len, reverse=True)
        vowel_keys = sorted(data_gen.VOWELS.keys(), key=len, reverse=True)
        
        converted = ""
        i = 0
        last_was_consonant = False
        
        while i < len(text):
            match = False
            # Check for vowel signs if the last character was a consonant
            if last_was_consonant:
                for vk in vowel_keys:
                    if text[i:i+len(vk)] == vk:
                        converted += matra_map.get(vk, data_gen.VOWELS[vk])
                        i += len(vk)
                        match = True
                        last_was_consonant = False # Reset context after a matra
                        break
            
            if not match:
                for k in keys:
                    if text[i:i+len(k)] == k:
                        converted += translit_map[k]
                        i += len(k)
                        match = True
                        # Mark if this was a consonant (but not a halant, though halant+vowel is rare)
                        last_was_consonant = (k in data_gen.CONSONANTS and k != '*')
                        break
            
            if not match:
                converted += text[i]
                i += 1
                last_was_consonant = False
        text = converted

    try:
        font = ImageFont.truetype(font_path, req.font_size)
    except Exception as e:
        return {"error": f"Font load failed: {e}"}

    ascent, descent = font.getmetrics()
    # Adding a small buffer to the line height to be safe
    line_height = ascent + descent
    
        # --- Handle Vertical Stacking with Grapheme Clusters ---
    if req.vertical and "\n" not in text:
        import re
        lines = re.findall(CLUSTER_REGEX, text)
        if not lines: # Fallback if regex fails to match anything for some reason
            lines = list(text)
    else:
        lines = text.split("\n")
    
    # --- Fix for Ranjana Font: Reorder 'i' matra to visual order ---
    # The NithyaRanjana font seems to require 'ि' (\u093F) to be BEFORE the consonant.
    i_matra = '\u093F'
    processed_lines = []
    
    for line in lines:
        if i_matra in line:
            # We need to reorder 'ि' to the start of each cluster it belongs to
            # even in horizontal lines.
            clusters = re.findall(CLUSTER_REGEX, line)
            new_line = ""
            for c in clusters:
                if i_matra in c:
                    new_line += i_matra + c.replace(i_matra, '')
                else:
                    new_line += c
            # Append non-cluster characters (like spaces)
            remaining = line
            for c in clusters:
                remaining = remaining.replace(c, '', 1)
            new_line += remaining # Fallback for spaces/other chars
            processed_lines.append(new_line)
        else:
            processed_lines.append(line)
    lines = processed_lines

    # --- Pre-process Ligatures ---
    lig_configs = load_ligature_configs() if req.use_overrides else {}
    merged_lines = []
    skip_next = 0
    for i in range(len(lines)):
        if skip_next > 0:
            skip_next -= 1
            continue
        
        found_lig = False
        for length in range(6, 1, -1):
            if i + length - 1 < len(lines):
                seq = "+".join(lines[i:i+length])
                if seq in lig_configs:
                    merged_lines.append({"text": seq, "type": "ligature", "conf": lig_configs[seq]})
                    skip_next = length - 1
                    found_lig = True
                    break
        if not found_lig:
            merged_lines.append({"text": lines[i], "type": "char"})

    # --- Calculate Bounds ---
    line_widths = []
    total_rendered_height = 0
    configs = load_glyph_configs() if req.use_overrides else {}

    for i, item in enumerate(merged_lines):
        line = item["text"]
        if item["type"] == "ligature":
            max_w = 0
            for conf in item["conf"]:
                f_size = int(req.font_size * conf.get("scale", 1.0))
                tmp_font = ImageFont.truetype(font_path, f_size)
                bb = tmp_font.getbbox(conf["char"])
                max_w = max(max_w, bb[2] - bb[0] + abs(conf.get("x_offset", 0)))
                total_rendered_height += line_height + req.line_spacing
            line_widths.append(max_w)
        else:
            bb = font.getbbox(line)
            line_widths.append(bb[2] - bb[0])
            total_rendered_height += line_height + req.line_spacing

    total_width = max(line_widths) if line_widths else req.font_size
    safety_top = int(req.font_size * 0.15)
    img_w = total_width + req.padding * 2
    img_h = total_rendered_height + req.padding * 2 + safety_top

    # --- Draw ---
    transparent = req.bg_color is None or req.bg_color.lower() == "transparent"
    mode = "RGBA"
    bg = (0, 0, 0, 0) if transparent else (*_hex_to_rgb(req.bg_color), 255)
    img = Image.new(mode, (img_w, img_h), color=bg)
    draw = ImageDraw.Draw(img)
    fg = (*_hex_to_rgb(req.fg_color), 255)
    
    y_cursor = req.padding + safety_top
    
    for i, item in enumerate(merged_lines):
        line = item["text"]
        
        if item["type"] == "ligature":
            char_configs = item["conf"]
            # Render ligature to a temporary layer to apply mask correctly
            lig_layer_h = (len(char_configs) * (req.font_size + req.line_spacing)) + 100
            lig_layer = Image.new("RGBA", (total_width + 100, lig_layer_h), (0,0,0,0))
            lig_y_cursor = 0
            studio_y_cursor = 50
            
            for char_idx, override in enumerate(char_configs):
                display_text = override["char"]
                scale_factor = req.font_size / 100.0
                scale = override.get("scale", 1.0)
                x_off = int(override.get("x_offset", 0) * scale_factor)
                y_off = int(override.get("y_offset", 0) * scale_factor)
                rot = override.get("rotation", 0.0)
                sx = override.get("skew_x", 0.0)
                sy = override.get("skew_y", 0.0)
                c_top = int(override.get("crop_top", 0) * scale_factor)
                c_bottom = int(override.get("crop_bottom", 0) * scale_factor)
                c_left = int(override.get("crop_left", 0) * scale_factor)
                c_right = int(override.get("crop_right", 0) * scale_factor)

                current_font = font
                if scale != 1.0:
                    current_font = ImageFont.truetype(font_path, int(req.font_size * scale))

                bb = current_font.getbbox(display_text)
                w, h = bb[2]-bb[0], bb[3]-bb[1]
                tw, th = w + 100, h + 100
                char_temp = Image.new("RGBA", (tw, th), color=(0,0,0,0))
                char_draw = ImageDraw.Draw(char_temp)
                tx, ty = (tw - w) // 2 - bb[0], (th - h) // 2 - bb[1]
                char_draw.text((tx, ty), display_text, font=current_font, fill=fg)
                
                if rot != 0 or sx != 0 or sy != 0:
                    if rot != 0:
                        char_temp = char_temp.rotate(rot, resample=Image.BICUBIC, expand=False)
                    if sx != 0 or sy != 0:
                        tw, th = char_temp.size
                        char_temp = char_temp.transform((tw, th), Image.AFFINE, 
                                                         (1, -sx, sx * (th/2), -sy, 1, sy * (tw/2)),
                                                         resample=Image.BICUBIC)
                
                if c_top > 0 or c_bottom > 0 or c_left > 0 or c_right > 0:
                    tw, th = char_temp.size
                    crop_x1 = tx + bb[0] + c_left
                    crop_y1 = ty + bb[1] + c_top
                    crop_x2 = tx + bb[2] - c_right
                    crop_y2 = ty + bb[3] - c_bottom
                    if crop_y1 > 0: char_temp.paste((0,0,0,0), (0, 0, tw, crop_y1))
                    if crop_y2 < th: char_temp.paste((0,0,0,0), (0, crop_y2, tw, th))
                    if crop_x1 > 0: char_temp.paste((0,0,0,0), (0, 0, crop_x1, th))
                    if crop_x2 < tw: char_temp.paste((0,0,0,0), (crop_x2, 0, tw, th))
                
                char_img = char_temp.crop((tx + bb[0], ty + bb[1], tx + bb[2], ty + bb[3]))
                
                # Apply Ligature Studio surgical tools by projecting back from studio coordinates
                studio_font = ImageFont.truetype(font_path, int(100 * scale))
                studio_bb = studio_font.getbbox(display_text)
                cw_studio = studio_bb[2] - studio_bb[0]
                ch_studio = studio_bb[3] - studio_bb[1]
                
                bbox_x = (400 - (cw_studio + 200)) // 2 + override.get("x_offset", 0) + 100
                bbox_y = studio_y_cursor + override.get("y_offset", 0) + 100

                c_mask = override.get("mask")
                if c_mask:
                    try:
                        import base64
                        mask_data = base64.b64decode(c_mask.split(',')[1])
                        mask_img = Image.open(io.BytesIO(mask_data)).convert("L")
                        char_mask = mask_img.crop((bbox_x, bbox_y, bbox_x + char_img.width, bbox_y + char_img.height))
                        new_alpha = char_mask.point(lambda x: 0 if x < 128 else 255, 'L')
                        orig_a = char_img.getchannel('A')
                        char_img.putalpha(ImageChops.darker(orig_a, new_alpha))
                    except Exception as e:
                        print(f"Mask error: {e}")

                c_adjs = override.get("adjustments")
                if c_adjs:
                    try:
                        for adj in c_adjs:
                            lx = adj['x'] - bbox_x
                            ly = adj['y'] - bbox_y
                            low = adj['ow']
                            loh = adj['oh']
                            ldx = adj['dx']
                            ldy = adj['dy']
                            
                            part = char_img.crop((lx, ly, lx + low, ly + loh))
                            if adj.get('mode') == 'move':
                                char_img.paste((0,0,0,0), (int(lx), int(ly), int(lx+low), int(ly+loh)))
                            if adj.get('mode') == 'extend' and adj.get('fw') and adj.get('fh'):
                                part = part.resize((int(abs(adj['fw'])), int(abs(adj['fh']))), Image.Resampling.LANCZOS)
                            char_img.paste(part, (int(lx+ldx), int(ly+ldy)), part)
                    except Exception as e:
                        print(f"Adj error: {e}")

                xb = (total_width - char_img.width) // 2
                lig_layer.paste(char_img, (xb + x_off, lig_y_cursor + y_off), char_img)
                
                y_adv = override.get("y_advance")
                if y_adv is not None:
                    lig_y_cursor += int(y_adv * scale_factor)
                    studio_y_cursor += int(y_adv)
                else:
                    lig_y_cursor += line_height + req.line_spacing
                    studio_y_cursor += ch_studio + 20

            # Crop the finished ligature layer to content
            l_bbox = lig_layer.getbbox()
            if l_bbox:
                lig_final = lig_layer.crop(l_bbox)
                
                # Global adjustments and masks are no longer supported
                # as they have been migrated to per-character properties.
                
                x_base = (total_width - lig_final.width) // 2
                img.paste(lig_final, (req.padding + x_base, y_cursor), lig_final)
                
                y_cursor += lig_final.height + req.line_spacing
            else:
                y_cursor += line_height + req.line_spacing
            
            # Since we've handled the whole ligature, we continue to the next merged_line
            continue

        else:
            base_char = line.replace('\u094D', '')
            char_conf = configs.get(base_char, {})
            
            # Position-based variant selection
            if i == 0:
                # Top character: try 'first' then 'full'
                priority = ["first", "full"]
            elif i == len(merged_lines) - 1:
                # Bottom character: try 'last' then 'full'
                priority = ["last", "full"]
            else:
                # Middle characters: prefer 'half' or 'middle' variants
                priority = ["half", "middle", "full"]
            
            override = None
            for p in priority:
                if p in char_conf:
                    override = char_conf[p]
                    break
            
            if not override:
                override = {} # Fallback to empty (default)
            display_text = line
            
            # (Standard rendering logic continues...)
            scale = override.get("scale", 1.0)
            x_off = override.get("x_offset", 0)
            y_off = override.get("y_offset", 0)
            rot = override.get("rotation", 0.0)
            sx = override.get("skew_x", 0.0)
            sy = override.get("skew_y", 0.0)
            c_top = override.get("crop_top", 0)
            c_bottom = override.get("crop_bottom", 0)
            c_left = override.get("crop_left", 0)
            c_right = override.get("crop_right", 0)

            current_font = font
            if scale != 1.0:
                current_font = ImageFont.truetype(font_path, int(req.font_size * scale))

            bb = current_font.getbbox(display_text)
            w, h = bb[2]-bb[0], bb[3]-bb[1]
            tw, th = w + 100, h + 100
            temp_layer = Image.new("RGBA", (tw, th), color=(0,0,0,0))
            temp_draw = ImageDraw.Draw(temp_layer)
            tx, ty = (tw - w) // 2 - bb[0], (th - h) // 2 - bb[1]
            temp_draw.text((tx, ty), display_text, font=current_font, fill=fg)
            
            if rot != 0 or sx != 0 or sy != 0:
                if rot != 0:
                    temp_layer = temp_layer.rotate(rot, resample=Image.BICUBIC, expand=False)
                if sx != 0 or sy != 0:
                    tw_layer, th_layer = temp_layer.size
                    temp_layer = temp_layer.transform((tw_layer, th_layer), Image.AFFINE, 
                                                     (1, -sx, sx * (th_layer/2), -sy, 1, sy * (tw_layer/2)),
                                                     resample=Image.BICUBIC)
            
            if c_top > 0 or c_bottom > 0 or c_left > 0 or c_right > 0:
                tw_layer, th_layer = temp_layer.size
                crop_x1 = tx + bb[0] + c_left
                crop_y1 = ty + bb[1] + c_top
                crop_x2 = tx + bb[2] - c_right
                crop_y2 = ty + bb[3] - c_bottom
                if crop_y1 > 0: temp_layer.paste((0,0,0,0), (0, 0, tw_layer, crop_y1))
                if crop_y2 < th_layer: temp_layer.paste((0,0,0,0), (0, crop_y2, tw_layer, th_layer))
                if crop_x1 > 0: temp_layer.paste((0,0,0,0), (0, 0, crop_x1, th_layer))
                if crop_x2 < tw_layer: temp_layer.paste((0,0,0,0), (crop_x2, 0, tw_layer, th_layer))
            
            cluster_img = temp_layer.crop((tx + bb[0], ty + bb[1], tx + bb[2], ty + bb[3]))
            
            x_base = (total_width - (bb[2]-bb[0])) // 2
            img.paste(cluster_img, (req.padding + x_base + x_off, y_cursor + y_off), cluster_img)
            
            y_cursor += line_height + req.line_spacing

    # --- Return PNG stream ---
    buf = io.BytesIO()
    fmt = "PNG"  # PNG supports transparency
    img.save(buf, format=fmt)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png",
                             headers={"Content-Disposition": 'inline; filename="ranjana_monogram.png"'})


def _hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
