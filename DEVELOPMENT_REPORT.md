# Agile Development Report: Ranjana Script AI Studio Improvements

**Project**: Calligraphic-Python (Ranjana Calligraphic Script Recognition & Monogram Pipeline)  
**Methodology**: Agile (Iterative Development)  
**Date**: 2026-02-21

---

## 1. Project Overview & Agile Context
This project aims to bridge the gap between AI-driven character recognition and traditional calligraphic art (Ranjana script). Following an Agile model, we prioritized features based on user feedback and technical necessity, iterating from basic recognition to complex script features like conjuncts (half-letters).

---

## 2. Sprint Backlog & Planning
Initial assessment identified three critical areas for the current session:
1.  **Model Robustness**: Accuracy was limited by a small dataset (21 samples/class).
2.  **System Conflicts**: Windows case-insensitive filesystem caused issues with 't' vs 'T' character folders.
3.  **Linguistic Completeness**: Lack of support for "half letters" (virama/halant), essential for Devanagari-based scripts.

---

## 3. Iteration 1: Foundation & Accuracy
**Goal**: Resolve system conflicts and improve recognition performance.

### Step 1: Research & Diagnosis
*   **Action**: Analyzed `data_gen.py` and `index.html`. 
*   **Finding**: Confirmed that using Devanagari character names for folders resolved the Windows "Case Sensitivity" conflict between labels like 'k' and 'K'.

### Step 2: Dataset Expansion (Data Augmentation v2.0)
*   **Action**: Modified `data_gen.py` to increase samples from **20 to 100 per class**.
*   **Technical Detail**: Introduced random scaling (0.85x - 1.15x) and subtle Gaussian noise to simulate the variability of hand-drawn calligraphy.
*   **Result**: Expanded dataset to **4,343 images**.

### Step 3: Incremental Training
*   **Action**: Executed `train.py` using the expanded dataset.
*   **Outcome**: Successfully retrained the Random Forest model with an updated accuracy of **45%** on the noisier, more diverse test set.

---

## 4. Iteration 2: Advanced Script Features
**Goal**: Implement linguistic features to support natural Ranjana writing.

### Step 4: Virama (Halant) Integration
*   **Action**: Updated transliteration mapping across `data_gen.py`, `api.py`, and `index.html`.
*   **Feature**: Defined `*` as the transliteration symbol for the Devanagari Virama (`्`).

### Step 5: Grapheme-Aware Rendering Engine
*   **Problem**: Vertical monogram generators often split characters by Unicode code point, which breaks conjuncts (e.g., 's' + 'halant' + 'k').
*   **Action**: Implemented a **Regex-based Grapheme Splitter** in `api.py`.
*   **Logic**: `[\u0905-\u0939\u0958-\u095F](?:[\u094D][\u0905-\u0939\u0958-\u095F])*[\u093E-\u094C\u094D\u0901-\u0903]?`.
*   **Result**: Conjuncts and vowel signs now stay attached to their base consonants during vertical stacking.

### Step 6: Backend Transliteration Layer
*   **Action**: Added an internal transliteration check in the `/monogram` endpoint to support mixed Romanized/Devanagari inputs directly from API clients.

---

## 5. Verification & Quality Assurance (QA)
*   **Infrastructure**: Resolved a TCP port conflict (10048) on port 8000 by identifying and terminating orphaned Python processes.
*   **Manual Test**: Verified the conjunct `s*ka` (स्का) via the API.
*   **Visual Proof**: Generated `test_conjunct.png` showing perfect vertical rendering of the half-letter 's' with 'k'.

---

## 6. Iteration 3: Transliteration Case Mapping Correction
**Goal**: Correct standard IAST transliteration logic for dental versus retroflex characters.
**Date/Time**: 2026-02-21 15:54 (NPT)

### Step 7: Case Mapping Reversal
*   **Problem**: Transliterating "aNitaa" incorrectly produced the Devanagari string with dental characters, and "anitaa" produced retroflex characters. The mapping for capitals and lowercases was historically reversed.
*   **Action**: Swapped mapping in `data_gen.py`. Now lowercase characters map to dentals (e.g., `t` -> `त`) and uppercase map to retroflexes (e.g., `T` -> `ट`).
*   **Verification**: Executed tests with horizontal and vertical text rendering. Updated `test_translit_logic.py` expected output array and encoded stdout output encoding for Windows compatibility.

---

## 7. Iteration 4: Halant Training & Hyperparameter Tuning
**Goal**: Expand model capability to recognize combining characters and improve accuracy over the augmented dataset.
**Date/Time**: 2026-02-21 16:03 (NPT)

### Step 8: Dataset Expansion for Combining Marks
*   **Problem**: The `halant` (`्`) is a zero-width combining character that didn’t generate visual features correctly and caused Windows file-system `OSError` due to its transliteration label using an asterisk (`*`).
*   **Action**: Padded the character with a standard dotted circle (U+25CC) so the crop bounded box could capture visual features. Re-mapped the folder name to `halant` to prevent OS-level path parsing failures.
*   **Result**: Generated 100 variations of the `halant` class, bringing the total dataset to 4,444 samples across 44 classes.

### Step 9: Model Optimization 
*   **Problem**: Model was using basic default parameters (`n_estimators=100`) despite the 5x expansion of the augmented dataset.
*   **Action**: Optimized `RandomForestClassifier` in `train.py` by increasing trees (`n_estimators=200`), capping depth (`max_depth=25`), and enforcing min split sizes (`min_samples_split=4`) to prevent overfitting on the synthetic noise.
*   **Result**: Test-set accuracy jumped from ~45% up to **55%**, and the test script correctly predicts raw `halant` images with **89% confidence**.

---

## 8. Iteration 5: Numbers and Punctuation Support
**Goal**: Integrate Devanagari numerals (०-९) and standard punctuation into the dataset and Monogram UI.
**Date/Time**: 2026-02-21 16:09 (NPT)

### Step 10: Mapping OS-Safe Directories
*   **Problem**: Adding characters like `?`, `.`, or `,` directly as labels crashes the Windows filesystem when generating the 100 augmented images per class.
*   **Action**: Included a `NUMBERS` and `SYMBOLS` transliteration map across `data_gen.py`, `api.py`, and `index.html`. Added a mapping system in the generator to safely rename invalid path characters (e.g. `?` becomes `question`, `.` becomes `danda`).
*   **Result**: Random Forest retrained successfully on **60 classes** (6,060 samples total), netting **62% test set accuracy**. Script correctly verifies inference tests against numerals like `४` and parsed characters like `question`.

---

## 9. Current Status & Definition of Done (DoD)
- [x] Case sensitivity folder conflict resolved.
- [x] Dataset expanded 5x with robust augmentations.
- [x] Model retrained and weights updated.
- [x] Half-letter (Virama) support fully integrated in Monogram Generator.
- [x] Grapheme clusters respected in UI and Backend.
- [x] Transliteration case mapping fixed across dentals and retroflexes (e.g., proper representation of aNitaa vs anitaa).
- [x] Combining characters (halant) are now fully renderable and have been added to the model classes.
- [x] Model hyperparameters optimized to handle diverse augmented datasets.
- [x] Devanagari numbers (0-9) and standard punctuation (?, ., -, etc.) added to the dataset and model. 

**Future Iterations**:
*   Train Convolutional Neural Network (CNN) architecture if higher accuracy is heavily prioritized over traditional machine learning approaches.
